# 888 Sport Forwarder v7 — EXTREME
**Prepared by Abuta**

## Deploy

```bash
pip install -r requirements.txt
python forwarder.py
```

First run: enter your phone number + OTP when prompted. Session saved to `session.session`.

## New Features in v7

| Feature | Flag | Default |
|---------|------|---------|
| Unicode font styles (bold/italic/mono) | `TEXT_FONT_STYLE` | `"bold"` |
| Compact time display (· HH:MM) | `TIME_COMPACT` | `True` |
| Media fallback caption (no unnamed) | `MEDIA_NO_CAPTION_TEXT` | auto |
| Default image on text-only msgs | `ATTACH_DEFAULT_IMAGE` | `False` |
| Smart scheduler (6 daily slots) | `SMART_SCHEDULE_ENABLED` | `True` |
| Content enrichment (🔴 LIVE, sport emoji) | `ENRICH_ENABLED` | `True` |
| Auto thread reply | `AUTO_THREAD_REPLY_ENABLED` | `False` |
| Media dedup by file hash | `DEDUP_MEDIA_ENABLED` | `True` |
| Heartbeat loop (30 min) | `HEARTBEAT_ENABLED` | `True` |
| CSV analytics per message | `ANALYTICS_ENABLED` | `True` |
| Link preview control | `LINK_PREVIEW_ENABLED` | `False` |
| Pause/resume without restart | `/pause` `/resume` | — |

## Commands (send in Saved Messages)

```
/ping          — uptime + key stats
/stats         — full stats table
/status        — live dashboard with sparklines
/queue         — DLQ pending messages
/pause         — stop forwarding (no restart needed)
/resume        — resume forwarding
/reload        — reload mapping + hotconfig
/fontset bold|italic|mono|normal
/timefmt compact|full
/testmsg       — send branded test to Saved Messages
/analytics     — analytics event count
```

## Hot Config

Edit `hotconfig.json` and send `/reload` — no restart needed.

## Boost Sessions

Place session files (`boost1.session` … `boost5.session`) beside the script. Login each manually once, then the bot manages them automatically.

## Files Created at Runtime

| File | Purpose |
|------|---------|
| `session.session` | Main account session |
| `mapping.json` | src→tgt message ID map |
| `bandit.json` | Header A/B test state |
| `dlq.db` | Failed-message retry queue |
| `backfill_state.json` | Backfill checkpoint |
| `growth.csv` | Member count history |
| `analytics.csv` | Per-message analytics |
| `forwarder.log` | Full log |
