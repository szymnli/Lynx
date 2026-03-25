import json

from core.config import LOG_FILE


class Logger:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file

    def log_alert(self, alert):
        """Write an alert to the log file."""
        with open(self.log_file, "a") as f:
            json.dump(alert.to_dict(), f, indent=4)
            f.write("\n")

    def read_logs(self):
        """Read all alerts from the log file."""
        try:
            with open(self.log_file, "r") as f:
                return [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            return []
