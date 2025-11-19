# Systemd Logging Fix for Journalctl

## Problem

INFO logs for Wolfram Alpha API calls were not appearing when monitoring with:
```bash
sudo journalctl -u qadam-ai -f
```

## Root Cause

1. **Default logging configuration** not compatible with systemd
2. **Output buffering** preventing immediate log visibility
3. **Logs not being sent to stdout** properly for systemd to capture

## Solution Applied

### 1. Explicit StreamHandler Configuration

```python
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Output to stdout for systemd
    ],
    force=True  # Force reconfiguration
)
```

**Why:** Systemd captures stdout/stderr, so we explicitly configure logging to use stdout.

### 2. Unbuffered Output

```python
# Force unbuffered output for systemd
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
```

**Why:** Line buffering ensures logs appear immediately, not after buffer fills.

### 3. Explicit Flush After Log Blocks

```python
logger.info("=" * 80)
logger.info(f"WOLFRAM ALPHA API CALL - Expression ID: {expr_id}")
logger.info(f"Original Expression: {expression}")
# ... more logs ...
sys.stdout.flush()  # Force immediate output to systemd
```

**Why:** Guarantees logs are written immediately, visible in real-time via journalctl.

## Deployment Steps

### On AI VM

1. **Stash any local changes:**
   ```bash
   cd /opt/qadam-ai/ai
   git stash
   ```

2. **Pull the latest code:**
   ```bash
   git pull origin backend-ai
   ```

3. **Restart the service:**
   ```bash
   sudo systemctl restart qadam-ai
   ```

4. **Monitor logs in real-time:**
   ```bash
   sudo journalctl -u qadam-ai -f
   ```

## Verification

After deployment, you should see logs like:

```
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - ================================================================================
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - WOLFRAM ALPHA API CALL - Expression ID: expr_1
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - --------------------------------------------------------------------------------
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - Original Expression: 2x + 5 = 15
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - Query to Wolfram: 2x + 5 = 15
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - API Endpoint: http://api.wolframalpha.com/v2/query
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - Parameters:
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO -   - input: 2x + 5 = 15
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO -   - output: JSON
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO -   - format: plaintext
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO -   - podstate: Result__Step-by-step solution
Nov 19 21:13:45 qadam-ai-vm python[12345]: 2025-11-19 21:13:45 - __main__ - INFO - --------------------------------------------------------------------------------
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - Response Status Code: 200
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - Wolfram Query Success: True
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - Number of result pods: 3
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - Found result: x = 5
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - Extracted 2 solution steps
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - Final Result: x = 5
Nov 19 21:13:47 qadam-ai-vm python[12345]: 2025-11-19 21:13:47 - __main__ - INFO - ================================================================================
```

## Testing

### Test 1: Check Service Status
```bash
sudo systemctl status qadam-ai
```

Should show: `Active: active (running)`

### Test 2: Monitor Logs in Real-Time
```bash
sudo journalctl -u qadam-ai -f
```

Should show logs immediately as they're generated.

### Test 3: Filter Wolfram Logs
```bash
sudo journalctl -u qadam-ai | grep "WOLFRAM ALPHA"
```

Should show all Wolfram Alpha API calls.

### Test 4: Check Recent Logs
```bash
sudo journalctl -u qadam-ai --since "5 minutes ago"
```

Should show logs from the last 5 minutes.

## Troubleshooting

### Logs Still Not Appearing

**Check service is running:**
```bash
sudo systemctl status qadam-ai
```

**Check for errors:**
```bash
sudo journalctl -u qadam-ai -n 50 --no-pager
```

**Restart service:**
```bash
sudo systemctl restart qadam-ai
sudo journalctl -u qadam-ai -f
```

### Service Not Starting

**Check for Python errors:**
```bash
sudo journalctl -u qadam-ai -n 100 --no-pager
```

**Check environment variables:**
```bash
sudo systemctl cat qadam-ai
```

Ensure `GROQ_API_KEY` and `WOLFRAM_APP_ID` are set.

### Logs Appearing But Delayed

**Check if line buffering is working:**
```python
# In intelligent_question_solver.py, verify:
sys.stdout.reconfigure(line_buffering=True)
```

**Check if flush is being called:**
```python
# After each log block, verify:
sys.stdout.flush()
```

## Log Filtering Commands

### Show only Wolfram API calls:
```bash
sudo journalctl -u qadam-ai | grep "WOLFRAM ALPHA API CALL"
```

### Show only errors:
```bash
sudo journalctl -u qadam-ai -p err
```

### Show logs with timestamps:
```bash
sudo journalctl -u qadam-ai -o short-iso
```

### Show logs in JSON format:
```bash
sudo journalctl -u qadam-ai -o json-pretty
```

### Follow logs with grep filter:
```bash
sudo journalctl -u qadam-ai -f | grep --line-buffered "WOLFRAM"
```

### Show logs for specific time range:
```bash
sudo journalctl -u qadam-ai --since "2025-11-19 20:00:00" --until "2025-11-19 21:00:00"
```

## Benefits

✅ **Real-time monitoring** - See logs immediately as they're generated  
✅ **Easy debugging** - Track Wolfram Alpha API calls in production  
✅ **Performance monitoring** - Measure API response times  
✅ **Error tracking** - Identify failures immediately  
✅ **Audit trail** - Complete record of all API interactions  

## Summary

The logging configuration has been updated to ensure full compatibility with systemd journalctl:

1. ✅ Explicit stdout configuration
2. ✅ Unbuffered line output
3. ✅ Explicit flush after log blocks
4. ✅ Proper log format with timestamps

All Wolfram Alpha API calls are now immediately visible in journalctl!
