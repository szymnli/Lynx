# Lynx

A Python daemon that watches your Linux system for signs of compromise. File changes, suspicious processes, sudo abuse. All logged and alerted on in real time.

Work in progress.

## What works

**File integrity** — SHA-256 baselines for critical paths (`/etc/passwd`, `/etc/sudoers`, `/bin/`, etc.), with inotify watching for changes live. Modifications to baselined files come out as CRITICAL. Run `-b` once to build the baseline before starting.

**Process monitoring** — `/proc` polling to catch new processes, deleted-binary detection and SUID binary diffing against a startup baseline.

**User monitoring** — real-time `journalctl` streaming to catch sudo failures, with a configurable window and threshold for brute-force detection. Sudoers file changes are caught via inotify on `/etc/`.

**Alert routing** — JSON log for everything, console output for HIGH+, desktop notifications for CRITICAL events.

**CLI** — `--logs` for viewing recent alerts with optional count and severity filtering, `--help` for usage info.

## What's not done yet

- systemd service file
- Rootkit detection

## Usage

```bash
git clone https://github.com/szymnli/lynx.git
cd lynx
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo venv/bin/python lynx.py -b
sudo venv/bin/python lynx.py
```

Needs root to read other users' `/proc` entries and stream from journald.

## CLI reference

| Flag | Description |
|------|-------------|
| `-b`, `--baseline` | Build a fresh SHA-256 baseline of watched files. Run once before starting. |
| `-l [N]`, `--logs [N]` | Show last N alerts from the log (default: 20). |
| `-s LEVEL`, `--severity LEVEL` | Use with `--logs` to filter by severity: LOW, MEDIUM, HIGH, CRITICAL. |
| `-h`, `--help` | Show usage information. |

**Examples:**

```bash
sudo venv/bin/python lynx.py -l
sudo venv/bin/python lynx.py -l 50
sudo venv/bin/python lynx.py -l --severity CRITICAL
sudo venv/bin/python lynx.py -l 50 -s HIGH
```
