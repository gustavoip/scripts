import dataclasses
import os
import re
import shutil
import subprocess
import sys
from enum import Enum
from typing import List, Optional

_DDCUTIL_EXECUTABLE = shutil.which("ddcutil")

_INPUT_SOURCE_PARAM = {
    "DELL S2721DS": "0x60",
    "DELL P2715Q": "0x60",
}

_I2C_BUS_REGEX = re.compile(r"I2C bus:.*?i2c-(?P<bus>\d+)")
_MODEL_REGEX = re.compile(r"Model:(?P<model>.*)")


class InputSourceS2721DS(Enum):
    HDMI_1 = "0x11"
    HDMI_2 = "0x12"


class InputSourceP2715Q(Enum):
    DP = "0x0f"
    HDMI = "0x11"


@dataclasses.dataclass
class Display:
    model: str
    bus: str
    current_input_source: Optional[str]


def get_displays() -> List[Display]:
    output = _check_output([_DDCUTIL_EXECUTABLE, "detect"]).strip()
    models = [s.strip() for s in _MODEL_REGEX.findall(output)]
    busses = _I2C_BUS_REGEX.findall(output)

    displays = []
    for model, bus in zip(models, busses):
        if model:
            display = Display(model, bus, _get_input_source(model, bus))
            displays.append(display)
    return displays


def _get_input_source(model: str, bus: str) -> Optional[str]:
    param = _INPUT_SOURCE_PARAM[model]
    output = _check_output([_DDCUTIL_EXECUTABLE, "--bus", bus, "getvcp", param])
    if "Invalid response" in output:
        return None
    return re.compile(f"sl=(.*)\\)").findall(output)[0]


def set_new_input_source(display: Display, source: str):
    param = _INPUT_SOURCE_PARAM[display.model]
    _check_output(
        [_DDCUTIL_EXECUTABLE, "setvcp", "--bus", display.bus, param, source]
    )


def _check_output(command):
    print(command)
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        result = str(e.output)

    return result


def to_work(display: List[Display]):
    for d in display:
        if d.model == "DELL S2721DS":
            set_new_input_source(d, InputSourceS2721DS.HDMI_2.value)
            print(f"Switching {d.model} to HDMI_2")
        elif d.model == "DELL P2715Q":
            set_new_input_source(d, InputSourceP2715Q.HDMI.value)
            print(f"Switching {d.model} to HDMI")


def to_home(display: List[Display]):
    for d in display:
        if d.model == "DELL S2721DS":
            set_new_input_source(d, InputSourceS2721DS.HDMI_1.value)
            print(f"Switching {d.model} to HDMI_1")
        elif d.model == "DELL P2715Q":
            set_new_input_source(d, InputSourceP2715Q.DP.value)
            print(f"Switching {d.model} to DP")


def set_config(profile):
    displays = get_displays()
    if profile.lower() in ("gustavoip", "home"):
        to_home(displays)
    if profile.lower() == "work":
        to_work(displays)


if __name__ == "__main__":
    set_config(str(sys.argv[1]) if len(sys.argv) == 2 else os.getlogin())
