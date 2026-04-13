# 🎮 2D Platformer Game

*Final project for Software Carpentry: A simple platformer game built with Python & Pygame.*

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

| Button        | fearures           |
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
.............PBP............
....E....P..............G...
############################
```

| Character  | features           |
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

# 🏁 DEMO
![图片1](https://github.com/user-attachments/assets/ae2b68cb-fab1-4642-8464-fe783468c57b)

---
## Assets Attribution
Game assets are sourced from:

- Tech With Tim — Python Platformer (code structure inspiration)  
  https://github.com/techwithtim/Python-Platformer  

- 小苏造水（Xiaosuzaoshui） — Pixel Art Packs  
  https://xiaosuzaoshui.itch.io/pixel-art  
