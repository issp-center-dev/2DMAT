# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure
# Copyright (C) 2020- The University of Tokyo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

from typing import Tuple, List, Dict, Union, Optional, Annotated
from annotated_types import Len
from pydantic import BaseModel, PositiveInt, ValidationError, Field, field_validator
from numbers import Number

class SolverConfig(BaseModel):
    path_to_solver: str = "satl2.exe"
    
class SolverReference(BaseModel):
    path_to_base_dir: str = "base"

class SolverInfo(BaseModel):
    name: Optional[str]
    config: SolverConfig
    reference: SolverReference

if __name__ == "__main__":
    import tomli

    input_data = """
    [solver]
    [solver.config]
    path_to_solver = "satl2.exe"
    [solver.reference]
    path_to_base_dir = "base"
    """

    params = tomli.loads(input_data)
    si = SolverInfo(**params["solver"])

    print(si)
