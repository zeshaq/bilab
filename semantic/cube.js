// Cube configuration for bilab's semantic layer.

// Phase 3 (governance): every query runs AS THE PERSON who asked. The backend
// has verified the caller's Keycloak token and passes the identity in headers
// (X-User, X-User-Groups, X-User-Token). Each query gets its own Trino
// connection carrying that token, so the lab's OPA masking and row filters
// apply to every metric exactly as in the person's own SQL client — the single
// security context for humans and agents (ADR-0007). The cache is kept per
// person, so one person's result is never served to another.

const fs = require('fs');
const crypto = require('crypto');

const ca = fs.readFileSync('/certs/trino.crt');

module.exports = {
  checkAuth: (req) => {
    const user = req.headers['x-user'];
    const token = req.headers['x-user-token'];
    if (!user || !token) {
      throw new Error('Not signed in: the semantic layer is reached through the backend with a Keycloak token');
    }
    req.securityContext = {
      user,
      token,
      groups: (req.headers['x-user-groups'] || '').split(',').filter(Boolean),
    };
  },
  contextToAppId: ({ securityContext }) => `BILAB_${securityContext.user}`,
  contextToOrchestratorId: ({ securityContext }) =>
    `BILAB_${securityContext.user}_${crypto.createHash('sha256').update(securityContext.token).digest('hex').slice(0, 16)}`,
  driverFactory: ({ securityContext }) => ({
    type: 'trino',
    host: 'trino',
    port: 8443,
    ssl: { ca },
    catalog: 'lakehouse',
    schema: 'curated',
    user: securityContext.user,
    custom_auth: `Bearer ${securityContext.token}`,
    headers: { 'X-Trino-User': securityContext.user, 'X-Trino-Source': 'bilab' },
  }),
  scheduledRefreshTimer: false,
  telemetry: false,
};
