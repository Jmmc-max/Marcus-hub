const ROBLOX_USER_LINK_PATTERN = /^https?:\/\/(?:www\.)?roblox\.com\/users\/(\d+)(?:\/profile)?(?:[/?#].*)?$/i;
const ROBLOX_USERNAME_PATTERN = /^[A-Za-z0-9_]{3,20}$/;
const MAX_BATCH_SIZE = 750;
const BATCH_CONCURRENCY = 10;

export function parseRobloxInput(input) {
  const trimmed = input.trim();
  const linkMatch = trimmed.match(ROBLOX_USER_LINK_PATTERN);

  if (linkMatch) {
    return { type: 'id', value: Number(linkMatch[1]) };
  }

  if (/^\d+$/.test(trimmed)) {
    return { type: 'id', value: Number(trimmed) };
  }

  if (ROBLOX_USERNAME_PATTERN.test(trimmed)) {
    return { type: 'username', value: trimmed };
  }

  throw new Error('Provide a Roblox profile link, numeric user ID, or username (3-20 letters, numbers, and underscores).');
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Roblox API request failed (${response.status}): ${text.slice(0, 200)}`);
  }

  return response.json();
}

async function resolveUserId(parsedInput) {
  if (parsedInput.type === 'id') {
    return parsedInput.value;
  }

  const data = await fetchJson('https://users.roblox.com/v1/usernames/users', {
    method: 'POST',
    body: JSON.stringify({ usernames: [parsedInput.value], excludeBannedUsers: false })
  });

  const user = data.data?.[0];
  if (!user) {
    throw new Error(`No Roblox user found for username "${parsedInput.value}".`);
  }

  return user.id;
}

export async function checkRobloxUser(input) {
  const parsedInput = parseRobloxInput(input);
  const userId = await resolveUserId(parsedInput);

  const [profile, avatar] = await Promise.all([
    fetchJson(`https://users.roblox.com/v1/users/${userId}`),
    fetchJson(`https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=${userId}&size=150x150&format=Png&isCircular=false`)
  ]);

  return {
    id: profile.id,
    name: profile.name,
    displayName: profile.displayName,
    description: profile.description || 'No description set.',
    created: profile.created,
    isBanned: Boolean(profile.isBanned),
    profileUrl: `https://www.roblox.com/users/${profile.id}/profile`,
    avatarUrl: avatar.data?.[0]?.imageUrl ?? null
  };
}


export async function checkRobloxUsers(inputs) {
  const targets = inputs
    .map(input => input.trim())
    .filter(input => input && !input.startsWith('#'));

  if (targets.length === 0) {
    throw new Error('The imported file did not contain any Roblox profile links, user IDs, or usernames.');
  }

  if (targets.length > MAX_BATCH_SIZE) {
    throw new Error(`Import files can contain at most ${MAX_BATCH_SIZE} targets per check.`);
  }

  const results = [];
  for (let index = 0; index < targets.length; index += BATCH_CONCURRENCY) {
    const chunk = targets.slice(index, index + BATCH_CONCURRENCY);
    const chunkResults = await Promise.all(chunk.map(async target => {
      try {
        const result = await checkRobloxUser(target);
        return { target, ok: true, result };
      } catch (error) {
        return { target, ok: false, error: error.message };
      }
    }));

    results.push(...chunkResults);
  }

  return results;
}
