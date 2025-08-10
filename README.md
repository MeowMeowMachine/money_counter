# Money Counter

A lightweight Python utility that displays a tiny, always-on-top window—a single borderless "box"—showing your **real-time earnings**, **progress toward a goal**, and **worked time**.

Designed to be unobtrusive and highly configurable, it features:

- **Global hotkeys** for quick control
- **Sound notifications** with priority handling
- **Periodic re-assertion** of the always-on-top state, ensuring visibility even when other apps open

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration (Brief)](#configuration-brief)
- [How It Works (Technical Details)](#how-it-works-technical-details)
- [Controls & Hotkeys](#controls--hotkeys)
- [Sound / Priority Rules](#sound--priority-rules)
- [Data Storage (`progress.csv`) Format](#data-storage-progresscsv-format)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Tips & Best Practices](#tips--best-practices)
- [License](#license)

---

## Features

- **Minimal borderless window**—the window *is* the box
- **Real-time earnings** calculated from hourly income
- **Always-on-top** mode with periodic re-assertion
- **Global hotkeys** (start/pause, save & exit, emergency exit)
- **Sound notifications** with priority rules (no queueing; higher-priority interrupts)
- **Progress saved** to `progress.csv` (timestamped)
- **Configurable** via `config.json` (appearance & behavior)

---

## Requirements

- **Python 3.8+**
- **Required packages:**
    ```bash
    pip install pygame keyboard PySDL2
    ```

> **Windows Notes:**
> - `keyboard` may require Administrator privileges for global hotkeys.
> - Always-on-top uses Win32 (`SetWindowPos`) and optionally PySDL2; safe fallbacks are included.

---

## Installation

1. Clone or copy the project folder.
2. Ensure `main.py` and `config.json` are at the project root.
3. Place `.wav` sound files (if used) in a `sounds/` folder and reference them in `config.json`.
4. Install dependencies:
     ```bash
     pip install pygame keyboard PySDL2
     ```

---

## Quick Start

1. Edit `config.json` (see example below) to change currency, income, keys, colors, fonts, or goal.
2. Run:
     ```bash
     python main.py
     ```
3. The tiny box window appears. Press your start key (**default: `F7`**) to begin/pause tracking.
     - **`F12`** (default): Save progress & exit
     - **Emergency exit:** `CTRL + AltGr`

---

## Configuration (Brief)

`config.json` controls the program. Default values are used for missing keys.

**Common settings:**

- `currency`: Currency symbol (e.g., `"EUR"`)
- `income`: Hourly rate (number)
- `goal`: Target amount
- `Keys`: Hotkey mapping (`StartStopSession`, `SaveProgress`)
- `GUI.Formatting`: `Color` (hex), `Font`, `FontSize`
- `GUI.Layout`: `Width`, `Height`, `PositionX`, `PositionY`, `Title`, `Overlapping`
- `Sounds`: File paths & trigger thresholds

**Minimal Example:**
```json
{
    "currency": "EUR",
    "income": 15,
    "goal": 3100,
    "Keys": {
        "StartStopSession": "F7",
        "SaveProgress": "F12"
    },
    "GUI": {
        "Formatting": {
            "Color": "#777d77",
            "Font": "Arial",
            "FontSize": 36
        },
        "Layout": {
            "Width": 400,
            "Height": 200,
            "PositionX": 0,
            "PositionY": 20,
            "Title": "Money Counter",
            "Overlapping": true
        }
    }
}
```

---

## How It Works (Technical Details)

### Window Creation

- Creates a **Pygame** window sized per config
- Borderless—just the box

### Always-on-Top

- On Windows, uses Win32 API `SetWindowPos` with `HWND_TOPMOST`
- Periodically re-asserts topmost status (configurable interval) without stealing focus

### Positioning

- Sets `SDL_VIDEO_WINDOW_POS` before `pygame.init()` for initial position
- Calls `SetWindowPos` after creation and periodically if overlapping mode is enabled

### Key Handling

- Global keys polled with **rising-edge detection** for reliable short presses
- Avoids blocking sleeps for responsiveness

### Sound Handling

- Uses `pygame.mixer` with a **priority model**:
    - **High priority** (`evenmoredollars`): interrupts and plays immediately
    - **Normal priority** (`dollar`): plays only if no higher-priority sound is active
    - **No queuing**: skipped if higher-priority sound plays

### Saving

- `SaveProgress` appends to `progress.csv`:
    - Timestamp
    - Cumulative progress
    - Time worked (H M)
    - Money earned this session
    - Remaining to goal
    - Percentage complete

---

## Controls & Hotkeys

| Action                | Default Key         |
|-----------------------|--------------------|
| Start / Pause         | `F7` (toggle)      |
| Save progress & exit  | `F12`              |
| Emergency exit        | `CTRL + AltGr`     | ! <Exiting> is only possible via keybind or stopping script due to internal logic > !

*Hotkeys are configurable in `config.json`.*

---

## Sound / Priority Rules

- **High priority**: `evenmoredollars`—interrupts and plays immediately
- **Normal priority**: `dollar`—plays only if nothing is playing
- **No queuing**: lower-priority sounds are skipped if a higher-priority one is playing

Place `.wav` files in `sounds/` and reference them in `config.json`.

---

## Data Storage (`progress.csv`) Format

When saving, the program appends a CSV row.

**Header:**
```text
date,progress,time,made,remaining,percentage
```
**Fields:**

- `date`: Timestamp (e.g., `08/10/2025 1:23 PM`)
- `progress`: Cumulative total saved
- `time`: Worked time (`HHH H MM M`)
- `made`: Money earned this session
- `remaining`: Goal minus progress
- `percentage`: `(progress / goal) * 100` (rounded/formatted)

**Example:**
```text
08/10/2025 1:23 PM,123.45,2H 15M,30.00,2976.55,3.98
```

---

## Troubleshooting & FAQ

### F7 (start key) sometimes doesn't react

- **Cause:** Blocking sleeps can miss presses
- **Fix:** Use non-blocking debounce; avoid `time.sleep()` inside the loop
- **Tip:** Run as administrator (Windows) for reliable keyboard hooks

### Window won't stay on top

- **Solution:** Reduce re-assert interval (e.g., `0.5s`) in config
- **Note:** Very short intervals may cause flicker; tune for your environment

### Close button / window unresponsive

- **Advice:** Avoid wrapping the native Pygame window in an SDL wrapper unless handling SDL events
- **Tip:** Use native Win32 calls for positioning and avoid interfering with native event handling

### Sounds not playing or queueing

- **Check:** Verify `.wav` file paths
- **Format:** Use uncompressed PCM `.wav` files for best compatibility
- **Note:** Lower-priority sounds are skipped by design—no queueing


## Small Notes
- This is a small program, not aimed to be a full-fledged application.
- It may have limitations and bugs; use at your own risk.
- I made this in my free time for personal uses. The code very well may not work on your end.
---
