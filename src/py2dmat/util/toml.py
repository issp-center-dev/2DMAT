from typing import MutableMapping, Any

from ..mpi import rank

USE_TOML = False
TOMLI_VERSION = 2

try:
    import tomli

    if tomli.__version__ < "2.0.0":
        TOMLI_VERSION = 1
    else:
        TOMLI_VERSION = 2
except ImportError:
    try:
        import toml

        USE_TOML = True
        if rank() == 0:
            print("WARNING: tomli is not found and toml is found.")
            print("         use of toml package is left for compatibility.")
            print("         please install tomli package.")
            print("HINT: python3 -m pip install tomli")
            print()
    except ImportError:
        if rank() == 0:
            print("ERROR: tomli is not found")
            print("HINT: python3 -m pip install tomli")
        raise


def load(path: str) -> MutableMapping[str, Any]:
    """read TOML file

    Parameters
    ----------
    path: str
        File path to an input TOML file

    Returns
    -------
    toml_dict: MutableMapping[str, Any]
        Dictionary representing TOML file

    """
    if USE_TOML:
        return toml.load(path)
    else:
        if TOMLI_VERSION == 1:
            with open(path, "r") as f:
                return tomli.load(f)
        else:
            with open(path, "rb") as f:
                return tomli.load(f)
