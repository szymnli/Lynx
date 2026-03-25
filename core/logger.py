import datetime
import json

from core.config import LOG_FILE


class Log:
    def __init__(self, severity, event_type, location, details):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.severity = severity  # LOW / MEDIUM / HIGH / CRITICAL
        self.event_type = event_type  # CREATE / DELETE / MODIFY / DELETE_SELF / ...
        self.location = location
        self.details = details

    def to_dict(self):
        """Convert the log entry to a dictionary."""
        return {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "event_type": self.event_type,
            "location": self.location,
            "details": self.details,
        }


class Logger:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file

    def log(self, severity, event_type, location, details):
        """Log an event to the log file."""
        entry = Log(severity, event_type, location, details)
        with open(self.log_file, "a") as f:
            json.dump(entry.to_dict(), f, indent=4)
            f.write("\n")
        return entry

    def log_baseline_checkpoint(self, baseline_path):
        """Log a baseline checkpoint event to the log file."""
        self.log(
            severity="LOW",
            event_type="BASELINE_CHECKPOINT",
            location=baseline_path,
            details="Created a baseline checkpoint",
        )

    def read_logs(self):
        """Read all logs from the log file."""
        try:
            with open(self.log_file, "r") as f:
                return [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            return []
