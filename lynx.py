import os
import sys
from collections import defaultdict

from alerts.notifier import Notifier
from core.config import BASELINE_PATH, INTEGRITY_DIRS
from core.logger import Logger
from monitors.file_integrity import (
    build_baseline,
    cleanup,
    compare_baseline,
    handle_events,
    save_baseline,
    start_monitoring,
)
from monitors.processes import (
    build_suid_baseline,
    check_deleted_binaries,
    check_new_processes,
    check_suid_binaries,
    get_process_snapshot,
)
from monitors.user import (
    check_sudo_failures,
    read_new_lines,
    start_journal_stream,
)

HEADER = r"""
        __
       ╱╲ ╲
       ╲ ╲ ╲      __  __    ___    __  _
        ╲ ╲ ╲  __╱╲ ╲╱╲ ╲ ╱' _ `╲ ╱╲ ╲╱'╲
         ╲ ╲ ╲_╲ ╲ ╲ ╲_╲ ╲╱╲ ╲╱╲ ╲╲╱>  <╱
          ╲ ╲____╱╲╱`____ ╲ ╲_╲ ╲_╲╱╲_╱╲_╲
           ╲╱___╱  `╱___╱  ╲╱_╱╲╱_╱╲╱╱╲╱_╱
                      ╱╲___╱
                      ╲╱__╱
    """

VALID_SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def cmd_baseline(notifier):
    try:
        os.mkdir("data")
        os.mkdir("logs")
    except OSError:
        pass
    print("Building baseline...")
    baseline = build_baseline()
    save_baseline(notifier, baseline)
    print("Baseline saved.")
    sys.exit(0)


def cmd_logs(logger):
    N = 20
    try:
        N = int(sys.argv[2])
    except (ValueError, IndexError):
        pass

    severity = None
    if "--severity" in sys.argv or "-s" in sys.argv:
        idx = (
            sys.argv.index("--severity")
            if "--severity" in sys.argv
            else sys.argv.index("-s")
        )
        try:
            severity = sys.argv[idx + 1]
        except IndexError:
            print("No severity value provided.")
            sys.exit(1)
        if severity not in VALID_SEVERITIES:
            print(f"Invalid severity. Choose from {VALID_SEVERITIES}")
            sys.exit(1)

    for log in logger.filter_logs(N, severity):
        print(
            f"[{log['timestamp']}] [{log['severity']}] {log['source']}: {log['event_type']} on {log['location']}"
        )
    sys.exit(0)


def cmd_help():
    print("""
Usage: sudo venv/bin/python lynx.py [option]

Options:
  -b, --baseline              Build a fresh SHA-256 baseline of watched files. Run once before starting.
  -l, --logs [N]              Show last N alerts from the log (default: 20).
      -s, --severity LEVEL    Filter logs by severity: LOW, MEDIUM, HIGH, CRITICAL.
  -h, --help                  Show this message.

Examples:
  sudo venv/bin/python lynx.py -b
  sudo venv/bin/python lynx.py -l
  sudo venv/bin/python lynx.py -l 50
  sudo venv/bin/python lynx.py -l --severity CRITICAL
  sudo venv/bin/python lynx.py -l 50 -s HIGH
    """)
    sys.exit(0)


def parse_args(logger, notifier):
    if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h"):
        cmd_help()
    elif len(sys.argv) == 2 and sys.argv[1] in ("--baseline", "-b"):
        cmd_baseline(notifier)
    elif len(sys.argv) >= 2 and sys.argv[1] in ("--logs", "-l"):
        cmd_logs(logger)
    elif len(sys.argv) > 1:
        print(
            "Invalid argument. Use --baseline or -b to build a baseline or no arguments to start monitoring."
        )
        sys.exit(1)
    elif not os.path.exists(BASELINE_PATH):
        print("Baseline file not found. Use --baseline or -b to build a baseline.")
        sys.exit(1)


def setup(notifier):
    print("Comparing baseline...")
    baseline = compare_baseline()
    print("Baseline comparison complete.")

    print("Initiating monitoring...")
    inotify, wd_to_path, watch_flags = start_monitoring()

    print("Taking process snapshot...")
    old_snapshot = get_process_snapshot()
    suid_baseline = build_suid_baseline(INTEGRITY_DIRS)
    print("Process snapshot taken.")

    print("Starting journal stream...")
    journal_stream = start_journal_stream()
    failure_tracker = defaultdict(list)
    print("User monitor online.")

    return (
        baseline,
        inotify,
        wd_to_path,
        watch_flags,
        old_snapshot,
        suid_baseline,
        journal_stream,
        failure_tracker,
    )


def monitor_loop(
    notifier,
    baseline,
    inotify,
    wd_to_path,
    watch_flags,
    old_snapshot,
    suid_baseline,
    journal_stream,
    failure_tracker,
):
    while True:
        try:
            handle_events(notifier, inotify, wd_to_path, watch_flags, baseline)

            new_lines = read_new_lines(journal_stream)
            check_sudo_failures(new_lines, failure_tracker, notifier)

            new_snapshot = get_process_snapshot()
            check_new_processes(old_snapshot, new_snapshot, notifier)
            check_deleted_binaries(new_snapshot, notifier)
            check_suid_binaries(suid_baseline, INTEGRITY_DIRS, notifier)
            old_snapshot = new_snapshot
        except KeyboardInterrupt:
            print("\nExiting...")
            cleanup(inotify, wd_to_path)
            break


def main():
    logger = Logger()
    notifier = Notifier(logger)

    parse_args(logger, notifier)

    print(HEADER)
    (
        baseline,
        inotify,
        wd_to_path,
        watch_flags,
        old_snapshot,
        suid_baseline,
        journal_stream,
        failure_tracker,
    ) = setup(notifier)
    monitor_loop(
        notifier,
        baseline,
        inotify,
        wd_to_path,
        watch_flags,
        old_snapshot,
        suid_baseline,
        journal_stream,
        failure_tracker,
    )


if __name__ == "__main__":
    main()
