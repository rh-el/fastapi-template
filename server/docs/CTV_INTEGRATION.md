# CTV Interactive Advertising -- Integration Guide

This document describes how to integrate the **CTV ad creative** (HTML/JS running in a webview) and the **smartphone landing page** with the backend API to deliver interactive advertising experiences.

## Architecture Overview

```
┌─────────────────────┐         ┌──────────────┐         ┌─────────────────────┐
│   CTV Ad Creative   │◄──WS───►│  FastAPI API  │◄──HTTP──│  Smartphone Browser │
│   (HTML/JS iframe)  │         │              │         │  (landing page)     │
└─────────────────────┘         └──────────────┘         └─────────────────────┘
```

- **CTV** communicates via **WebSocket** (real-time push from API)
- **Smartphone** communicates via **REST HTTP** (request/response)
- The API is a **thin relay**: it stores interactions and pushes lightweight events to the CTV. All visual logic (asset display, opacity, animations) lives in the CTV ad creative JS.

## Flow Summary

1. Ad creative loads on CTV. **No API call is made** on impression.
2. Viewer presses a button on the TV remote (e.g., OK).
3. CTV JS calls `POST /session/register` to create a session and get a pairing code.
4. CTV JS opens a WebSocket to `/ws/ctv/{session_id}`.
5. CTV JS renders the QR code (static, baked per campaign) and the pairing code overlay.
6. User scans QR code on their phone, lands on the campaign page.
7. User enters the pairing code on the phone page.
8. Phone calls `POST /session/pair` with the campaign ID and pairing code.
9. API updates the session to "paired" and sends a `session_paired` event to the CTV via WebSocket.
10. Phone displays interaction buttons (from the `interaction_config` returned in the pair response).
11. User taps a button. Phone calls `POST /session/{id}/interact`.
12. API records the interaction and pushes an `interaction` event to the CTV via WebSocket.
13. CTV JS receives the event and calls the appropriate local handler (e.g., `toggleAsset()`).

---

## CTV Ad Creative Integration

### Prerequisites

- The ad creative runs as HTML/JS inside an iframe or webview on the CTV.
- The creative must know its `campaign_id` (typically injected as a macro or hardcoded at build time).
- The QR code is pre-baked into the creative (static URL per campaign, e.g., `https://interact.example.com/c/{campaign_id}`).

### Step 1: Listen for Remote Button Press

```javascript
const API_BASE = "https://your-api-domain.com/api/v1";
const CAMPAIGN_ID = "your-campaign-uuid";

let sessionId = null;
let ws = null;

// Only trigger session creation on deliberate viewer interaction
document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.keyCode === 13) { // OK button on most remotes
        if (!sessionId) {
            initSession();
        }
    }
});
```

### Step 2: Register a Session

```javascript
async function initSession() {
    const res = await fetch(`${API_BASE}/session/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ campaign_id: CAMPAIGN_ID }),
    });
    const data = await res.json();

    sessionId = data.id;
    const pairingCode = data.pairing_code; // e.g., "A7X3"

    // Display pairing code on screen (next to the pre-baked QR code)
    showPairingCode(pairingCode);

    // Connect WebSocket
    connectWebSocket(sessionId);
}
```

### Step 3: Connect via WebSocket

```javascript
function connectWebSocket(sessionId) {
    const wsUrl = `wss://your-api-domain.com/api/v1/ws/ctv/${sessionId}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("WebSocket connected");
        // Start heartbeat to keep connection alive
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ event: "heartbeat" }));
            }
        }, 30000); // every 30s
    };

    ws.onmessage = (msg) => {
        const { event, data } = JSON.parse(msg.data);
        handleEvent(event, data);
    };

    ws.onclose = (e) => {
        console.log("WebSocket closed:", e.code, e.reason);
        // Optionally: show "session ended" UI
    };
}
```

### Step 4: Handle Incoming Events

```javascript
function handleEvent(event, data) {
    switch (event) {
        case "session_paired":
            onSessionPaired();
            break;
        case "interaction":
            onInteraction(data);
            break;
        case "session_expired":
            onSessionExpired();
            break;
        case "heartbeat_ack":
            // Connection healthy, nothing to do
            break;
    }
}

function onSessionPaired() {
    // Hide the QR code and pairing code, show "Connected!" feedback
    document.getElementById("pairing-overlay").style.display = "none";
    document.getElementById("connected-badge").style.display = "block";
}

function onInteraction(data) {
    // data = { action_type: "toggle_asset", payload: { asset_id: "product_1" } }
    switch (data.action_type) {
        case "toggle_asset":
            toggleAsset(data.payload.asset_id);
            break;
        case "show_overlay":
            showOverlay(data.payload);
            break;
        // Add more handlers as needed per creative
    }
}

function onSessionExpired() {
    // Clean up and show default ad state
    if (ws) ws.close();
    document.getElementById("pairing-overlay").style.display = "none";
}
```

### Step 5: Visual Logic (Creative-Specific)

All visual mechanics are 100% in the creative JS. The API sends only action names and minimal payloads.

```javascript
function toggleAsset(assetId) {
    const el = document.getElementById(assetId);
    if (!el) return;
    el.style.opacity = el.style.opacity === "1" ? "0" : "1";
    el.style.transition = "opacity 0.3s ease";
}

function showOverlay(payload) {
    const overlay = document.getElementById("overlay");
    overlay.textContent = payload.text || "";
    overlay.style.display = "block";
    if (payload.duration) {
        setTimeout(() => { overlay.style.display = "none"; }, payload.duration * 1000);
    }
}

function showPairingCode(code) {
    const el = document.getElementById("pairing-code");
    el.textContent = code;
    document.getElementById("pairing-overlay").style.display = "flex";
}
```

### WebSocket Events Reference (CTV Receives)

| Event | Data | When |
|-------|------|------|
| `session_paired` | `{}` | A phone successfully paired with this session |
| `interaction` | `{ action_type: string, payload: object }` | A phone user triggered an action |
| `session_expired` | `{}` | The session timed out |
| `heartbeat_ack` | — | Response to a heartbeat ping |

### WebSocket Events Reference (CTV Sends)

| Event | Data | Purpose |
|-------|------|---------|
| `heartbeat` | — | Keep the connection alive (send every ~30s) |

---

## Smartphone Landing Page Integration

The smartphone page is the web app the user lands on after scanning the QR code. It communicates with the API via standard REST calls.

### Prerequisites

- The page URL contains the `campaign_id` (from the QR code, e.g., `https://interact.example.com/c/{campaign_id}`).
- No authentication required (anonymous sessions).

### Step 1: Show Pairing Code Input

After loading, the page should display a text input for the 4-character pairing code shown on the TV.

### Step 2: Pair with the CTV

```
POST /api/v1/session/pair
Content-Type: application/json

{
    "campaign_id": "uuid-from-qr-code",
    "pairing_code": "A7X3"
}
```

**Response (200):**

```json
{
    "session_id": "3eabbf9c-8220-4150-b312-f5cf64ec4b6a",
    "interaction_config": [
        {
            "action_type": "toggle_asset",
            "label": "Show Product",
            "payload": { "asset_id": "product_1" }
        },
        {
            "action_type": "toggle_asset",
            "label": "Show Logo",
            "payload": { "asset_id": "logo_1" }
        }
    ]
}
```

- `session_id`: Store this -- you need it for all subsequent interaction calls.
- `interaction_config`: Array of actions to render as buttons on the phone UI. Each has a `label` (display text), an `action_type`, and a `payload` to send back when clicked.

**Error responses:**

| Status | Meaning |
|--------|---------|
| 400 | Invalid pairing code for this campaign |
| 404 | Campaign not found |
| 409 | Session already paired |
| 410 | Session expired |

### Step 3: Render Interaction Buttons

Use the `interaction_config` from the pair response to dynamically generate the UI:

```javascript
function renderButtons(interactionConfig, sessionId) {
    const container = document.getElementById("buttons");
    interactionConfig.forEach((action) => {
        const btn = document.createElement("button");
        btn.textContent = action.label;
        btn.addEventListener("click", () => {
            sendInteraction(sessionId, action.action_type, action.payload);
        });
        container.appendChild(btn);
    });
}
```

### Step 4: Send Interactions

```
POST /api/v1/session/{session_id}/interact
Content-Type: application/json

{
    "action_type": "toggle_asset",
    "payload": { "asset_id": "product_1" }
}
```

**Response (201):**

```json
{
    "id": "0ce06c48-29ab-4019-a19d-6d04c4f22ba3",
    "session_id": "3eabbf9c-8220-4150-b312-f5cf64ec4b6a",
    "action_type": "toggle_asset",
    "payload": { "asset_id": "product_1" },
    "created_at": "2026-02-12T10:25:55.000000"
}
```

**Error responses:**

| Status | Meaning |
|--------|---------|
| 404 | Session not found |
| 409 | Session is not paired yet |
| 410 | Session expired |

### Step 5: Polling Fallback (Optional)

If you need to check session status from the phone side:

```
GET /api/v1/session/{session_id}
```

**Response (200):**

```json
{
    "id": "3eabbf9c-8220-4150-b312-f5cf64ec4b6a",
    "campaign_id": "76712e6e-b2f4-47a2-baf4-7db3a7c19e3d",
    "pairing_code": "A7X3",
    "status": "paired",
    "created_at": "2026-02-12T10:25:50.000000",
    "expires_at": "2026-02-12T10:55:50.000000"
}
```

Session statuses: `waiting_for_pair`, `paired`, `expired`, `closed`.

---

## Campaign Management API

Campaigns are created and managed via the admin endpoints. Each campaign defines the set of interactions available.

### Create a Campaign

```
POST /api/v1/campaign/
Content-Type: application/json

{
    "name": "Summer Product Launch",
    "description": "Interactive ad for summer collection",
    "qr_base_url": "https://interact.example.com/c",
    "interaction_config": [
        {
            "action_type": "toggle_asset",
            "label": "Show Product",
            "payload": { "asset_id": "product_1" }
        },
        {
            "action_type": "show_overlay",
            "label": "Learn More",
            "payload": { "text": "Visit example.com", "duration": 5 }
        }
    ]
}
```

### List All Campaigns

```
GET /api/v1/campaign/
```

### Get Campaign by ID

```
GET /api/v1/campaign/{campaign_id}
```

---

## Session Lifecycle & Timeouts

| Phase | TTL | Description |
|-------|-----|-------------|
| Unpaired | 5 minutes | From session registration to pairing. If no phone pairs within this window, the session expires. |
| Paired | 30 minutes | From pairing. The session remains active for interactions during this window. |

When a session expires:
- Subsequent API calls return `410 Gone`.
- The CTV receives a `session_expired` WebSocket event (if still connected).
- The pairing code becomes available for reuse.

---

## Pairing Code Rules

- 4-character alphanumeric (uppercase letters + digits), e.g., `A7X3`.
- Case-insensitive on input (the API uppercases before matching).
- Unique among **active sessions for the same campaign** (not globally).
- Displayed alongside the pre-baked QR code on the CTV screen.
