import datetime


class Alert:
    def __init__(self, severity, event_type, location, source, context=None):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.severity = severity  # LOW / MEDIUM / HIGH / CRITICAL
        self.event_type = event_type  # CREATE / DELETE / MODIFY / DELETE_SELF / ...
        self.location = location
        self.source = source  # which monitor raised this
        self.context = context or {}

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "event_type": self.event_type,
            "location": self.location,
            "source": self.source,
            "context": self.context,
        }

    def summary(self):
        return f"[{self.severity}] {self.source}: {self.event_type} on {self.location}"
