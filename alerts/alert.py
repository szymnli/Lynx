import datetime


class Alert:
    def __init__(self, severity, event_type, location, source, context=None):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.severity = severity  # LOW / MEDIUM / HIGH / CRITICAL
        self.event_type = event_type  # CREATE / DELETE / MODIFY / DELETE_SELF / ...
        self.location = location
        self.source = source  # Which monitor
        self.context = context or {}

    def to_dict(self):
        """Return a dictionary representation of the alert."""
        return {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "event_type": self.event_type,
            "location": self.location,
            "source": self.source,
            "context": self.context,
        }

    def summary(self):
        """Return a summary string of the alert."""
        return f"{self.severity} - {self.event_type} - {self.location} - {self.source}"
