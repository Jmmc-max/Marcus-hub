import { createServer } from 'node:http';
import { loadEnv } from './env.js';
import { editInteractionResponse, jsonResponse, sendWebhook, verifyDiscordRequest } from './discord.js';
import { checkRobloxUser, checkRobloxUsers } from './roblox.js';

loadEnv();

const {
  CLIENT_ID,
  DISCORD_PUBLIC_KEY,
  PORT = 3000,
  WEBHOOK_URL,
  PUBLIC_BASE_URL,
  INTERACTIONS_ENDPOINT_URL
} = process.env;

const MAX_IMPORT_BYTES = 512_000;


function getInteractionsEndpointUrl() {
  if (INTERACTIONS_ENDPOINT_URL) {
    return INTERACTIONS_ENDPOINT_URL;
  }

  if (PUBLIC_BASE_URL) {
    return `${PUBLIC_BASE_URL.replace(/\/$/, '')}/interactions`;
  }

  const endpointPortHint = Number(PORT) === 443 ? '' : `:${PORT}`;
  return `https://YOUR_HOST${endpointPortHint}/interactions`;
}

function buildBatchSummaryEmbed(results) {
  const opened = results.filter(item => item.ok).length;
  const failed = results.length - opened;
  const lines = results.map(item => {
    if (item.ok) {
      return `✅ ${item.target} -> ${item.result.profileUrl}`;
    }

    return `❌ ${item.target} -> ${item.error}`;
  });

  return {
    color: failed ? 0xffcc4d : 0x57f287,
    title: 'Roblox Import Check Results',
    description: lines.join('\n').slice(0, 4096),
    fields: [
      { name: 'Can open', value: String(opened), inline: true },
      { name: 'Cannot open', value: String(failed), inline: true }
    ],
    timestamp: new Date().toISOString()
  };
}

function buildResultEmbed(result) {
  const embed = {
    color: result.isBanned ? 0xff5555 : 0x57f287,
    title: `${result.displayName} (@${result.name})`,
    url: result.profileUrl,
    description: result.description.slice(0, 4096),
    fields: [
      { name: 'User ID', value: String(result.id), inline: true },
      { name: 'Banned', value: result.isBanned ? 'Yes' : 'No', inline: true },
      { name: 'Created', value: `<t:${Math.floor(new Date(result.created).getTime() / 1000)}:F>`, inline: false },
      { name: 'Profile', value: result.profileUrl, inline: false }
    ],
    timestamp: new Date().toISOString()
  };

  if (result.avatarUrl) {
    embed.thumbnail = { url: result.avatarUrl };
  }

  return embed;
}

function getOption(interaction, name) {
  return interaction.data?.options?.find(option => option.name === name);
}

async function readImportAttachment(attachment) {
  if (attachment.size > MAX_IMPORT_BYTES) {
    throw new Error(`Import file is too large. Maximum size is ${MAX_IMPORT_BYTES} bytes.`);
  }

  const response = await fetch(attachment.url);
  if (!response.ok) {
    throw new Error(`Could not download import file (${response.status}).`);
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType && !contentType.includes('text/') && !contentType.includes('octet-stream')) {
    throw new Error('Import file must be a plain text file with one target per line.');
  }

  return response.text();
}

async function handleRobloxCheck(interaction) {
  const target = getOption(interaction, 'target')?.value;
  if (!target) {
    throw new Error('Missing target option.');
  }

  const result = await checkRobloxUser(target);
  const embed = buildResultEmbed(result);
  const payload = { embeds: [embed] };

  await sendWebhook({
    webhookUrl: WEBHOOK_URL,
    payload: {
      username: 'Roblox Checker',
      embeds: [embed],
      content: `Checked Roblox profile: ${result.profileUrl}`
    }
  });

  return payload;
}

async function handleRobloxCheckFile(interaction) {
  const attachmentId = getOption(interaction, 'file')?.value;
  const attachment = interaction.data?.resolved?.attachments?.[attachmentId];
  if (!attachment) {
    throw new Error('Missing import file attachment.');
  }

  const text = await readImportAttachment(attachment);
  const results = await checkRobloxUsers(text.split(/\r?\n/));
  const embed = buildBatchSummaryEmbed(results);
  const payload = { embeds: [embed] };

  await sendWebhook({
    webhookUrl: WEBHOOK_URL,
    payload: {
      username: 'Roblox Checker',
      embeds: [embed],
      content: `Checked ${results.length} imported Roblox target(s).`
    }
  });

  return payload;
}

async function processInteraction(interaction) {
  if (interaction.data?.name === 'roblox-check') {
    return handleRobloxCheck(interaction);
  }

  if (interaction.data?.name === 'roblox-check-file') {
    return handleRobloxCheckFile(interaction);
  }

  return { content: 'Unknown command.' };
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }

  return Buffer.concat(chunks);
}

const server = createServer(async (request, response) => {
  if (request.method === 'GET' && request.url === '/') {
    jsonResponse(response, 200, { ok: true, name: 'Roblox Checker Bot' });
    return;
  }

  if (request.method !== 'POST' || request.url !== '/interactions') {
    jsonResponse(response, 404, { error: 'Not found' });
    return;
  }

  const body = await readBody(request);
  const signature = request.headers['x-signature-ed25519'];
  const timestamp = request.headers['x-signature-timestamp'];

  if (!DISCORD_PUBLIC_KEY) {
    jsonResponse(response, 500, { error: 'Missing DISCORD_PUBLIC_KEY.' });
    return;
  }

  if (!verifyDiscordRequest({ publicKey: DISCORD_PUBLIC_KEY, signature, timestamp, body })) {
    jsonResponse(response, 401, { error: 'Invalid request signature.' });
    return;
  }

  const interaction = JSON.parse(body.toString('utf8'));
  if (interaction.type === 1) {
    jsonResponse(response, 200, { type: 1 });
    return;
  }

  jsonResponse(response, 200, { type: 5 });

  try {
    const payload = await processInteraction(interaction);
    await editInteractionResponse({
      applicationId: CLIENT_ID ?? interaction.application_id,
      interactionToken: interaction.token,
      payload
    });
  } catch (error) {
    await editInteractionResponse({
      applicationId: CLIENT_ID ?? interaction.application_id,
      interactionToken: interaction.token,
      payload: { content: `Could not check Roblox target: ${error.message}` }
    });
  }
});

server.listen(Number(PORT), () => {
  console.log(`Roblox Checker interaction server listening on port ${PORT}`);
  console.log(`Set your Discord Interactions Endpoint URL to: ${getInteractionsEndpointUrl()}`);
  if (!DISCORD_PUBLIC_KEY) {
    console.warn('DISCORD_PUBLIC_KEY is not set. Discord requests cannot be verified until you add it.');
  }
});
