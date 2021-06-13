#!/usr/bin/python3

import dataclasses
import datetime
import os
import shutil
import subprocess
import sys
import time

_XRANDR_PATH = shutil.which("xrandr")


def get_monitors():
    output = subprocess.check_output([_XRANDR_PATH], env=get_environ_with_display_var()).decode()
    return [Screen(x.split()[0]) for x in output.split("\n") if " connected" in x]


@dataclasses.dataclass
class Screen:
    name: str


def get_scheduled_brightness():
    now = datetime.datetime.now()
    hour = now.hour + now.minute / 60

    if 4.5 < hour < 15:
        return 1
    #  gracefully decaying the light intensity
    elif 15 <= hour < 19.5:
        p = get_relative_progress(start=15, end=19.5, current=hour)
        return max(1 - (0.1 ** (1 - p)) * p, 0.25)
    else:
        return 0.15


def set_brightness(screen: Screen, percentage_value):
    assert 0.1 <= percentage_value <= 1
    percentage_value = round(percentage_value, 3)
    subprocess.check_output(
        [_XRANDR_PATH, "--output", screen.name, "--brightness", str(percentage_value)],
        env=get_environ_with_display_var(),
    )


def get_relative_progress(start, end, current):
    assert current <= end
    percentage = (current - start) / (end - start)
    assert 0 <= percentage <= 1
    return percentage


def get_environ_with_display_var():
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    return env


if __name__ == "__main__":
    value = float(sys.argv[1]) if len(sys.argv) == 2 else get_scheduled_brightness()
    screens = get_monitors()
    for screen in screens:
        try:
            set_brightness(screen, value)
            time.sleep(0.5)
        except Exception as e:
            print(f"[{type(e).__name__}] Error setting brightness={value} for {screen.name}")
        else:
            print(f"{screen.name}'s brightness set to {100*value}%")
