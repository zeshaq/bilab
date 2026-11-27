// Cube configuration for bilab's semantic layer (Phase 1).

// Phase 1: a single service identity (Keycloak client svc-dataops) for every
// query, so all queries hit Trino with one governed identity and OPA's masking /
// row filters apply to the metric the same way they would in that identity's own
// SQL client. Per-user token passthrough (each request carries the caller's
// Keycloak token) is Phase 3 (governance) — see docs/roadmap.md.
//
// The svc-dataops access token is short-lived, so a fresh one is fetched (and
// cached) when the current one is within 30s of expiry. The secret is read from
// the container environment, never from argv or config.

const fs = require('fs');
const { execSync } = require('child_process');

const ca = fs.readFileSync('/certs/trino.crt');

let cache = { token: null, expiresAt: 0 };

function principal(token) {
  try {
    const p = token.split('.')[1];
    return JSON.parse(Buffer.from(p, 'base64').toString('utf8')).preferred_username;
  } catch {
    return 'svc-dataops';
  }
}

function svcToken() {
  if (cache.token && Date.now() < cache.expiresAt - 30000) {
    return cache.token;
  }
  const raw = execSync('node /cube/conf/token.js', { encoding: 'utf8' });
  const j = JSON.parse(raw);
  cache = { token: j.access_token, expiresAt: Date.now() + j.expires_in * 1000 };
  return cache.token;
}

module.exports = {
  driverFactory: () => {
    const token = svcToken();
    const user = principal(token);
    return {
      type: 'trino',
      host: 'trino',
      port: 8443,
      ssl: { ca },
      catalog: 'lakehouse',
      schema: 'curated',
      user,
      custom_auth: `Bearer ${token}`,
      headers: { 'X-Trino-User': user, 'X-Trino-Source': 'bilab' },
    };
  },
  scheduledRefreshTimer: false,
  telemetry: false,
};
