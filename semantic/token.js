// Fetch a fresh svc-dataops client_credentials token from Keycloak and print
// the raw token JSON to stdout. Reads the client secret from the environment
// (DATAOPS_OIDC_CLIENT_SECRET), never from argv. Called synchronously by
// cube.js via execSync.
const http = require('http');
const qs = require('querystring');

const body = qs.stringify({
  grant_type: 'client_credentials',
  client_id: 'svc-dataops',
  client_secret: process.env.DATAOPS_OIDC_CLIENT_SECRET,
});

const req = http.request(
  {
    host: 'keycloak',
    port: 8080,
    path: '/realms/datalab/protocol/openid-connect/token',
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(body),
    },
  },
  (res) => {
    let data = '';
    res.on('data', (c) => (data += c));
    res.on('end', () => process.stdout.write(data));
  }
);
req.on('error', (e) => {
  console.error(e.message);
  process.exit(1);
});
req.end(body);
