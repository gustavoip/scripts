import dataclasses
import re
import shutil
import subprocess
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


def toggle():
    displays = get_displays()
    for display in displays:
        match display.model:
            case "DELL S2721DS":
                match display.current_input_source:
                    case InputSourceS2721DS.HDMI_1.value:
                        set_new_input_source(display, InputSourceS2721DS.HDMI_2.value)
                        print(f"Switching {display.model} to HDMI_2")

                    case InputSourceS2721DS.HDMI_2.value:
                        set_new_input_source(display, InputSourceS2721DS.HDMI_1.value)
                        print(f"Switching {display.model} to HDMI_1")

            case "DELL P2715Q":
                match display.current_input_source:
                    case InputSourceP2715Q.DP.value:
                        set_new_input_source(display, InputSourceP2715Q.HDMI.value)
                        print(f"Switching {display.model} to DP")

                    case InputSourceP2715Q.HDMI.value:
                        set_new_input_source(display, InputSourceP2715Q.DP.value)
                        print(f"Switching {display.model} to HDMI")
                    case None:
                        print(f"Skipping {display.model} because it's off")


if __name__ == "__main__":
    toggle()
