# Disk Scheduling Algorithm Visualizer

A Python simulator that compares **FCFS, SSTF, SCAN and C-SCAN** disk scheduling.
It prints a results table and shows an animated head-movement chart for each algorithm,
plus a bar chart comparing total seek distance.

## Requirements (Ubuntu 22.04 / 24.04)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tk git
```

## Setup

```bash
git clone <your-repo-url>
cd disk-scheduling-visualizer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

No compilation is needed (Python is interpreted).

## Run

```bash
# Default textbook example (head 53, 200 cylinders), opens the animation window
python3 disk_scheduler.py

# Custom input
python3 disk_scheduler.py -r 98 183 37 122 14 124 65 67 -H 53 -s 200 -d up

# Head moving towards lower cylinders first
python3 disk_scheduler.py -d down

# Do not count the C-SCAN return sweep
python3 disk_scheduler.py --no-jump-count

# Terminal table only (no window)
python3 disk_scheduler.py --no-gui

# Save the final chart as an image (works without a display)
python3 disk_scheduler.py --save result.png --no-gui
```

| Option | Meaning | Default |
|---|---|---|
| `-r, --requests` | Request queue (cylinder numbers) | 98 183 37 122 14 124 65 67 |
| `-H, --head` | Initial head position | 53 |
| `-s, --size` | Total cylinders (0 to size-1) | 200 |
| `-d, --direction` | `up` or `down` (SCAN, C-SCAN) | up |
| `--no-jump-count` | Exclude the C-SCAN return sweep from the total | off |
| `--no-gui` | Print the table only | off |
| `--save FILE.png` | Save the final chart | none |

## Test

```bash
python3 -m unittest -v
```

Expected for the default example: FCFS 640, SSTF 236, SCAN 331, C-SCAN 382.

## Design

- `disk_scheduler.py`: algorithm functions (`fcfs`, `sstf`, `scan`, `cscan`), metrics (`total_seek`), CLI and matplotlib visualization.
- `test_disk_scheduler.py`: unit tests (textbook values, direction, edge cases, duplicates).

Assumptions: SCAN and C-SCAN travel to the disk edge before reversing or returning (classic versions).
If no requests lie behind the head, SCAN stops after the last request.

## Troubleshooting

- Window does not open over SSH or WSL: use `--save result.png --no-gui`, or install `python3-tk` and run on the desktop.
- `ModuleNotFoundError: matplotlib`: activate the venv and run `pip install -r requirements.txt`.
