import serial
import time
import argparse

AXIS_MAX_FEEDRATE = {
    'X': 2000,
    'Y': 2000
}

def inches_to_mm(inches):
    return inches * 25.4

def generate_jog_pair(axis, distance_inches, speed_percent):
    distance_mm = inches_to_mm(distance_inches)
    max_feedrate = AXIS_MAX_FEEDRATE[axis.upper()]
    feedrate = max_feedrate * (speed_percent / 100)

    forward = f"$J=G91 G21 F{feedrate:.0f} {axis.upper()}{distance_mm:.3f}"
    backward = f"$J=G91 G21 F{feedrate:.0f} {axis.upper()}-{distance_mm:.3f}"
    return forward, backward

def wait_for_idle(ser, timeout=10):
    start = time.time()
    printed = False
    while time.time() - start < timeout:
        ser.write(b"?\n")
        time.sleep(0.25)
        while ser.in_waiting:
            status = ser.readline().decode(errors='ignore').strip()
            if not printed and "<Jog" in status:
                print("⏳ Jogging...")
                printed = True
            if "Idle" in status:
                print("✅ Jog complete.\n")
                return True
    print("⚠️ Timeout waiting for Idle")
    return False

def send_and_log(ser, cmd):
    ser.write((cmd + '\n').encode())
    print(f">> {cmd}")
    time.sleep(0.25)
    while ser.in_waiting:
        response = ser.readline().decode(errors='ignore').strip()
        if response and not response.startswith("<") and response != "ok":
            print(f"<< {response}")

def send_jog_commands(port, baudrate, axis, distance_inches, speed_percent, cycles):
    print(f"🔌 Connecting to {port} at {baudrate} baud...")
    with serial.Serial(port, baudrate, timeout=2) as ser:
        time.sleep(0.5)
        print("⏳ Waiting for FluidNC to fully boot...\n")

        booted = False
        timeout = time.time() + 10
        while time.time() < timeout:
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                if "FluidNC" in line:
                    print(f"<< {line}")
                    booted = True
            else:
                time.sleep(0.2)

        if not booted:
            print("⚠️ FluidNC did not boot. Power cycle and try again.")
            return

        time.sleep(2)
        while ser.in_waiting:
            _ = ser.readline()

        send_and_log(ser, "$X")
        print("✅ Machine unlocked.\n")

        if cycles == 0:
            print("⏳ Giving FluidNC a moment before starting loop...\n")
            time.sleep(2)

        forward, backward = generate_jog_pair(axis, distance_inches, speed_percent)

        try:
            if cycles == 0:
                print("🔁 Looping infinitely. Press Ctrl+C to stop.\n")
                cycle = 1
                while True:
                    print(f"▶️ Cycle {cycle}:")
                    send_and_log(ser, forward)
                    wait_for_idle(ser)
                    send_and_log(ser, backward)
                    wait_for_idle(ser)
                    cycle += 1
            else:
                for cycle in range(1, cycles + 1):
                    print(f"▶️ Cycle {cycle}:")
                    send_and_log(ser, forward)
                    wait_for_idle(ser)
                    send_and_log(ser, backward)
                    wait_for_idle(ser)
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user. Exiting gracefully...")

# === Entry Point ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SketchNC Jog Motion Tester")
    parser.add_argument("--port", type=str, default="COM3", help="Serial COM port (e.g., COM3)")
    parser.add_argument("--axis", type=str, choices=["X", "Y"], required=True, help="Axis to jog")
    parser.add_argument("--distance", type=float, required=True, help="Jog distance (in inches)")
    parser.add_argument("--speed", type=int, default=50, help="Speed percentage (0–100%)")
    parser.add_argument("--cycles", type=int, default=0, help="Number of full back-forth cycles (0 = infinite)")

    args = parser.parse_args()

    send_jog_commands(
        port=args.port,
        baudrate=115200,
        axis=args.axis,
        distance_inches=args.distance,
        speed_percent=args.speed,
        cycles=args.cycles
    )
