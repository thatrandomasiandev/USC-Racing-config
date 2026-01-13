# Network Access Guide

Your server is already configured to be accessible on your local network!

## Quick Start

Just run:

```bash
./run_server.sh
```

The script will show you both the localhost URL and your network IP address.

## Finding Your IP Address

If you need to find your IP manually:

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

## Accessing from Other Devices

Once the server is running, other devices on the same network can access:

- **Main App**: `http://YOUR_IP:8000`
- **API Docs**: `http://YOUR_IP:8000/docs`
- **Health Check**: `http://YOUR_IP:8000/api/health`

### Example:
If your computer's IP is `10.25.91.52`, access from another device:
- `http://10.25.91.52:8000`

## Requirements

1. **Same Network**: All devices must be on the same WiFi/LAN network
2. **Firewall**: Make sure your firewall allows connections on port 8000
3. **Server Running**: Keep the server running on your main computer

## Firewall Configuration

### macOS

If you get "Connection Refused", allow Python through the firewall:

1. System Settings → Network → Firewall → Options
2. Allow Python/uvicorn to accept incoming connections

Or temporarily disable firewall to test:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

### Windows

1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Add Python or port 8000

### Linux

```bash
sudo ufw allow 8000
```

## Testing Network Access

1. **On your computer**: Test `http://localhost:8000`
2. **On your phone/tablet** (same WiFi): Test `http://YOUR_IP:8000`
3. **Check the run script output** - it shows your IP automatically

## Troubleshooting

### "Connection Refused"

- ✅ Check firewall settings
- ✅ Verify server is running
- ✅ Confirm devices are on same network
- ✅ Try accessing from your own computer using the IP (not localhost)

### "Can't Connect"

- ✅ Check IP address is correct
- ✅ Verify port 8000 is not blocked
- ✅ Try `ping YOUR_IP` from another device

### Port Already in Use

Change the port in `.env`:
```bash
TEL_PORT=8001
```

Then access via `http://YOUR_IP:8001`

## Server Configuration

The server is already configured with:
- ✅ `HOST=0.0.0.0` (listens on all network interfaces)
- ✅ `CORS_ORIGINS=*` (allows requests from any origin)
- ✅ Default port: `8000`

## That's It!

Just run `./run_server.sh` and use the network URL it shows you. 🚀

