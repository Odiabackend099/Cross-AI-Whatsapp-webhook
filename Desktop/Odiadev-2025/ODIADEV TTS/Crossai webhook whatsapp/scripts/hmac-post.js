
import crypto from 'crypto';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();

const url = (process.env.VERCEL_URL || 'http://localhost:3000') + '/api/webhooks/whatsapp/crossai';
const secret = process.env.META_APP_SECRET;

const body = {
  object: "whatsapp_business_account",
  entry: [{
    id: "WABA_ID",
    changes: [{
      field: "messages",
      value: {
        messaging_product: "whatsapp",
        metadata: { display_phone_number: "15551234567", phone_number_id: "1234567890" },
        contacts: [{ wa_id: "2348012345678", profile: { name: "Test User" } }],
        messages: [{ from: "2348012345678", id: "wamid.TEST", timestamp: `${Math.floor(Date.now()/1000)}`, type: "text", text: { body: "hello" } }]
      }
    }]
  }]
};

const raw = JSON.stringify(body);
const sig = "sha256=" + crypto.createHmac("sha256", secret).update(raw).digest("hex");
const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json", "X-Hub-Signature-256": sig }, body: raw });
console.log("status", r.status);
console.log(await r.text());
