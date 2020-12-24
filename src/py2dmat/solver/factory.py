from typing import Dict, Type

from .solver_base import Solver_Base
from . import surface
from . import analytical


class SolverFactory:
    """
    Factory class of solvers

    Attributes
    ==========
    solvers: Dict[str, Type[Solver_Base]]
        Registered solvers
    """

    solvers: Dict[str, Type[Solver_Base]] = {}

    def __init__(self) -> None:
        self.register(surface.surface, "surface")
        self.register(analytical.analytical, "analytical")

    def register(self, solver: Type[Solver_Base], solver_name: str) -> None:
        if solver_name in self.solvers:
            raise RuntimeError(f"solver_name '{solver_name}' is already registered")
        self.solvers[solver_name] = solver

    def solver(self, name: str, *args, **kw) -> Solver_Base:
        if name not in self.solvers:
            raise RuntimeError(f"solver '{name}' is not registered")
        return self.solvers[name](*args, **kw)
