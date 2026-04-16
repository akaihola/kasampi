#!/usr/bin/env python3
"""
Casambi Bluetooth Low Energy device discovery scanner.
Discovers CBU-TED, PROFESSIONALE CASAMB, and other Casambi lighting control modules.
"""

import subprocess
import re
import sys
from datetime import datetime

# Casambi device name patterns
CASAMBI_PATTERNS = [
    re.compile(r'CBU-TED', re.IGNORECASE),
    re.compile(r'CBU-PWM', re.IGNORECASE),
    re.compile(r'PROFESSIONALE CASAMB', re.IGNORECASE),
    re.compile(r'CASAMB', re.IGNORECASE),
    re.compile(r'DALI.*DIM', re.IGNORECASE),
    re.compile(r'DC MAXIJOLLY', re.IGNORECASE),
]

def is_casambi_device(name):
    """Check if a device name matches Casambi patterns."""
    return any(pattern.search(name) for pattern in CASAMBI_PATTERNS)

def run_bluetoothctl_scan(duration=15):
    """Run bluetoothctl scan and capture output."""
    print(f"🔍 Starting Casambi device scan ({duration}s)...")
    print("   Ensure Bluetooth is enabled and devices are in range.")
    print()

    # Build the scan command using a simpler heredoc approach
    cmd = f'''(
        {{
            echo "power on"
            sleep 0.5
            echo "scan on"
            sleep {duration}
            echo "scan off"
            sleep 0.5
            echo "devices"
            sleep 0.5
            echo "quit"
        }} | bluetoothctl 2>&1
    )'''

    try:
        result = subprocess.run(
            ['bash', '-c', cmd],
            capture_output=True,
            text=True,
            timeout=duration + 10
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        print("❌ Scan timed out")
        return ""
    except Exception as e:
        print(f"❌ Error running scan: {e}")
        return ""

def parse_devices(output):
    """Parse bluetoothctl output to extract devices."""
    devices = []

    # Look for NEW Device lines during scanning
    new_pattern = re.compile(r'\[NEW\] Device ([0-9A-F:]{17}) (.+)', re.IGNORECASE)
    # Look for Device lines in the list
    list_pattern = re.compile(r'^Device ([0-9A-F:]{17}) (.+)$', re.IGNORECASE | re.MULTILINE)

    # Extract all devices
    for match in new_pattern.finditer(output):
        mac = match.group(1)
        name = match.group(2).strip()
        devices.append((mac, name))

    for match in list_pattern.finditer(output):
        mac = match.group(1)
        name = match.group(2).strip()
        devices.append((mac, name))

    # Remove duplicates while preserving order
    seen = set()
    unique_devices = []
    for mac, name in devices:
        if mac not in seen:
            seen.add(mac)
            unique_devices.append((mac, name))

    return unique_devices

def categorize_devices(devices):
    """Separate Casambi devices from other BLE devices."""
    casambi = []
    other = []

    for mac, name in devices:
        if is_casambi_device(name):
            casambi.append((mac, name))
        else:
            other.append((mac, name))

    return casambi, other

def display_results(casambi_devices, other_devices):
    """Display formatted scan results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*60}")
    print(f"📊 Casambi Device Discovery Results - {timestamp}")
    print(f"{'='*60}")

    if casambi_devices:
        print(f"\n🟢 Casambi Devices Found: {len(casambi_devices)}")
        print("-" * 60)

        # Group by device type
        cbu_ted = [(m, n) for m, n in casambi_devices if 'CBU-TED' in n.upper()]
        cbu_pwm = [(m, n) for m, n in casambi_devices if 'CBU-PWM' in n.upper()]
        profess = [(m, n) for m, n in casambi_devices if 'PROFESSIONALE' in n.upper()]
        other_casambi = [(m, n) for m, n in casambi_devices
                        if not any(x in n.upper() for x in ['CBU-TED', 'CBU-PWM', 'PROFESSIONALE'])]

        if cbu_ted:
            print(f"\n  CBU-TED ({len(cbu_ted)}):")
            for mac, name in cbu_ted:
                print(f"    • {mac}  {name}")

        if cbu_pwm:
            print(f"\n  CBU-PWM ({len(cbu_pwm)}):")
            for mac, name in cbu_pwm:
                print(f"    • {mac}  {name}")

        if profess:
            print(f"\n  PROFESSIONALE CASAMB ({len(profess)}):")
            for mac, name in profess:
                print(f"    • {mac}  {name}")

        if other_casambi:
            print(f"\n  Other Casambi ({len(other_casambi)}):")
            for mac, name in other_casambi:
                print(f"    • {mac}  {name}")
    else:
        print("\n⚠️  No Casambi devices detected")
        print("   Try moving closer to the devices or extending scan duration.")

    if other_devices:
        print(f"\n🔵 Other BLE Devices: {len(other_devices)}")
        print("-" * 60)
        # Show max 5 to avoid clutter
        for mac, name in other_devices[:5]:
            print(f"    • {mac}  {name}")
        if len(other_devices) > 5:
            print(f"    ... and {len(other_devices) - 5} more")

    print(f"\n{'='*60}")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Discover Casambi Bluetooth lighting control devices'
    )
    parser.add_argument(
        '-d', '--duration',
        type=int,
        default=15,
        help='Scan duration in seconds (default: 15)'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Show raw bluetoothctl output for debugging'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔦 Casambi Device Scanner")
    print("   Discovering Bluetooth Low Energy lighting controllers")
    print("=" * 60)
    print()

    # Run scan
    output = run_bluetoothctl_scan(args.duration)

    if not output:
        print("❌ Failed to get scan results")
        sys.exit(1)

    if args.raw:
        print("\n--- Raw bluetoothctl output ---")
        print(output)
        print("--- End raw output ---\n")

    # Parse and display results
    devices = parse_devices(output)
    casambi, other = categorize_devices(devices)
    display_results(casambi, other)

    # Exit code based on findings
    sys.exit(0 if casambi else 1)

if __name__ == "__main__":
    main()
