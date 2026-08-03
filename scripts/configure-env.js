import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const ENV_PATH = resolve('.env');
const ALLOWED_KEYS = new Set(['DISCORD_TOKEN', 'CLIENT_ID', 'DISCORD_PUBLIC_KEY', 'GUILD_ID', 'WEBHOOK_URL', 'PORT']);
const args = process.argv.slice(2);

function printHelp() {
  console.log(`Usage:
  npm run configure -- --client-id YOUR_APPLICATION_ID --token YOUR_BOT_TOKEN

Options:
  --token, --discord-token     Discord bot token/key
  --client-id                  Discord application/client ID
  --public-key                 Discord application public key for request verification
  --guild-id                   Optional Discord server ID for faster command registration
  --webhook-url                Optional Discord webhook URL for logs
  --port                       Optional HTTP server port, defaults to 3000

Examples:
  npm run configure -- --client-id 153361584328 --public-key YOUR_PUBLIC_KEY --token YOUR_BOT_TOKEN
  npm run configure -- --guild-id YOUR_SERVER_ID
`);
}

function parseArgs(values) {
  const parsed = {};

  for (let index = 0; index < values.length; index += 1) {
    const arg = values[index];
    const next = values[index + 1];

    if (arg === '--help' || arg === '-h') {
      parsed.help = true;
      continue;
    }

    if (!arg.startsWith('--')) {
      continue;
    }

    const key = arg.slice(2);
    if (!next || next.startsWith('--')) {
      throw new Error(`${arg} needs a value.`);
    }

    parsed[key] = next;
    index += 1;
  }

  return parsed;
}

function readExistingEnv() {
  if (!existsSync(ENV_PATH)) {
    return new Map();
  }

  const env = new Map();
  for (const line of readFileSync(ENV_PATH, 'utf8').split(/\r?\n/)) {
    if (!line || line.trim().startsWith('#') || !line.includes('=')) {
      continue;
    }

    const [key, ...valueParts] = line.split('=');
    if (ALLOWED_KEYS.has(key)) {
      env.set(key, valueParts.join('='));
    }
  }

  return env;
}

function maskSecret(value) {
  if (!value) {
    return '(not set)';
  }

  if (value.length <= 8) {
    return '********';
  }

  return `${value.slice(0, 4)}...${value.slice(-4)}`;
}

const parsed = parseArgs(args);
if (parsed.help || args.length === 0) {
  printHelp();
  process.exit(0);
}

const env = readExistingEnv();
const updates = {
  DISCORD_TOKEN: parsed.token ?? parsed['discord-token'],
  CLIENT_ID: parsed['client-id'],
  DISCORD_PUBLIC_KEY: parsed['public-key'],
  GUILD_ID: parsed['guild-id'],
  WEBHOOK_URL: parsed['webhook-url'],
  PORT: parsed.port
};

for (const [key, value] of Object.entries(updates)) {
  if (value) {
    env.set(key, value);
  }
}

const output = [
  '# Created by npm run configure. Do not commit this file.',
  `DISCORD_TOKEN=${env.get('DISCORD_TOKEN') ?? ''}`,
  `CLIENT_ID=${env.get('CLIENT_ID') ?? ''}`,
  `DISCORD_PUBLIC_KEY=${env.get('DISCORD_PUBLIC_KEY') ?? ''}`,
  `GUILD_ID=${env.get('GUILD_ID') ?? ''}`,
  `WEBHOOK_URL=${env.get('WEBHOOK_URL') ?? ''}`,
  `PORT=${env.get('PORT') ?? 3000}`,
  ''
].join('\n');

writeFileSync(ENV_PATH, output);

console.log('Saved configuration to .env');
console.log(`DISCORD_TOKEN=${maskSecret(env.get('DISCORD_TOKEN'))}`);
console.log(`CLIENT_ID=${env.get('CLIENT_ID') ?? '(not set)'}`);
console.log(`DISCORD_PUBLIC_KEY=${maskSecret(env.get('DISCORD_PUBLIC_KEY'))}`);
console.log(`GUILD_ID=${env.get('GUILD_ID') ?? '(not set)'}`);
console.log(`WEBHOOK_URL=${maskSecret(env.get('WEBHOOK_URL'))}`);
console.log(`PORT=${env.get('PORT') ?? 3000}`);
console.log('\nNext run: npm run setup-and-start');
