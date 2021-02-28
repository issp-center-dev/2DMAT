# -*- coding: utf-8 -*-
from typing import MutableMapping, Optional
from pathlib import Path

from . import exception


class Info:
    base: dict
    algorithm: dict
    solver: dict
    runner: dict

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
        self.base = d["base"]
        self.algorithm = d["algorithm"]
        self.solver = d["solver"]
        self.runner = d.get("runner", {})

        self.base["root_dir"] = (
            Path(self.base.get("root_dir", ".")).expanduser().absolute()
        )
        self.base["output_dir"] = (
            self.base["root_dir"]
            / Path(self.base.get("output_dir", ".")).expanduser()
        )

    def _cleanup(self) -> None:
        self.base = {}
        self.base["root_dir"] = Path(".").absolute()
        self.base["output_dir"] = self.base["root_dir"]
        self.algorithm = {}
        self.solver = {}
        self.runner = {}
