
# WhatsApp Cloud API Playbook
- Create System User, assign permissions, get permanent token.
- Store META_APP_SECRET securely.
- Deploy this webhook to Vercel and set VERIFY_TOKEN & META_APP_SECRET.
- In Meta App → Webhooks, set Callback URL to /api/webhooks/whatsapp/crossai and verify with VERIFY_TOKEN.
- Subscribe to WhatsApp objects (messages, message_template_status_update, account_update).
- In your worker, dedupe by message id (wamid), and handle timeouts/retries.
