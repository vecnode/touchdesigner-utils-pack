# Useful set of functions to deal with OS (tested: Windows 11)
import os
import winreg
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple


# Opens a registry key for read access on the 64-bit view.
def _open_registry_key(hive, key_path):
    return winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)


# Iterates subkey names for a given opened registry key.
def _iter_subkey_names(key_handle) -> Iterator[str]:
    index = 0
    while True:
        try:
            yield winreg.EnumKey(key_handle, index)
            index += 1
        except OSError:
            break


# Iterates value tuples for a given opened registry key.
def _iter_values(key_handle) -> Iterator[Tuple[str, object, int]]:
    index = 0
    while True:
        try:
            yield winreg.EnumValue(key_handle, index)
            index += 1
        except OSError:
            break


# Joins a registry path and child key using registry separators.
def _join_registry_path(parent: str, child: str) -> str:
    return f"{parent}\\{child}" if parent else child


# Returns a printable dump of direct subkeys and values under a registry path.
def list_registry_keys_values(hive, key_path):
    lines: List[str] = [f"\nListing registry keys and values under: {key_path}"]
    try:
        with _open_registry_key(hive, key_path) as key:
            for subkey_name in _iter_subkey_names(key):
                lines.append(f"Subkey: {subkey_name}")
            for value_name, value_data, value_type in _iter_values(key):
                lines.append(f"Value: {value_name}, Data: {value_data}, Type: {value_type}")
    except FileNotFoundError:
        lines.append(f"Key not found: {key_path}")
    return "\n".join(lines) + "\n"


# Recursively searches registry keys by name and returns matching key dumps.
def search_for_key_in_registry_list(hive, key_path, search_term):
    results: List[str] = []
    needle = str(search_term).lower()
    try:
        with _open_registry_key(hive, key_path) as key:
            for subkey_name in _iter_subkey_names(key):
                full_subkey_path = _join_registry_path(key_path, subkey_name)
                if needle in subkey_name.lower():
                    results.append(list_registry_keys_values(hive, full_subkey_path))
                # Recurse into subkeys to keep original behavior.
                nested = search_for_key_in_registry_list(hive, full_subkey_path, search_term)
                if nested:
                    results.append(nested)
    except FileNotFoundError:
        return ""
    return "".join(results)


# Lists all detected TouchDesigner executables under likely install directories.
def find_touchdesigner_executables(base_dirs: Optional[Sequence[str]] = None) -> List[str]:
    if base_dirs is None:
        base_dirs = [
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
        ]

    seen = set()
    matches: List[str] = []
    for base_dir in base_dirs:
        if not base_dir:
            continue
        derivative_path = os.path.join(base_dir, "Derivative")
        if not os.path.isdir(derivative_path):
            continue
        try:
            items = os.listdir(derivative_path)
        except OSError:
            continue
        for item in items:
            if "TouchDesigner" not in item:
                continue
            touchdesigner_path = os.path.join(derivative_path, item, "bin", "TouchDesigner.exe")
            if os.path.isfile(touchdesigner_path):
                normalized = os.path.normcase(os.path.normpath(touchdesigner_path))
                if normalized not in seen:
                    seen.add(normalized)
                    matches.append(touchdesigner_path)
    return matches


# Returns the first detected TouchDesigner executable or a not-found message.
def find_touchdesigner_exe(base_dirs=None):
    matches = find_touchdesigner_executables(base_dirs=base_dirs)
    if matches:
        return matches[0]
    return "TouchDesigner executable not found."




# Detects installed plugin binaries (VST2, VST3, and AU-style bundles) on Windows.
def find_audio_plugins_windows(
    extra_dirs: Optional[Sequence[str]] = None,
    include_registry_paths: bool = True,
) -> Dict[str, List[str]]:
    plugin_ext_by_type = {
        "vst2": (".dll",),
        "vst3": (".vst3",),
        "au": (".component",),
    }

    default_dirs = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Common Files", "VST3"),
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Steinberg", "VstPlugins"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Steinberg", "VstPlugins"),
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "VstPlugins"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "VstPlugins"),
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Common Files", "Avid", "Audio", "Plug-Ins"),
        os.path.join(os.environ.get("COMMONPROGRAMFILES", "C:\\Program Files\\Common Files"), "Audio", "Plug-Ins", "Components"),
    ]

    candidate_dirs: List[str] = [d for d in default_dirs if d]
    if extra_dirs:
        candidate_dirs.extend(d for d in extra_dirs if d)

    if include_registry_paths:
        registry_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VST"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\VST"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VST3"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\VST"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\VST3"),
        ]
        for hive, key_path in registry_locations:
            try:
                with _open_registry_key(hive, key_path) as key:
                    try:
                        value, _ = winreg.QueryValueEx(key, "VSTPluginsPath")
                        if isinstance(value, str) and value.strip():
                            candidate_dirs.append(value.strip())
                    except FileNotFoundError:
                        pass
                    try:
                        value, _ = winreg.QueryValueEx(key, "VST3Path")
                        if isinstance(value, str) and value.strip():
                            candidate_dirs.append(value.strip())
                    except FileNotFoundError:
                        pass
            except FileNotFoundError:
                continue

    normalized_dirs_seen: Set[str] = set()
    scan_dirs: List[str] = []
    for path in candidate_dirs:
        expanded = os.path.expandvars(os.path.expanduser(str(path).strip().strip('"')))
        normalized = os.path.normcase(os.path.normpath(expanded))
        if normalized in normalized_dirs_seen:
            continue
        normalized_dirs_seen.add(normalized)
        if os.path.isdir(expanded):
            scan_dirs.append(expanded)

    found: Dict[str, Set[str]] = {"vst2": set(), "vst3": set(), "au": set()}
    for root_dir in scan_dirs:
        for current_root, _, files in os.walk(root_dir):
            for filename in files:
                full_path = os.path.join(current_root, filename)
                lower_name = filename.lower()
                for plugin_type, exts in plugin_ext_by_type.items():
                    if lower_name.endswith(exts):
                        found[plugin_type].add(os.path.normpath(full_path))

    # Some hosts store VST3 as directories ending with .vst3.
    for root_dir in scan_dirs:
        try:
            for item in os.listdir(root_dir):
                full_path = os.path.join(root_dir, item)
                if os.path.isdir(full_path) and item.lower().endswith(".vst3"):
                    found["vst3"].add(os.path.normpath(full_path))
        except OSError:
            continue

    return {
        "vst2": sorted(found["vst2"], key=lambda p: p.lower()),
        "vst3": sorted(found["vst3"], key=lambda p: p.lower()),
        "au": sorted(found["au"], key=lambda p: p.lower()),
    }



def main():
    print("Utilities for TouchDesigner Projects")


if __name__ == "__main__":
    main()

