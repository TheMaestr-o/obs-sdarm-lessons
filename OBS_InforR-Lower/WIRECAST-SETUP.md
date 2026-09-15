# Wirecast Setup Guide for Lower Third Overlay

This guide explains how to use the Wirecast-compatible versions of the lower third overlay system.

## Why a Wirecast Version?

The original OBS setup uses `BroadcastChannel` to send overlay data from the control panel to the display window. BroadcastChannel works well when both windows are within the same browser context (like OBS Browser Sources in the same scene).

Wirecast opens browser windows in separate contexts, so `BroadcastChannel` messages don't cross between them. The Wirecast versions use **localStorage polling** instead:

- **panel-wirecast.html** writes overlay data to localStorage when you press "Show"
- **result-wirecast.html** polls localStorage every 500ms to detect and apply updates

This approach works reliably in Wirecast without additional configuration.

## What You Need

1. A local HTTP server running on port 8001 (see below)
2. Two separate browser windows or tabs
3. The Wirecast-compatible files:
   - `panel-wirecast.html` — control panel
   - `result-wirecast.html` — overlay display

## Setup Steps

### 1. Start the Local Server

Run the same server you use for the OBS version:

```bash
cd /Users/ohnedan/Developer/OBS/OBS_InforR-Lower
python3 -m http.server 8001
```

Or use any HTTP server (Node.js, nginx, etc.) that serves this directory on http://localhost:8001.

### 2. Open the Control Panel

In one browser window, open:

```
http://localhost:8001/panel-wirecast.html
```

This shows:
- Line 1 / Line 2 text fields
- Lesson & Question picker (with Quarter, Language, Lesson selects)
- Template selector (Slash & Slide, Slide Up/Down)
- Color pickers for Color 1 and Color 2
- **Show** button

### 3. Open the Overlay Display

In a second browser window (or tab in a different browser), open:

```
http://localhost:8001/result-wirecast.html
```

This window shows the lower third overlay. It starts hidden and will display content when you press Show.

### 4. Add to Wirecast

In Wirecast, add the overlay window as a browser source:

**Method A: Window Capture (Recommended)**
- In Wirecast, add a new layer and select "Window Capture"
- Choose the browser window showing `result-wirecast.html`
- Position and size the capture as needed

**Method B: URL Input (if supported)**
- Some Wirecast versions allow entering a URL directly
- Use `http://localhost:8001/result-wirecast.html`
- Check your Wirecast version's documentation

### 5. Position and Size

The overlay is anchored to the bottom-left (220px tall, full width). Position it in Wirecast to match your lower third area.

## Usage During Live Stream

1. **Panel Window** (foreground on your computer):
   - Pick a Quarter, Language, Lesson from Settings (once per session)
   - Choose a template (Slash & Slide or Slide Up/Down)
   - Optionally adjust colors
   - Click a question letter to load it, OR type your own Line 1/Line 2
   - Press **Show**

2. **Overlay Window** (captured in Wirecast):
   - Immediately displays the text with the chosen animation
   - Holds the content indefinitely until you press Show again
   - No manual "hide" button needed — just press Show with empty text if needed

3. **Repeating**:
   - Click Next/Previous to step through questions
   - Press Show for each question
   - Overlay updates instantly

## Comparison to OBS Version

| Aspect | OBS | Wirecast |
|--------|-----|----------|
| **Communication** | BroadcastChannel + localStorage | localStorage polling (500ms) |
| **Setup** | Custom Browser Dock or two Browser Sources | Two separate browser windows |
| **Latency** | Instant | ~500ms (polling interval) |
| **Color 1 default** | #ffffff (white) | #ffffff (white) |
| **Color 2 default** | #c6a15b (gold) | #c6a15b (gold) |
| **Lesson picker** | Same (requires http://) | Same (requires http://) |
| **Files created** | N/A | `panel-wirecast.html`, `result-wirecast.html` |

## Troubleshooting

**Overlay doesn't update when I press Show:**
- Check that both windows are open and showing the correct URLs
- Verify the local server is running (try opening http://localhost:8001 in a browser)
- Check browser console (F12) for errors — there should be none
- Firewall/network: both windows must access the same localhost:8001

**Colors don't appear:**
- Color pickers use hex format (3 or 6 digits)
- Default Color 1 is `fff` (white), Color 2 is `c6a15b` (gold)
- Hex values are case-insensitive

**Lesson/Question picker is empty:**
- Only works over http://, not file://
- Make sure panel-wirecast.html is opened as `http://localhost:8001/panel-wirecast.html`
- Check server logs to see if lessons-data.json was fetched

**Overlay only shows briefly then disappears:**
- This is correct behavior — the overlay holds the content after the animation completes
- If you want to hide it, press Show with empty Line 1/Line 2
- There is no explicit "hide" button

## Files Included

- **result-wirecast.html** — 76 lines, thin wrapper with localStorage polling
- **panel-wirecast.html** — 790 lines, control panel with all features (lesson picker, colors, templates)
- **WIRECAST-SETUP.md** — this file

The original OBS files (`result.html`, `panel.html`) remain unchanged.

## Performance Notes

- Polling interval: 500ms (good balance between responsiveness and CPU usage)
- Timestamp deduplication: prevents animations from restarting if localStorage changes but timestamp is same
- Cache-busting: `?_t=...` in iframe URL ensures fresh reload even with identical text

## Next Steps

1. Test locally with both windows open before going live
2. Verify overlay positioning in Wirecast (it's 220px tall)
3. During stream, keep the panel window in focus to control the overlay
4. Use Next/Previous buttons to step through questions quickly
