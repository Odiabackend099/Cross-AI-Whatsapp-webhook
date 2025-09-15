// Production HMAC signature test script
import crypto from "crypto";
import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const url = "http://localhost:3000/api/webhooks/whatsapp/crossai";
const secret = process.env.META_APP_SECRET;

if (!secret) {
  console.error("ERROR: META_APP_SECRET not set in .env file");
  process.exit(1);
}

// Real WhatsApp webhook payload structure
const realWhatsAppPayload = {
  object: "whatsapp_business_account",
  entry: [{
    id: "108542142347049",
    changes: [{
      field: "messages",
      value: {
        messaging_product: "whatsapp",
        metadata: {
          display_phone_number: "2349876543210",
          phone_number_id: "103845678901234"
        },
        contacts: [{
          wa_id: "2348012345678",
          profile: { name: "Test Customer" }
        }],
        messages: [{
          from: "2348012345678",
          id: `wamid.HBgNMjM0ODAxMjM0NTY3OBUCABIYFjNBOTFGQzk3NEQ1NzQ5RkQ5NUMwQQA=${Date.now()}`,
          timestamp: Math.floor(Date.now() / 1000).toString(),
          type: "text",
          text: { body: "Hello, this is a real test message!" }
        }]
      }
    }]
  }]
};

const rawBody = JSON.stringify(realWhatsAppPayload);
const computedSignature = "sha256=" + crypto.createHmac("sha256", secret).update(rawBody).digest("hex");

console.log("=== PRODUCTION HMAC SIGNATURE TEST ===");
console.log("Testing with REAL WhatsApp payload structure");
console.log("Payload size:", rawBody.length, "bytes");
console.log("Secret used:", secret.substring(0, 8) + "..." + secret.substring(secret.length - 8));
console.log("Computed signature:", computedSignature.substring(0, 20) + "...");

try {
  console.log("\n--- Testing VALID signature ---");
  const validResponse = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Hub-Signature-256": computedSignature
    },
    body: rawBody
  });
  
  const validResult = await validResponse.text();
  console.log("Status:", validResponse.status);
  console.log("Response:", validResult);
  console.log("Valid signature test:", validResponse.status === 200 ? "PASS" : "FAIL");
  
  console.log("\n--- Testing INVALID signature ---");
  const invalidResponse = await fetch(url, {
    method: "POST", 
    headers: {
      "Content-Type": "application/json",
      "X-Hub-Signature-256": "sha256=this_is_definitely_not_a_valid_signature_hash"
    },
    body: rawBody
  });
  
  const invalidResult = await invalidResponse.text();
  console.log("Status:", invalidResponse.status);
  console.log("Response:", invalidResult);
  console.log("Invalid signature test:", invalidResponse.status === 403 ? "PASS" : "FAIL");
  
} catch (error) {
  console.error("ERROR during testing:", error.message);
}