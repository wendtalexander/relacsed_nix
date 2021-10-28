import os


def nix_metadata_to_dict(section):
    info = {}
    for p in section.props:
        info[p.name] = ([v for v in p.values], p.unit if p.unit is not None else "")
    for s in section.sections:
        info[s.name] = nix_metadata_to_dict(s)
    return info


def is_windows_path(path):
    return "\\" in path


def convert_path(path):
    converted = ""
    if is_windows_path(path):
        if os.sep == "/":  # unix like
            converted = path.replace("\\", "/")
        else:
            converted = path
    else:
        if os.sep == "\\":
            converted = path.replace("/", "\\")
        else:
            converted = path
    return converted
