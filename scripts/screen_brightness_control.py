#!/usr/bin/python3

import datetime
import os
import re
import shutil
import subprocess
import sys

_XRANDR_PATH = shutil.which("xrandr")
_DEVICES_REGEX = re.compile(r" - Device: (.*)\n")
_PROPERTIES_REGEX = re.compile(r"(?P<key>[^ ,]{1,20})=(?P<value>[^, \n\t]{1,20})")


def get_monitors():
    output = subprocess.check_output([_XRANDR_PATH], env=get_env_vars()).decode()
    return [Monitor(x.split()[0]) for x in output.split("\n") if " connected" in x]


class Monitor:
    def __init__(self, name):
        self.name = name

    def set_brightness(self, intensity):
        set_brightness(self.name, round(intensity, 3))


def get_scheduled_brightness():
    now = datetime.datetime.now()
    hour = now.hour + now.minute / 60

    if 4.5 < hour < 15:
        return 1
    #  gracefully decaying the light intensity
    elif 15 < hour < 20:
        p = _get_relative_progress(start=15, end=19.5, current=hour)
        return max(1 - (0.1 ** (1 - p)) * p, 0.55)
    else:
        return 0.35


def set_brightness(path, percentage_value):
    assert 0.1 <= percentage_value <= 1
    subprocess.check_output(
        [_XRANDR_PATH, "--output", path, "--brightness", str(percentage_value)],
        env=get_env_vars(),
    )


def _get_relative_progress(start, end, current):
    assert current <= end
    percentage = (current - start) / (end - start)
    assert 0 <= percentage <= 1
    return percentage


def get_env_vars():
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    return env


if __name__ == "__main__":
    value = float(sys.argv[1]) if len(sys.argv) == 2 else get_scheduled_brightness()
    monitors = get_monitors()
    for monitor in monitors:
        try:
            monitor.set_brightness(value)
        except Exception as e:
            print(f"[{type(e).__name__}] Error setting brightness={value} for {monitor.name}")
        else:
            print(f"{monitor.name}'s brightness set to {value}%")
