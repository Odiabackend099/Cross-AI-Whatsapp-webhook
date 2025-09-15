
# CrossAI WhatsApp Webhook (Vercel + Express dev)

A production-grade WhatsApp Cloud API webhook that verifies the GET challenge and validates HMAC signatures on POST using META_APP_SECRET.

## Local
```
cp .env.example .env
# fill VERIFY_TOKEN and META_APP_SECRET
npm install
npm run dev
```

Tests:
```
node scripts/verify-get.js
node scripts/hmac-post.js
```

## Vercel
- Set env: VERIFY_TOKEN, META_APP_SECRET
- Webhook URL: https://<project>.vercel.app/api/webhooks/whatsapp/crossai
- Regions: fra1, iad1
