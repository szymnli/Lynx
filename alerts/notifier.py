class Notifier:
    def __init__(self, logger):
        self.logger = logger

    def notify(self, alert):
        """Notify the user of the alert."""
        self.logger.log_alert(alert)  # always

        if alert.severity in ("HIGH", "CRITICAL"):
            print(alert.summary())  # console

        if alert.severity == "CRITICAL":
            self._desktop_notify(alert)  # libnotify

    def _desktop_notify(self, alert):
        """Send a desktop notification for the alert."""
        # notify2 / plyer call goes here
        ...
