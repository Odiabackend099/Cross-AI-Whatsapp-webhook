
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();
const base = process.env.VERCEL_URL || 'http://localhost:3000';
const token = process.env.VERIFY_TOKEN || 'wrong';
const r = await fetch(`${base}/api/webhooks/whatsapp/crossai?hub.mode=subscribe&hub.verify_token=${encodeURIComponent(token)}&hub.challenge=12345`);
console.log("status", r.status);
console.log(await r.text());
