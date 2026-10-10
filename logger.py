import os
from datetime import datetime

log_file = "logs.md"


def add_log(step, execution_time):
    """logs.md me ek row add karo."""
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(
                "# Execution Logs\n\n| Date & Time | Step | Time Taken"
                " |\n|---|---|---|\n"
            )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"| {now} | {step} | {execution_time:.2f} sec |\n")
