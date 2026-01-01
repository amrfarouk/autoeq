## Task: eqMac API Discovery

### Objective
Determine how to programmatically control eqMac presets on macOS.

### Steps

1. **Check if eqMac is running and find its port**:
```bash
   lsof -i -P | grep -i eqmac
   ps aux | grep -i eqmac
```

2. **Search eqMac GitHub for API docs**:
   - Repo: https://github.com/bitgapp/eqMac
   - Look for: API endpoints, HTTP server, WebSocket, IPC

3. **Probe common localhost ports**:
```bash
   for port in 3000 8080 1234 5000 37289; do
     curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/ && echo " - port $port responds"
   done
```

4. **Check eqMac app support folder**:
```bash
   ls -la ~/Library/Application\ Support/eqMac*/
   cat ~/Library/Application\ Support/eqMac*/config.json 2>/dev/null
```

5. **Inspect app bundle for clues**:
```bash
   grep -r "localhost" /Applications/eqMac.app/Contents/ 2>/dev/null | head -20
```

### Deliverable
Report:
- API endpoint format (if exists)
- Available presets/IDs
- If no API: recommend alternative (accessibility API, cliclick, etc.)