# eqMac API Discovery Report

**Date**: 2026-01-01
**Status**: Complete
**Objective**: Determine how to programmatically control eqMac presets on macOS

---

## Executive Summary

| Finding | Status |
|---------|--------|
| eqMac Running | ✅ Yes (PID 36905) |
| Public API Available | ❌ No |
| Local HTTP Server | ⚠️ Port 5000 (AirTunes, 403 Forbidden) |
| WebSocket API | 🔜 Planned (not implemented) |
| Programmatic Control | ❌ Not currently possible |

---

## Detailed Findings

### 1. Process Status

| Aspect | Value |
|--------|-------|
| Running | ✅ Yes |
| PID | 36905 |
| Memory | ~256 MB |
| Audio Driver | eqMac.driver via coreaudiod (PID 559) |
| Network Ports | Port 5000 (AirTunes protocol) |

### 2. Port 5000 Analysis

eqMac runs an HTTP server on port 5000, but it's protected:

```
Server: AirTunes/925.5.1
Status: 403 Forbidden
Protocol: Apple AirTunes/Bonjour
```

Direct HTTP requests are rejected. The server expects:
- Proper AirTunes protocol handshake
- Authenticated Bonjour service discovery
- Authorized Apple ecosystem device connections

### 3. GitHub Repository Research

**Repository**: https://github.com/bitgapp/eqMac

| Feature | Status |
|---------|--------|
| Public API | ❌ Not available |
| WebSocket API | 🔜 Roadmap item |
| AppleScript | ❌ Not supported |
| CLI Interface | ❌ Not provided |
| OSC Protocol | ❌ Not implemented |

The README mentions a planned WebSocket API:
> "API - Control all aspects of eqMac through a WebSocket API. Works with any programming language that supports WebSockets."

**Current Status**: NOT YET IMPLEMENTED

### 4. Application Architecture

| Component | Location |
|-----------|----------|
| Main App | `/Applications/eqMac.app/Contents/MacOS/eqMac` |
| Web UI | Embedded Angular app (ui.zip, v5.4.1) |
| Helper Tool | `com.bitgapp.eqmac.helper` (XPC service) |
| Audio Driver | `eqMac.driver` (kernel-level) |

### 5. Remote API Endpoints

eqMac communicates with cloud services, not local APIs:

| Endpoint | Purpose |
|----------|---------|
| `https://api.eqmac.app/licenses/{userId}` | License validation |
| `https://api.eqmac.app/account` | Account info |
| `https://api.eqmac.app/subscription` | Subscription details |
| `https://ui.eqmac.app/v5/` | Web UI |
| `https://update.eqmac.app/update.xml` | Auto-updates |

### 6. Configuration Storage

| File | Location |
|------|----------|
| Preferences | `~/Library/Preferences/com.bitgapp.eqmac.plist` (3.6MB) |
| Cache DB | `~/Library/Caches/com.bitgapp.eqmac/Cache.db` |

Configuration includes:
- Equalizer presets (basic, advanced, expert with 10-band)
- Per-app volume settings
- License tokens (JWT-based, hardware-bound)
- UI state and preferences

---

## Recommendations

Since no API exists, here are alternative approaches:

### Option 1: macOS Accessibility API (Recommended)
```python
# Use pyobjc to interact with UI elements
from AppKit import NSWorkspace
from ApplicationServices import AXUIElementCreateApplication
# Programmatically click UI elements
```

### Option 2: AppleScript + System Events
```applescript
tell application "System Events"
    tell process "eqMac"
        -- Interact with UI elements
    end tell
end tell
```

### Option 3: Direct Preferences Manipulation
```bash
# Read current presets
defaults read com.bitgapp.eqmac

# Potentially modify presets (requires app restart)
defaults write com.bitgapp.eqmac PresetName "CustomPreset"
```

### Option 4: Wait for Official API
- Monitor releases at https://github.com/bitgapp/eqMac/releases
- Join Discord for updates: https://discord.eqmac.app

### Option 5: cliclick for UI Automation
```bash
# Install cliclick
brew install cliclick

# Click at coordinates (requires finding button positions)
cliclick c:100,200
```

---

## Conclusion

**eqMac does NOT currently have a public API for programmatic control.**

The application is a native macOS audio equalizer that:
1. Integrates at the kernel level via Core Audio
2. Uses a cloud-based architecture for licensing/updates
3. Has a planned but unimplemented WebSocket API
4. Runs an AirTunes server on port 5000 (inaccessible)

**Best Current Approach**: Use macOS Accessibility APIs or AppleScript with System Events to automate the UI, or directly manipulate the preferences plist (with app restart).

---

## Files Generated

- This report: `reports/eqMac_API_Discovery_Report.md`
