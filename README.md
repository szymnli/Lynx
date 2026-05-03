# Lynx

A Python daemon that watches your Linux system for signs of compromise. File changes, suspicious processes, sudo abuse. ALl logged and alerted on in real time.

Work in progress.

## What works

**File integrity** — SHA-256 baselines for critical paths (`/etc/passwd`, `/etc/sudoers`, `/bin/`, etc.), with inotify watching for changes live. Modifications to baselined files come out as CRITICAL. Run `-b` once to build the baseline before starting.

**Process monitoring** — `/proc` polling to catch new processes, deleted-binary detection and SUID binary diffing against a startup baseline.

**User monitoring** — real-time `journalctl` streaming to catch sudo failures, with a configurable window and threshold for brute-force detection. Sudoers file changes are caught via inotify on `/etc/`.

**Alert routing** — JSON log for everything, console output for HIGH+, desktop notifications for CRITICAL (stubbed, not yet wired up).

## What's not done yet

- Working desktop notifications
- systemd service file
- `--logs` CLI flag for reading recent alerts without grepping raw JSON,
- deleted-binary whitelist in `config.yaml`
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
