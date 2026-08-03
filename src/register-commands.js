import { loadEnv } from './env.js';

loadEnv();

const { CLIENT_ID, DISCORD_TOKEN, GUILD_ID } = process.env;

if (!CLIENT_ID || !DISCORD_TOKEN) {
  throw new Error('Missing CLIENT_ID or DISCORD_TOKEN in environment.');
}

const commands = [
  {
    name: 'roblox-check',
    description: 'Check a public Roblox user by profile link, user ID, or username.',
    type: 1,
    options: [
      {
        name: 'target',
        description: 'Roblox profile URL, numeric user ID, or username',
        type: 3,
        required: true
      }
    ]
  },
  {
    name: 'roblox-check-file',
    description: 'Import a text file and check public Roblox profiles, one target per line.',
    type: 1,
    options: [
      {
        name: 'file',
        description: 'Plain text file with Roblox profile URLs, user IDs, or usernames',
        type: 11,
        required: true
      }
    ]
  }
];

const route = GUILD_ID
  ? `https://discord.com/api/v10/applications/${CLIENT_ID}/guilds/${GUILD_ID}/commands`
  : `https://discord.com/api/v10/applications/${CLIENT_ID}/commands`;

const response = await fetch(route, {
  method: 'PUT',
  headers: {
    Authorization: `Bot ${DISCORD_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(commands)
});

if (!response.ok) {
  throw new Error(`Command registration failed (${response.status}): ${(await response.text()).slice(0, 500)}`);
}

console.log(`Registered ${commands.length} command(s) ${GUILD_ID ? `for guild ${GUILD_ID}` : 'globally'}.`);
