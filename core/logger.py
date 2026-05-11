import json

from core.config import LOG_FILE


class Logger:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file

    def log_alert(self, alert):
        """Write an alert to the log file."""
        with open(self.log_file, "a") as f:
            json.dump(alert.to_dict(), f)
            f.write("\n")

    def read_logs(self):
        """Read all alerts from the log file."""
        try:
            with open(self.log_file, "r") as f:
                return [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def filter_logs(self, n=20, severity=None):
        logs = self.read_logs()
        if severity:
            logs = [log for log in logs if log["severity"] == severity]
        return list(reversed(logs[-n:]))
