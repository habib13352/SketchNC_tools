 # 🛠️ SketchNC Tools

A collection of utility scripts and automated testing tools for the [SketchNC (repo comming soon) a low-cost CNC plotter project, built on ESP32 and powered by FluidNC.

This repository provides modular utilities to simplify diagnostics, motion testing, and future automation tasks for the SketchNC platform.

---

## 📦 Included Tools

### ✅ `motion_test.py` — Jog Motion Tester

This script sends continuous or repeated jog commands to the SketchNC machine via FluidNC serial interface. It is ideal for verifying motion smoothness, feedrate accuracy, and mechanical consistency of the X/Y axis.

#### 🔧 Features:
- Jog either **X** or **Y** axis
- Supports:
  - Custom jog distances (in inches)
  - Speed scaling as % of max feedrate
  - Fixed or infinite number of cycles (use 0 for infite still needs testing)
- Detects FluidNC boot state and unlocks the machine
- Waits for motion to complete between jogs
- Clean logs of commands and status
- Handles `Ctrl+C` to safely stop jogs

#### 🧪 Usage Example:
```bash
python motion_test.py --port COM3 --axis X --distance 1.0 --speed 50 --cycles 5

