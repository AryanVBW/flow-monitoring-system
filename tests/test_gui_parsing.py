#!/usr/bin/env python3
"""
Test script to verify GUI can parse Arduino data format
"""

def test_parse_data_line(line: str):
    """Test parsing of CSV data line"""
    try:
        parts = line.split(",")
        print(f"Line: {line}")
        print(f"Parts: {parts}")
        print(f"Number of parts: {len(parts)}")
        
        if len(parts) < 4:
            print("❌ Not enough parts")
            return

        timestamp_ms = float(parts[0])
        flow_rate = float(parts[1])
        total_volume = float(parts[2])
        status = parts[3].strip()
        
        # Extract debug info if available (new format includes pulse counts)
        current_pulses = int(parts[4]) if len(parts) > 4 else 0
        total_pulses = int(parts[5]) if len(parts) > 5 else 0

        print(f"✅ Parsed successfully:")
        print(f"  - Timestamp: {timestamp_ms} ms")
        print(f"  - Flow Rate: {flow_rate} L/min")
        print(f"  - Total Volume: {total_volume} L")
        print(f"  - Status: '{status}'")
        print(f"  - Current Pulses: {current_pulses}")
        print(f"  - Total Pulses: {total_pulses}")
        print()

    except (ValueError, IndexError) as e:
        print(f"❌ Failed to parse: {e}")
        print()

# Test with sample Arduino data
test_lines = [
    "1715,0.0000,0.00000,WAITING,0,0",
    "2717,0.0000,0.00000,WAITING,0,0",
    "3719,0.0000,0.00000,WAITING,0,0",
    "4721,1.2000,0.00020,CONNECTED,9,15",
    "5723,2.4000,0.00060,CONNECTED,18,33"
]

print("🧪 Testing GUI CSV parsing with Arduino data format:")
print("=" * 60)

for line in test_lines:
    test_parse_data_line(line)