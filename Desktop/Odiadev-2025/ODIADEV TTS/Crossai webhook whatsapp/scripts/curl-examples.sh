#!/usr/bin/env bash
set -euo pipefail
: "${GRAPH_VERSION:=v20.0}"
: "${WABA_PERMANENT_TOKEN?Set WABA_PERMANENT_TOKEN}"
: "${WABA_ID?Set WABA_ID}"
: "${WABA_PHONE_NUMBER_ID?Set WABA_PHONE_NUMBER_ID}"
: "${TEST_TO?Set TEST_TO as E.164 e.g. 23480XXXX}"

echo "[1] List templates"
curl -s -G "https://graph.facebook.com/${GRAPH_VERSION}/${WABA_ID}/message_templates"   -d "access_token=${WABA_PERMANENT_TOKEN}"

echo "[2] Send hello_world"
curl -s -X POST "https://graph.facebook.com/${GRAPH_VERSION}/${WABA_PHONE_NUMBER_ID}/messages"   -H "Authorization: Bearer ${WABA_PERMANENT_TOKEN}"   -H "Content-Type: application/json"   -d "{"messaging_product":"whatsapp","to":"${TEST_TO}","type":"template","template":{"name":"hello_world","language":{"code":"en_US"}}}"
