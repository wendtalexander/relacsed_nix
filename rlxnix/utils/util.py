import os
import json
import logging
import numpy as np
import pandas as pd

from tqdm import tqdm

def nix_metadata_to_dict(section):
    info = {}
    for p in section.props:
        info[p.name] = ([v for v in p.values], p.unit if p.unit is not None else "")
    for s in section.sections:
        info[s.name] = nix_metadata_to_dict(s)
    return info


def np_encoder(object : np.generic):
    """Makes sure to properly convert numpy types for the json dump

    Parameters
    ----------
    object : Any
        any numpy data object

    Returns
    -------
    python native
        the object as python native equivalent
    """
    if isinstance(object, np.generic):
        return object.item()


def metadata_to_json(metadata_dict: dict)->str:
    """Dumps a dictionary to json

    Parameters
    ----------
    metadata_dict : dict
        The metadata dictionary
    Returns
    -------
    str
        A json string.
    """
    return json.dumps(metadata_dict, default=np_encoder)


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


def data_links_to_pandas(data_links) -> pd.DataFrame:
    """Export the rlxnix.DataLink objects to a pandas.DataFrame.

    Parameters
    ----------
    data_links : list of DataLink
        DataLinks of stimulus segments or ReproRuns.

    Returns
    -------
    pd.DataFrame
        The DataFrame
    """
    df_list = []
    for dl in tqdm(data_links, disable=not(logging.root.level == logging.INFO)):
        df_list.append(dl.to_pandas())
    return pd.concat(df_list, ignore_index=True)



