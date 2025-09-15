import crypto from 'crypto';

export const config = {
  api: { bodyParser: false }
};

function readStream(req, limit = 1024 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > limit) {
        reject(Object.assign(new Error('Payload too large'), { statusCode: 413 }));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function tsecEq(a, b) {
  try {
    const A = Buffer.from(a);
    const B = Buffer.from(b);
    return A.length === B.length && require('crypto').timingSafeEqual(A, B);
  } catch {
    return false;
  }
}

export default async function handler(req, res) {
  const VERIFY_TOKEN = process.env.VERIFY_TOKEN;
  const APP_SECRET = process.env.META_APP_SECRET;

  if (req.method === 'GET' && req.url === '/') {
    res.status(200).json({ status: 'healthy', ts: new Date().toISOString() });
    return;
  }

  if (req.method === 'GET') {
    const mode = req.query?.['hub.mode'];
    const token = req.query?.['hub.verify_token'];
    const challenge = req.query?.['hub.challenge'];

    if (mode === 'subscribe' && token && VERIFY_TOKEN && token === VERIFY_TOKEN && challenge) {
      res.status(200).send(challenge);
      return;
    }
    res.status(403).json({ error: 'Verification failed' });
    return;
  }

  if (req.method === 'POST') {
    try {
      if (!APP_SECRET) {
        res.status(500).json({ error: 'Server misconfigured: missing META_APP_SECRET' });
        return;
      }

      const signature = req.headers['x-hub-signature-256'];
      if (!signature || !signature.startsWith('sha256=')) {
        res.status(401).json({ error: 'Missing || invalid signature header' });
        return;
      }

      const raw = await readStream(req);
      const expected = 'sha256=' + require('crypto').createHmac('sha256', APP_SECRET).update(raw).digest('hex');

      if (!tsecEq(expected, signature)) {
        res.status(401).json({ error: 'Signature verification failed' });
        return;
      }

      let body;
      try { body = JSON.parse(raw.toString('utf8')); }
      catch { res.status(400).json({ error: 'Invalid JSON' }); return; }

      res.status(200).json({ ok: true });

      try {
        const entries = Array.isArray(body?.entry) ? body.entry : [];
        for (const entry of entries) {
          const changes = Array.isArray(entry?.changes) ? entry.changes : [];
          for (const ch of changes) {
            if (ch.field === 'messages') {
              const msgs = Array.isArray(ch?.value?.messages) ? ch.value.messages : [];
              for (const m of msgs) {
                console.log('[message]', {
                  from_hash: require('crypto').createHash('sha256').update(String(m.from || '')).digest('hex').slice(0, 12),
                  type: m.type,
                  ts: m.timestamp
                });
              }
            }
          }
        }
      } catch (e) {
        console.error('post-ack processing error', e?.message || e);
      }
      return;
    } catch (e) {
      res.status(e.statusCode || 500).json({ error: e.message || 'Internal error' });
      return;
  }

  res.setHeader('Allow', 'GET, POST');
  res.status(405).end('Method Not Allowed');
}