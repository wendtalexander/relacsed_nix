import os
import numpy as np
import json


def nix_metadata_to_dict(section):
    info = {}
    for p in section.props:
        info[p.name] = ([v for v in p.values], p.unit if p.unit is not None else "")
    for s in section.sections:
        info[s.name] = nix_metadata_to_dict(s)
    return info


def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()


def metadata_to_json(dict):
    return json.dumps(dict, default=np_encoder)


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
