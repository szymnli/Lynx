import os

import yaml
from inotify_simple import INotify, flags

# Load configuration from config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Get the list of directories to monitor from the config
MONITORING_DIRS = config["monitoring"]["directories"]


def main():
    print(r"""
        __
       ╱╲ ╲
       ╲ ╲ ╲      __  __    ___    __  _
        ╲ ╲ ╲  __╱╲ ╲╱╲ ╲ ╱' _ `╲ ╱╲ ╲╱'╲
         ╲ ╲ ╲L╲ ╲ ╲ ╲_╲ ╲╱╲ ╲╱╲ ╲╲╱>  <╱
          ╲ ╲____╱╲╱`____ ╲ ╲_╲ ╲_╲╱╲_╱╲_╲
           ╲╱___╱  `╱___╱> ╲╱_╱╲╱_╱╲╱╱╲╱_╱
                      ╱╲___╱
                      ╲╱__╱
        """)

    print("Initiating monitoring...")
    inotify = INotify()
    # Define watch flags (CREATE, DELETE, MODIFY, DELETE_SELF)
    watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF
    wd_to_path = {}
    # Initialize inotify watches for each directory
    for dir in MONITORING_DIRS:
        # Walk through the directory and add watches for each subdirectory
        for root, dirs, files in os.walk(dir, topdown=True):
            wd = inotify.add_watch(root, watch_flags)
            wd_to_path[wd] = root

    while True:
        try:
            # Read events from inotify and process them
            events = inotify.read()
            for event in events:
                # Print event details
                flag_names = [f.name for f in flags.from_mask(event.mask)]
                print(
                    f"  - {', '.join(flag_names)} on '{event.name}' | full path: {wd_to_path[event.wd]}/{event.name}"
                )

                # Watch new directories automatically
                if "CREATE" in flag_names and event.mask & flags.ISDIR:
                    path = os.path.join(wd_to_path[event.wd], event.name)
                    wd = inotify.add_watch(path, watch_flags)
                    wd_to_path[wd] = path
                    print(f"Watching new directory: '{path}'")

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
