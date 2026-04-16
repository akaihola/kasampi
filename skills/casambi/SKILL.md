---
name: casambi-discovery-linux
description: |
  Discover and list Casambi Bluetooth lighting control devices on Linux systems using Bluetooth Low Energy scanning.
  
  Use when Claude needs to:
  - Find nearby Casambi BLE devices on Linux machines
  - List discovered CBU-TED, PROFESSIONALE CASAMB, CBU-PWM4, and DALI modules
  - Verify Casambi device visibility from a Linux host
  - Troubleshoot Casambi Bluetooth connectivity on Linux
  
  Requires: Linux with bluetoothctl, BlueZ stack, and Bluetooth LE support
---

# Casambi Discovery (Linux)

## Overview

Scan for and discover Casambi Bluetooth Low Energy (BLE) lighting control devices on Linux systems using bluetoothctl. Provides structured discovery of CBU-TED, PROFESSIONALE CASAMB, and other Casambi-compatible modules commonly used in professional lighting installations.

**Platform:** Linux (requires bluetoothctl/BlueZ)
**Typical devices:** CBU-TED, PROFESSIONALE CASAMB, CBU-PWM4 RGBW, DALI 1xDIM

## Quick Start

Discover Casambi devices using the built-in script:

```bash
# Run the discovery script
./scripts/casambi_scan.py
```

This will:
- Enable Bluetooth power if needed
- Scan for 15 seconds
- List all discovered Casambi devices
- Show non-Casambi BLE devices for context

## Device Types Detected

| Device Type | Example Names | Use Case |
|-------------|---------------|----------|
| CBU-TED | `CBU-TED`, `CBU-PWM4 RGBW` | Tunable white / RGBW control |
| PROFESSIONALE CASAMB | `PROFESSIONALE CASAMB` | Professional lighting modules |
| DALI Modules | `DALI 1xDIM [A0]` | DALI bus controllers |

## Manual Discovery

If the script is unavailable, use bluetoothctl directly:

```bash
# Start interactive session
bluetoothctl

# Inside bluetoothctl:
power on
scan on
# Wait 10-15 seconds
devices
scan off
```

Filter for Casambi-specific results:

```bash
timeout 15 bash -c '
  bluetoothctl power on 2>/dev/null
  bluetoothctl scan on &
  sleep 12
  bluetoothctl scan off 2>/dev/null
  bluetoothctl devices 2>/dev/null
' | grep -iE "(CBU|TED|CASAMB|DALI)"
```

## What to Expect

**Typical Output:**
```
Device 5B:56:EA:B2:BE:36 CBU-TED
Device 41:EE:68:5B:B8:89 CBU-TED
Device 4C:C5:EE:86:74:64 PROFESSIONALE CASAMB
Device 3A:B6:D2:24:A9:2A PROFESSIONALE CASAMB
```

**Key Points:**
- Casambi devices use random Bluetooth addresses (change periodically)
- Device names are human-readable identifiers
- Scanning requires the Bluetooth controller to be powered on
- Devices must be within Bluetooth range (~10 meters, line of sight works best)

## Troubleshooting

**No devices found:**
- Verify Bluetooth is enabled: `bluetoothctl show` → check "Powered: yes"
- Check if controller exists: `bluetoothctl list`
- Ensure devices are powered and in range
- Try longer scan duration (20-30 seconds)

**Permission errors:**
- User must be in `bluetooth` group
- Or run with appropriate permissions via `sudo` (not recommended for regular use)

**Stale device list:**
- Run `bluetoothctl remove <MAC>` to clear old entries
- Restart scanning

## Resources

### scripts/
- `casambi_scan.py` - Automated discovery script with formatted output

### references/
- No additional references required for basic discovery

### assets/
- No assets required for discovery operations
