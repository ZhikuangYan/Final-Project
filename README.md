# 🎮 2D Platformer Game

*A simple platform game built with Python & Pygame.*

---

# 📌 Project Overview

This is a 2D platformer game built with **Python + Pygame**.
The player can move, jump, collect coins, break blocks, avoid enemies, and reach the goal to complete the level.

---

# ✨ Features

### ✔ Platforms

* Regular terrain blocks
* Floating platforms
* Breakable bricks (can be destroyed by hitting from below)

### ✔ Enemies

* Moves automatically left and right
* Turns around when hitting walls or platform edges
* Player takes damage upon contact (includes invincibility period)

### ✔ Player

* Move left/right with A/D
* Jump with Space
* Collision detection + gravity system
* Three-heart health system (Heart UI)
* Falling off the map results in death

### ✔ Level System

* Load maps from `.txt` files
* Support unlimited horizontal scrolling (horizontal camera offset)
* Coin system and score calculation
* Level completion screen / death screen

### ✔ Sprites / Tiles

* Player animations (Idle / Run / Jump / Fall)
* Slime enemy animations (Idle)
* Grass, platforms, bricks, coins, flag endpoints
* Custom sky background colors

---

# 🎮 Controls

| 按键        | 功能           |
| --------- | ------------ |
| **A / D** | Move left / right      |
| **SPACE** | jump           |
| **R**     | Restart the level after death or completion |
  | **ESC**   | Quit game         |

---

# 🗂 Project Structure

```
/project_root
│
├── main.py             
├── level1.txt             
├── assets/
│   ├── Background/
│   │   └── Blue.png
│   ├── Enemy/
│   │   └── Slime/idle.png
│   ├── Items/coin.png
│   ├── UI/
│   │   ├── heart_full.png
│   │   ├── heart_empty.png
│   │   └── goal.png
│   └── MainCharacters/
│       └── PinkMan/*.png
│
└── README.md
```

---

# 🧱 Level Format

Levels are defined by `.txt` files:

```
............................
............................
..............C.............
.............PPP............
....C...................G...
############################
```

| 字符  | 功能           |
| --- | ------------ |
| `#` | Grass |
| `P` | Platform |
| `B` | breakable block |
| `C` | Coin |
| `E` | Enemy |
| `G` | Goal |
| `.` | blank |

---

# 🏁 How to Run

install pygame：

```bash
pip install pygame
```

run：

```bash
python main.py
```

---
