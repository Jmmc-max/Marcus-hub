import { createPublicKey, verify } from 'node:crypto';

const ED25519_SPKI_PREFIX = '302a300506032b6570032100';

export function verifyDiscordRequest({ publicKey, signature, timestamp, body }) {
  if (!publicKey || !signature || !timestamp) {
    return false;
  }

  const key = createPublicKey({
    key: Buffer.from(`${ED25519_SPKI_PREFIX}${publicKey}`, 'hex'),
    format: 'der',
    type: 'spki'
  });

  return verify(
    null,
    Buffer.concat([Buffer.from(timestamp), body]),
    key,
    Buffer.from(signature, 'hex')
  );
}

export function jsonResponse(response, statusCode, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body)
  });
  response.end(body);
}

export async function editInteractionResponse({ applicationId, interactionToken, payload }) {
  const response = await fetch(`https://discord.com/api/v10/webhooks/${applicationId}/${interactionToken}/messages/@original`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Discord response edit failed (${response.status}): ${(await response.text()).slice(0, 200)}`);
  }
}

export async function sendWebhook({ webhookUrl, payload }) {
  if (!webhookUrl) {
    return;
  }

  const response = await fetch(webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Webhook send failed (${response.status}): ${(await response.text()).slice(0, 200)}`);
  }
}
