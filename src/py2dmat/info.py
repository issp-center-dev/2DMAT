# -*- coding: utf-8 -*-
from typing import MutableMapping, Optional
from pathlib import Path

from . import exception


class Info(dict):
    def __init__(self, d: Optional[MutableMapping] = None):
        if d is not None:
            self.from_dict(d)
        else:
            self._cleanup()

    def from_dict(self, d: MutableMapping) -> None:
        for section in ["base", "algorithm", "solver"]:
            if section not in d:
                raise exception.InputError(
                    f"ERROR: section {section} does not appear in input"
                )
        self._cleanup()
        self["base"] = d["base"]
        self["algorithm"] = d["algorithm"]
        self["solver"] = d["solver"]

        self["base"]["root_dir"] = Path(self["base"].get("root_dir", ".")).absolute()
        self["base"]["output_dir"] = Path(
            self["base"].get("output_dir", ".")
        ).absolute()

    def _cleanup(self) -> None:
        self["base"] = {}
        self["algorithm"] = {}
        self["solver"] = {}
        self["calc"] = {}
        self["log"] = {}
        self["log"]["Log_number"] = 0
        self["log"]["time"] = {}
        self["log"]["time"]["prepare"] = {}
        self["log"]["time"]["run"] = {}
        self["log"]["time"]["post"] = {}
