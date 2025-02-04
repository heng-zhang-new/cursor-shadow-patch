import os
import re
import random
import shutil
import pathlib
import platform
from uuid import uuid4

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[96m"
PURPLE = "\033[95m"
RESET = "\033[0m"

REVERSE = "\033[7m"
NO_REVERSE = "\033[27m"


def pause():
    input(f"\n{REVERSE}Press Enter to continue...{NO_REVERSE}")


SYSTEM = platform.system()
if SYSTEM not in ("Windows", "Linux", "Darwin"):
    print(f"{RED}[ERR] Unsupported OS: {SYSTEM}{RESET}")
    pause()
    exit()
if SYSTEM == "Windows":
    # ANSI Support for OLD Windows
    os.system("color")


def uuid():
    return str(uuid4())


def path(path: str | pathlib.Path):
    return pathlib.Path(path).resolve()


def curbasepath():
    if SYSTEM == "Windows":
        localappdata = os.getenv("LOCALAPPDATA")
        assert localappdata, "Panicked: LOCALAPPDATA not exist"
        return path(localappdata) / "Programs" / "cursor" / "resources" / "app"
    elif SYSTEM == "Darwin":
        return path("/Applications/Cursor.app/Contents/Resources/app")
    elif SYSTEM == "Linux":
        bases = [
            path("/opt/Cursor/resources/app"),
            path("/usr/share/cursor/resources/app"),
        ]
        for base in bases:
            if base.exists():
                return base
        print(f"{RED}[ERR] Cursor base path not found, please specify{RESET}")
        pause()
        exit()
    else:
        assert None


def jspath(p: str):
    if not p:
        jspath = curbasepath() / "out" / "main.js"
        if not jspath.exists():
            print(f"{RED}[ERR] main.js not found in default path '{jspath}'{RESET}")
            pause()
            exit()
        print(f"{GREEN}[√]{RESET} {jspath}")
    else:
        jspath = path(p)
        if not jspath.exists():
            print(f"{RED}[ERR] File '{jspath}' not found{RESET}")
            pause()
            exit()
    return jspath


def randomuuid(randomuuid: str):
    if not randomuuid:
        randomuuid = uuid()
        print(randomuuid)
    return randomuuid


def macaddr(macaddr: str):
    if not macaddr:
        while not macaddr or macaddr in (
            "00:00:00:00:00:00",
            "ff:ff:ff:ff:ff:ff",
            "ac:de:48:00:11:22",
        ):
            macaddr = ":".join([f"{random.randint(0, 255):02X}" for _ in range(6)])
        print(macaddr)
    return macaddr


def load(path: pathlib.Path):
    with open(path, "rb") as f:
        return f.read()


def save(path: pathlib.Path, data: bytes):
    print(f"\n> Save {path}")
    try:
        with open(path, "wb") as f:
            f.write(data)
            print(f"{GREEN}[√] File saved{RESET}")
    except PermissionError:
        print(
            f"{RED}[ERR] The file '{path}' is in use, please close it and try again{RESET}"
        )
        pause()
        exit()


def backup(path: pathlib.Path):
    print(f"\n> Backing up '{path.name}'")
    bakfile = path.with_name(path.name + ".bak")
    if not os.path.exists(bakfile):
        shutil.copy2(path, bakfile)
        print(f"{GREEN}[√] Backup created: '{bakfile.name}'{RESET}")
    else:
        print(f"{BLUE}[i] Backup '{bakfile.name}' already exists, good{RESET}")


def replace(
    data: bytes, pattern: str | bytes, replace: str | bytes, probe: str | bytes
) -> bytes:
    if isinstance(pattern, str):
        pattern = pattern.encode()
    if isinstance(replace, str):
        replace = replace.encode()
    if isinstance(probe, str):
        probe = probe.encode()
    assert isinstance(pattern, bytes)
    assert isinstance(replace, bytes)
    assert isinstance(probe, bytes)
    print(f"> {pattern.decode()} => {replace.decode()}")

    regex = re.compile(pattern, re.DOTALL)
    count = len(list(regex.finditer(data)))
    patched_regex = re.compile(probe, re.DOTALL)
    patched_count = len(list(patched_regex.finditer(data)))

    if count == 0:
        if patched_count > 0:
            print(
                f"{BLUE}[i] Found {patched_count} pattern{'' if patched_count == 1 else 's'} already patched, will overwrite{RESET}"
            )
        else:
            print(f"{YELLOW}[WARN] Pattern <{pattern}> not found, SKIPPED!{RESET}")
            return data

    data, replaced1_count = patched_regex.subn(replace, data)
    data, replaced2_count = regex.subn(replace, data)
    replaced_count = replaced1_count + replaced2_count
    if replaced_count != count + patched_count:
        print(
            f"{YELLOW}[WARN] Patched {replaced_count}/{count}, failed {count - replaced_count}{RESET}"
        )
    else:
        print(
            f"{GREEN}[√] Patched {replaced_count} pattern{'' if count == 1 else 's'}{RESET}"
        )
    return data
