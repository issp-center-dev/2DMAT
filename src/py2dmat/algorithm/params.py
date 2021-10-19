import typing
from typing import cast
from typing import List, Optional, Union, Any, overload, MutableMapping

import itertools
import pathlib
from os import PathLike

import abc

import numpy as np

from py2dmat import exception


class Param(abc.ABC):
    name: str

    def __init__(self):
        ...

    @abc.abstractmethod
    def random(self, rng: np.random.RandomState, nwalkers: int = 1) -> np.ndarray:
        ...

    @abc.abstractmethod
    def next(
        self, rng: np.random.RandomState, x: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        ...

    @abc.abstractmethod
    def isValid(self, val: Union[float, np.ndarray]) -> Union[bool, np.ndarray]:
        ...

    @property
    @abc.abstractmethod
    def lower_bound(self) -> float:
        ...

    @property
    @abc.abstractmethod
    def upper_bound(self) -> float:
        ...

    @property
    @abc.abstractmethod
    def unit(self) -> float:
        ...


class ContinuousParam(Param):
    _lower_bound: float
    _upper_bound: float
    _unit: float

    def __init__(
        self, lower_bound: float, upper_bound: float, unit: float, name: str = None
    ):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._unit = unit
        if name is None:
            self.name = ""
        else:
            self.name = name

    @classmethod
    def from_dict(cls, input_dict: MutableMapping[str, Any]) -> "ContinuousParam":
        for name in ("xmin", "xmax"):
            if name not in input_dict:
                msg = f"ERROR: [[algorithm.parameter]] does not have '{name}'"
                raise exception.InputError(msg)
        lower_bound = input_dict["xmin"]
        upper_bound = input_dict["xmax"]
        unit = input_dict.get("xunit", 1.0)
        name = input_dict.get("name", "")
        return cls(lower_bound, upper_bound, unit, name)

    def random(self, rng: np.random.RandomState, nwalkers: int = 1) -> np.ndarray:
        return (
            rng.random_sample(nwalkers) * (self.upper_bound - self.lower_bound)
            + self.lower_bound
        )

    @overload
    def next(self, rng: np.random.RandomState, x: float) -> float:
        ...

    @overload
    def next(self, rng: np.random.RandomState, x: np.ndarray) -> np.ndarray:
        ...

    def next(self, rng: np.random.RandomState, x):
        step = rng.normal() * self.unit
        return x + step

    @overload
    def isValid(self, val: float) -> bool:
        ...

    @overload
    def isValid(self, val: np.ndarray) -> np.ndarray:
        ...

    def isValid(self, val):
        return (self.lower_bound <= val) & (val <= self.upper_bound)

    @property
    def lower_bound(self) -> float:
        return self._lower_bound

    @property
    def upper_bound(self) -> float:
        return self._upper_bound

    @property
    def unit(self) -> float:
        return self._unit


class DiscreteParam(Param):
    candidates: np.ndarray
    ncandidates: int

    def __init__(self, candidates: np.ndarray, name: str = "") -> None:
        self.candidates = candidates
        self.ncandidates = candidates.size
        if name is None:
            self.name = ""
        else:
            self.name = name

    @classmethod
    def from_dict(cls, input_dict: MutableMapping[str, Any]) -> "DiscreteParam":
        if "xs" in input_dict:
            candidates = np.array(input_dict["xs"])
        else:
            for name in ("xmin", "xmax", "xnum"):
                if name not in input_dict:
                    msg = f"ERROR: [[algorithm.parameter]] does not have '{name}'"
                    raise exception.InputError(msg)
            lower_bound = input_dict["xmin"]
            upper_bound = input_dict["xmax"]
            xnum = input_dict["xnum"]
            candidates = np.linspace(start=lower_bound, stop=upper_bound, num=xnum)
        candidates.sort()
        name = input_dict.get("name", "")
        return cls(candidates, name)

    @overload
    def next(self, rng: np.random.RandomState, x: float) -> float:
        ...

    @overload
    def next(self, rng: np.random.RandomState, x: np.ndarray) -> np.ndarray:
        ...

    def next(self, rng: np.random.RandomState, x):
        step = rng.randint(low=1, high=self.ncandidates)
        c = self.index(x)
        return self.candidates[(c + step) % self.ncandidates]

    def random(self, rng: np.random.RandomState, nwalkers: int) -> np.ndarray:
        return self.candidates[rng.randint(self.ncandidates, size=nwalkers)]

    @overload
    def isValid(self, val: float) -> bool:
        ...

    @overload
    def isValid(self, val: np.ndarray) -> np.ndarray:
        ...

    def isValid(self, val):
        cs = self.index(val)
        if isinstance(val, int):
            return bool(np.isclose(self.candidates[cs], val))
        else:
            return np.isclose(self.candidates[cs], val)

    @overload
    def index(self, x: float) -> int:
        ...

    @overload
    def index(self, x: np.ndarray) -> np.ndarray:
        ...

    def index(self, x):
        if isinstance(x, float):
            c = cast(int, self.candidates.searchsorted(x))
            if c == self.ncandidates:
                c -= 1
            rs = (self.candidates[[c - 1, c]] - x) ** 2
            if rs[0] < rs[1]:
                return c - 1
            else:
                return c
        else:
            cs = self.candidates.searchsorted(x)
            for i, c in enumerate(cs):
                if c == self.ncandidates:
                    c -= 1
                rs = (self.candidates[[c - 1, c]] - x) ** 2
                if rs[0] < rs[1]:
                    cs[i] = c - 1
                else:
                    cs[i] = c
            return cs

    def __iter__(self):
        yield from self.candidates

    @property
    def lower_bound(self) -> float:
        return self.candidates[0]

    @property
    def upper_bound(self) -> float:
        return self.candidates[-1]

    @property
    def unit(self) -> float:
        raise NotImplementedError()


class SetParams:
    _coordinates: np.ndarray
    ncoordinates: int
    neighbor_list: List[List[int]]
    ncandidates: np.ndarray
    offset: int
    _indicies: np.ndarray

    def __init__(
        self, coordinates: np.ndarray, offset: int = 0, indices: np.ndarray = None
    ) -> None:
        self._coordinates = coordinates
        self.ncoordinates = coordinates.shape[0]
        self.offset = offset
        self.neighbor_list = []
        self.ncandidates = np.array([])
        if indices is None:
            self._indices = np.arange(offset, offset + self.ncoordinates)
        else:
            self._indices = indices

    def coordinate(self, index: Union[int, List[int], np.ndarray]) -> np.ndarray:
        return self._coordinates[np.array(index) - self.offset, :]

    def next(
        self, rng: np.random.RandomState, index: Union[int, List[int], np.ndarray]
    ) -> np.ndarray:
        indices = np.array(index)
        ret = []
        for i in indices:
            neighbors = self.neighbor_list[i]
            j = rng.randint(self.ncandidates[i])
            ret.append(neighbors[j])
        return np.array(ret, dtype=int)

    def random(self, rng: np.random.RandomState, nwalkers: int = 1) -> np.ndarray:
        return (
            rng.randint(self.ncoordinates, shape=(nwalkers, self.ncoordinates))
            + self.offset
        )

    def set_neighborlist(self, nlist: List[List[int]]) -> None:
        self.neighbor_list = nlist
        self.ncandidates = np.array([len(nn) for nn in nlist])

    def coordinates(self, mpisize: int = 1, mpirank: int = 0):
        idx = np.array_split(np.arange(self.ncoordinates), mpisize)[mpirank]
        return self._coordinates[idx, :]

    def indices(self, mpisize: int = 1, mpirank: int = 0):
        idx = np.array_split(np.arange(self.ncoordinates), mpisize)[mpirank]
        return self._indices[idx]


class DirectProductParams:
    params: List[Param]
    nparams: int

    def __init__(self, params: List[Param]) -> None:
        self.params = params
        self.nparams = len(params)

    def next(
        self,
        rng: np.random.RandomState,
        x: np.ndarray,
        *,
        changes: Optional[Union[int, List[int], List[bool]]] = None,
    ) -> np.ndarray:
        """
        Propose a next candidate

        Parameters
        -------------
        rng: np.random.RandomState
            Random number generator

        changes: int or list of int or list of bool, default None
            Which parameters will be changed.
            If None, all the parameters will be changed.
        """
        if x.ndim == 1:
            x = x.reshape((1, -1))
            is_1d = True
        elif x.ndim == 2:
            is_1d = False
        else:
            raise RuntimeError()

        if changes is None:
            changes_ = np.ones(shape=self.nparams, dtype=bool)
        elif isinstance(changes, int):
            changes_ = np.zeros(shape=self.nparams, dtype=bool)
            changes_[changes] = True
        else:
            if len(changes) == 0:
                changes_ = np.zeros(shape=self.nparams, dtype=bool)
            elif isinstance(changes[0], int):
                changes_ = np.zeros(shape=self.nparams, dtype=bool)
                changes_[changes] = True
            else:
                changes_ = np.array(changes)

        nwalkers = x.shape[0]
        ret = np.zeros((nwalkers, self.nparams), dtype=float)
        for iwalker in range(nwalkers):
            for ipara in range(self.nparams):
                if changes_[ipara]:
                    r = self.params[ipara].next(rng, x[iwalker, ipara])
                    ret[iwalker, ipara] = r
                else:
                    ret[iwalker, ipara] = x[iwalker, ipara]
        if is_1d:
            ret = ret.reshape(-1)
        return ret

    def random(self, rng: np.random.RandomState, nwalkers: int = 1) -> np.ndarray:
        X = np.zeros(shape=(nwalkers, self.nparams), dtype=float)
        for iparam in range(self.nparams):
            X[:, iparam] = self.params[iparam].random(rng, nwalkers)
        return X

    def isValid(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            x = np.reshape(x, (1, -1))
        elif x.ndim > 2:
            raise RuntimeError()

        n = x.shape[0]
        res = np.ones(n, dtype=bool)
        for i in range(n):
            for v, param in zip(x[i,:], self.params):
                res[i] &= param.isValid(cast(float, v))
        return res

    def min_list(self) -> np.ndarray:
        res = [p.lower_bound for p in self.params]
        return np.array(res)

    def max_list(self) -> np.ndarray:
        res = [p.upper_bound for p in self.params]
        return np.array(res)

    def unit_list(self) -> np.ndarray:
        res = [p.unit for p in self.params]
        return np.array(res)

    def is_all_continuous(self) -> bool:
        b = np.array([isinstance(param, ContinuousParam) for param in self.params])
        return bool(b.all())

    def is_all_discrete(self) -> bool:
        b = np.array([isinstance(param, DiscreteParam) for param in self.params])
        return bool(b.all())

    def to_SetParams(self) -> SetParams:
        return SetParams(np.array([list(it) for it in itertools.product(*self.params)]))


def read_input_old(
    info_param: MutableMapping[str, Any], dimension: int, root_dir: PathLike
):
    if "mesh_path" in info_param:
        mesh_path = root_dir / pathlib.Path(info_param["mesh_path"]).expanduser()
        comments = info_param.get("comments", "#")
        delimiter = info_param.get("delimiter", None)
        skiprows = info_param.get("skiprows", 0)

        data = np.loadtxt(
            mesh_path, comments=comments, delimiter=delimiter, skiprows=skiprows,
        )
        indices = data[:, 0].astype(int)
        coords = data[:, 1:]
        return SetParams(coords, offset=indices[0], indices=indices)

    if "min_list" not in info_param:
        raise exception.InputError(
            "ERROR: algorithm.param.min_list is not defined in the input"
        )
    min_list = np.array(info_param["min_list"])
    if len(min_list) != dimension:
        raise exception.InputError(
            f"ERROR: len(min_list) != dimension ({len(min_list)} != {dimension})"
        )

    if "max_list" not in info_param:
        raise exception.InputError(
            "ERROR: algorithm.param.max_list is not defined in the input"
        )
    max_list = np.array(info_param["max_list"])
    if len(max_list) != dimension:
        raise exception.InputError(
            f"ERROR: len(max_list) != dimension ({len(max_list)} != {dimension})"
        )

    if "num_list" in info_param:
        num_list = np.array(info_param["num_list"], dtype=int)
        if len(num_list) != dimension:
            raise exception.InputError(
                f"ERROR: len(num_list) != dimension ({len(num_list)} != {self.dimension})"
            )
        params: List[Param] = []
        for lower, upper, num in zip(min_list, max_list, num_list):
            candidates = np.linspace(
                cast(float, lower), cast(float, upper), num=cast(int, num)
            )
            params.append(DiscreteParam(candidates))
        return DirectProductParams(params)
    else:
        unit_list = np.array(info_param.get("unit_list", [1.0] * dimension))
        if len(unit_list) != dimension:
            raise exception.InputError(
                f"ERROR: len(unit_list) != dimension ({len(unit_list)} != {dimension})"
            )
        params: List[Param] = []
        for lower, upper, unit in zip(min_list, max_list, unit_list):
            lower = cast(float, lower)
            upper = cast(float, upper)
            unit = cast(float, unit)
            params.append(ContinuousParam(lower, upper, unit))
        return DirectProductParams(params)


def read_input(
    input_dict: MutableMapping[str, Any], dimension: int, root_dir: PathLike
):
    if "parameter" in input_dict:
        # new format
        params_array_tables = input_dict["parameter"]
        params: List[Param] = []
        for param_dict in params_array_tables:
            repeat = param_dict.get("repeat", 1)
            if not (isinstance(repeat, int) and repeat >= 0):
                msg = f"repeat should be non-negative integer ({repeat} is given)"
                raise exception.InputError(msg)
            for _ in range(repeat):
                if "xs" in param_dict or "xnum" in param_dict:
                    param = DiscreteParam.from_dict(param_dict)
                else:
                    param = ContinuousParam.from_dict(param_dict)
                params.append(param)
        if len(params) != dimension:
            raise exception.InputError(
                f"ERROR: len(parameter) != dimension ({len(params)} != {dimension})"
            )
        return DirectProductParams(params)
    else:
        # old format
        if "param" not in input_dict:
            raise exception.InputError(
                "ERROR: algorithm.param is not defined in the input"
            )
        return read_input_old(input_dict["param"], dimension, root_dir)
