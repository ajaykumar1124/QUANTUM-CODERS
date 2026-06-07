const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const PUBLIC_DIR = path.join(ROOT, 'public');
const INDEX_FILE = path.join(PUBLIC_DIR, 'index.html');
const PORT = Number(process.env.PORT || 3000);

const USERS = {
  admin: { password: 'tngst2026', role: 'Administrator' },
  ajay: { password: 'ajay@123', role: 'Analyst' },
  parasuraman: { password: 'para@123', role: 'Analyst' },
  jayakumar: { password: 'jaya@123', role: 'Auditor' },
  balaraman: { password: 'bala@123', role: 'Auditor' },
  praveen: { password: 'praveen@123', role: 'Analyst' },
  quantum: { password: 'quantum@svcet', role: 'Team' },
  auditor: { password: 'audit2026', role: 'Auditor' },
  demo: { password: 'demo123', role: 'Demo User' }
};

const sessions = new Map();

function toDisplayUser(username, user) {
  return {
    username,
    name: username.charAt(0).toUpperCase() + username.slice(1),
    role: `${user.role} - Audit Division`
  };
}

function extractArraySource(html, name) {
  const start = html.indexOf(`const ${name}=[`);
  if (start === -1) throw new Error(`Could not find ${name} data in frontend.`);
  const arrayStart = html.indexOf('[', start);
  const marker = '];';
  const end = html.indexOf(marker, arrayStart);
  if (end === -1) throw new Error(`Could not parse ${name} data in frontend.`);
  return html.slice(arrayStart, end + 1);
}

function loadPrototypeData() {
  const html = fs.readFileSync(INDEX_FILE, 'utf8');
  const dealers = Function(`"use strict"; return (${extractArraySource(html, 'prototypeDealers')});`)();
  const explanations = Function(`"use strict"; return (${extractArraySource(html, 'prototypeExplains')});`)();
  return { dealers, explanations };
}

let data = loadPrototypeData();

function send(res, status, body, headers = {}) {
  const payload = typeof body === 'string' ? body : JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': typeof body === 'string' ? 'text/plain; charset=utf-8' : 'application/json; charset=utf-8',
    ...headers
  });
  res.end(payload);
}

function sendJson(res, status, body) {
  send(res, status, body, { 'Content-Type': 'application/json; charset=utf-8' });
}

function notFound(res) {
  sendJson(res, 404, { error: 'Not found' });
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 1_000_000) {
        req.destroy();
        reject(new Error('Request body too large'));
      }
    });
    req.on('end', () => {
      if (!body) return resolve({});
      try {
        resolve(JSON.parse(body));
      } catch {
        reject(new Error('Invalid JSON'));
      }
    });
  });
}

function getSession(req) {
  const header = req.headers.authorization || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : '';
  return token ? sessions.get(token) : null;
}

function requireSession(req, res) {
  const session = getSession(req);
  if (!session) {
    sendJson(res, 401, { error: 'Unauthorized' });
    return null;
  }
  return session;
}

function csvEscape(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`;
}

function dealersToCsv(rows) {
  const headers = ['Rank', 'GSTIN', 'Business Name', 'Sector', 'District', 'Declared Turnover', 'Est. Actual', 'Anomaly Score', 'Risk Level', 'Top Signal'];
  const lines = rows.map((d, index) => [
    index + 1,
    d.gstin,
    d.name,
    d.sector,
    d.district,
    d.declared,
    d.actual,
    d.score,
    d.risk,
    d.signal
  ].map(csvEscape).join(','));
  return [headers.map(csvEscape).join(','), ...lines].join('\n');
}

function getMetrics() {
  const totalDealers = data.dealers.length;
  const critical = data.dealers.filter(d => d.risk === 'Critical').length;
  const high = data.dealers.filter(d => d.risk === 'High').length;
  const medium = data.dealers.filter(d => d.risk === 'Medium').length;
  const avgScore = totalDealers
    ? data.dealers.reduce((sum, dealer) => sum + dealer.score, 0) / totalDealers
    : 0;
  const sectors = [...new Set(data.dealers.map(d => d.sector))].sort();
  const districts = [...new Set(data.dealers.map(d => d.district))].sort();
  return { totalDealers, critical, high, medium, avgScore, sectors, districts };
}

function buildAuditBrief(dealer) {
  const riskAction = dealer.risk === 'Critical'
    ? 'Open an immediate field audit within 7 days and preserve e-way, EPFO, and TANGEDCO evidence.'
    : dealer.risk === 'High'
      ? 'Queue a priority desk review within 30 days and request supporting ledgers.'
      : 'Keep the dealer under watchlist review and validate the next return cycle.';

  return `${dealer.name} in ${dealer.district} is flagged at ${Math.round(dealer.score * 100)}% anomaly confidence because ${dealer.signal} is inconsistent with the declared turnover of ${dealer.declared}. Cross-database indicators suggest operating scale closer to ${dealer.actual}, creating potential GST revenue exposure for Tamil Nadu. The strongest signal pattern points to ${dealer.sector} sector under-reporting risk, especially where workforce, power use, logistics, or water consumption exceed the declared business scale. ${riskAction}`;
}

async function handleApi(req, res, url) {
  if (req.method === 'POST' && url.pathname === '/api/login') {
    const body = await parseBody(req);
    const username = String(body.username || '').trim().toLowerCase();
    const password = String(body.password || '');
    const user = USERS[username];

    if (!user || user.password !== password) {
      return sendJson(res, 401, { error: 'Invalid credentials' });
    }

    const token = crypto.randomBytes(24).toString('hex');
    const session = { ...toDisplayUser(username, user), createdAt: new Date().toISOString() };
    sessions.set(token, session);
    return sendJson(res, 200, { token, user: session });
  }

  if (req.method === 'POST' && url.pathname === '/api/logout') {
    const header = req.headers.authorization || '';
    const token = header.startsWith('Bearer ') ? header.slice(7) : '';
    if (token) sessions.delete(token);
    return sendJson(res, 200, { ok: true });
  }

  if (req.method === 'GET' && url.pathname === '/api/health') {
    return sendJson(res, 200, { ok: true, app: 'TN-GRAD', time: new Date().toISOString() });
  }

  if (!requireSession(req, res)) return;

  if (req.method === 'GET' && url.pathname === '/api/dealers') {
    const sector = url.searchParams.get('sector');
    const risk = url.searchParams.get('risk');
    const district = url.searchParams.get('district');
    const q = (url.searchParams.get('q') || '').toLowerCase();
    const rows = data.dealers.filter(d => {
      return (!sector || d.sector === sector)
        && (!risk || d.risk === risk)
        && (!district || d.district === district)
        && (!q || `${d.gstin} ${d.name} ${d.sector} ${d.district}`.toLowerCase().includes(q));
    });
    return sendJson(res, 200, rows);
  }

  if (req.method === 'GET' && url.pathname === '/api/explanations') {
    return sendJson(res, 200, data.explanations);
  }

  if (req.method === 'GET' && url.pathname === '/api/metrics') {
    return sendJson(res, 200, getMetrics());
  }

  if (req.method === 'POST' && url.pathname === '/api/audit-brief') {
    const body = await parseBody(req);
    const query = String(body.gstin || body.query || '').toLowerCase();
    const dealer = data.dealers.find(d => d.gstin.toLowerCase() === query || d.name.toLowerCase().includes(query));
    if (!dealer) return sendJson(res, 404, { error: 'Dealer not found' });
    return sendJson(res, 200, { dealer, brief: buildAuditBrief(dealer) });
  }

  if (req.method === 'GET' && url.pathname === '/api/export/dealers.csv') {
    const csv = dealersToCsv(data.dealers);
    res.writeHead(200, {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="tn-grad-dealers.csv"'
    });
    return res.end(csv);
  }

  const dealerCsvMatch = url.pathname.match(/^\/api\/export\/dealer\/([^/]+)\.csv$/);
  if (req.method === 'GET' && dealerCsvMatch) {
    const gstin = decodeURIComponent(dealerCsvMatch[1]);
    const dealer = data.dealers.find(d => d.gstin === gstin);
    if (!dealer) return sendJson(res, 404, { error: 'Dealer not found' });
    const csv = dealersToCsv([dealer]);
    res.writeHead(200, {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="${dealer.gstin}.csv"`
    });
    return res.end(csv);
  }

  return notFound(res);
}

function serveStatic(req, res, url) {
  const pathname = url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname);
  const requested = path.normalize(path.join(PUBLIC_DIR, pathname));
  if (!requested.startsWith(PUBLIC_DIR)) return notFound(res);

  fs.readFile(requested, (err, file) => {
    if (err) return notFound(res);
    const ext = path.extname(requested).toLowerCase();
    const types = {
      '.html': 'text/html; charset=utf-8',
      '.css': 'text/css; charset=utf-8',
      '.js': 'text/javascript; charset=utf-8',
      '.json': 'application/json; charset=utf-8',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.svg': 'image/svg+xml'
    };
    res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
    res.end(file);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  try {
    if (url.pathname.startsWith('/api/')) {
      await handleApi(req, res, url);
    } else {
      serveStatic(req, res, url);
    }
  } catch (error) {
    sendJson(res, 500, { error: error.message || 'Internal server error' });
  }
});

server.listen(PORT, () => {
  console.log(`TN-GRAD full-stack app running at http://localhost:${PORT}`);
});
