# CTV ↔ Smartphone Connection Guide (No pairing code)

This guide documents the **CTV ad creative** (HTML/JS webview) and **smartphone landing page** handshake using the current backend endpoints:

- `POST /api/v1/session/register`
- `POST /api/v1/session/claim`
- `POST /api/v1/session/interact/{session_id}`
- `GET /api/v1/session/{session_id}`

## Architecture overview

```
┌─────────────────────┐          ┌──────────────┐          ┌─────────────────────┐
│   CTV Ad Creative   │──HTTP───►│  FastAPI API  │◄──HTTP───│  Smartphone Browser │
│   (HTML/JS webview) │          │              │          │  (landing page)     │
└─────────────────────┘          └──────────────┘          └─────────────────────┘
           │
           │ (read-only)
           ▼
   ┌─────────────────────┐
   │ Supabase read path   │  (Edge Function or similar)
   └─────────────────────┘
```

- **All writes go through FastAPI** (claim + interactions).
- **CTV reads interactions** via a Supabase serverless function (or equivalent) filtered by `session_id`.

## End-to-end flow

- **1) CTV registers a session**
  - Trigger this only after an explicit remote interaction (OK/Enter).
  - Backend returns a `claim_token` and `qr_url`.
- **2) Phone claims the session**
  - Phone extracts `claim_token` from the QR landing URL (fragment) and calls `/session/claim`.
  - Backend returns `interaction_config` + `interaction_token`.
- **3) Phone posts interactions**
  - Every interaction call includes `Authorization: Bearer <interaction_token>`.
- **4) CTV consumes interactions**
  - CTV polls/streams new `interaction` rows for this `session_id` and triggers local handlers.

## Session/register (CTV → API)

```
POST /api/v1/session/register
Content-Type: application/json

{
  "campaign_id": "<uuid>"
}
```

**Response (201):**

```json
{
  "id": "<session_id>",
  "campaign_id": "<campaign_id>",
  "status": "waiting_for_pair",
  "claim_token": "<opaque>",
  "qr_url": "https://<landing>#claim=<opaque>",
  "created_at": "2026-02-25T10:25:10.000000",
  "expires_at": "2026-02-25T10:26:10.000000"
}
```

- **Render** the QR code using `qr_url`.
- The token is in the **URL fragment** (`#claim=...`) to reduce referrer/log leakage.

## Session/claim (Phone → API)

Phone extracts:

```javascript
const claimToken = new URLSearchParams(window.location.hash.slice(1)).get("claim");
if (!claimToken) throw new Error("Missing claim token");
```

Then:

```
POST /api/v1/session/claim
Content-Type: application/json

{
  "claim_token": "<claim_token>"
  "campaign_id": uuid
}
```

**Response (200):**

```json
{
  "session_id": "<session_id>",
  "interaction_token": "<jwt>",
  "expires_at": "2026-02-25T10:26:10.000000",
  "interaction_config": [
    {
      "action_type": "toggle_asset",
      "label": "Show Product",
      "payload": { "asset_id": "product_1" }
    }
  ]
}
```

- **`interaction_token`** is a short-lived Bearer token bound to that session. Keep it in memory (don’t persist).

**Common errors:**

| Status | Meaning |
|--------|---------|
| 400 | Invalid claim token |
| 409 | Session already claimed/paired |
| 410 | Claim token or session expired |

## Session/interact (Phone → API)

```
POST /api/v1/session/interact/<session_id>
Authorization: Bearer <interaction_token>
Content-Type: application/json

{
  "action_type": "toggle_asset",
  "payload": { "asset_id": "product_1" }
}
```

**Errors:**

| Status | Meaning |
|--------|---------|
| 401 | Missing/invalid/expired interaction token |
| 404 | Session not found |
| 409 | Session not paired yet |
| 410 | Session expired |

## CTV: consuming interactions (Supabase read path)

Because CTV should not call the write endpoints directly for streaming, have it read persisted interaction rows for the session.

**Suggested Edge Function shape:**

```
GET https://<supabase-edge-fn>/ctv/interactions?session_id=<uuid>&after=<cursor>
→ returns [{ id, session_id, action_type, payload, created_at }, ...]
```

CTV polling loop recommendations:

- **Start fast, then back off** (e.g. 300–500ms up to ~2s).
- **Stop** when `GET /api/v1/session/{session_id}` returns `expired` or when your local ad timeout ends.
- Use `after` cursor as either `created_at` or the last `interaction.id` you processed.

## Timeouts (current backend defaults)

- Session TTL is **~60 seconds** (`SESSION_EXPIRY_SECONDS`).
- `interaction_token` expiry matches the session expiry (with a tiny grace).
