import express from 'express';
import dotenv from 'dotenv';
import crypto from 'crypto';
import getRawBody from 'raw-body';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ ok: true, ts: new Date().toISOString() });
});

app.get('/api/webhooks/whatsapp/crossai', (req, res) => {
  const VERIFY_TOKEN = process.env.VERIFY_TOKEN;
  const { ['hub.mode']: mode, ['hub.verify_token']: token, ['hub.challenge']: challenge } = req.query;
  if (mode === 'subscribe' && token === VERIFY_TOKEN && challenge) {
    return res.status(200).send(challenge);
  }
  return res.status(403).json({ error: 'Verification failed' });
});

app.post('/api/webhooks/whatsapp/crossai', async (req, res) => {
  try {
    const secret = process.env.META_APP_SECRET;
    const header = req.header('X-Hub-Signature-256');
    if (!secret || !header || !header.startsWith('sha256=')) {
      return res.status(401).json({ error: 'Missing signature or secret' });
    }
    const raw = await getRawBody(req, { limit: '1mb' });
    const expected = 'sha256=' + crypto.createHmac('sha256', secret).update(raw).digest('hex');
    const ok = Buffer.from(expected).length === Buffer.from(header).length &&
               crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(header));
    if (!ok) return res.status(401).json({ error: 'Bad signature' });

    res.status(200).json({ ok: true });

    try {
      const payload = JSON.parse(raw.toString('utf8'));
      console.log('[dev] received', JSON.stringify({
        object: payload.object,
        entries: (payload.entry || []).length
      }));
    } catch (e) {
      console.error('parse error', e.message);
    }
  } catch (e) {
    console.error('server error', e);
    res.status(500).json({ error: 'Internal error' });
  }
});

app.listen(PORT, () => {
  console.log(`Dev webhook listening on http://localhost:${PORT}`);
});