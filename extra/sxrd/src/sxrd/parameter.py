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

from pathlib import Path

class AtomInfo(BaseModel):
    name: str
    pos_center: Annotated[List[float], Len(min_length=3, max_length=3)]
    DWfactor: float
    occupancy: float = Field(default=1.0)
    displace_vector: Optional[List[List[Union[int, float]]]] = None
    opt_DW: Optional[List[Union[int, float]]] = None
    opt_occupancy: Optional[int] = None

    def is_coeff(v):
        return (isinstance(v, list)
                and len(v)==4
                and isinstance(v[0], int)
                and isinstance(v[1], Number)
                and isinstance(v[2], Number)
                and isinstance(v[3], Number)
        )

    @field_validator("displace_vector")
    def displace_vector_format(cls, vs):
        if all([AtomInfo.is_coeff(v) for v in vs]):
            return vs
        raise ValueError("must contain type and three coeffs")

    @field_validator("opt_DW")
    def opt_dw_format(cls, v):
        if len(v)==2 and isinstance(v[0], int) and isinstance(v[1], Number):
            return v
        raise ValueError("must contain type and three coeffs")

class DomainInfo(BaseModel):
    domain_occupancy: float
    atom: List[AtomInfo]

class SolverParam(BaseModel):
    scale_factor: Optional[float] = 1.0
    opt_scale_factor: Optional[bool] = False
    type_vector: List[int]
    domain: List[DomainInfo]

class SolverReference(BaseModel):
    f_in_file: str

class SolverConfig(BaseModel):
    sxrd_exec_file: Path = "sxrdcalc"
    bulk_struc_in_file: Path

class SolverInfo(BaseModel):
    name: Optional[str] = None
    config: SolverConfig
    reference: SolverReference
    param: SolverParam
    option: Optional[Dict[str,str]] = None


if __name__ == "__main__":
    import tomli

    input_data = """
[solver]
  name = "sxrd"
[solver.config]
  #sxrd_exec_file = "../bin/sxrdcalc.exe"
  bulk_struc_in_file = "sic111-r3xr3.blk"
[solver.param]
  scale_factor = 1.0
  type_vector = [1, 2]
[[solver.param.domain]]
  domain_occupancy = 1.0
  [[solver.param.domain.atom]]
    name = "Si"
    pos_center = [0.0, 0.0, 0.0]
    DWfactor = 0.0
    occupancy = 1.0
    displace_vector = [[1, 0.0, 0.0, 1.0]]
  [[solver.param.domain.atom]]
    name = "Si"
    pos_center = [0.3333, 0.6666, 1.0]
    DWfactor = 0.0
    occupancy = 1.0
    displace_vector = [[1, 0.0, 0.0, 1.0]]
  [[solver.param.domain.atom]]
    name = "Si"
    pos_center = [0.6666, 0.3333, 1.0]
    DWfactor = 0.0
    occupancy = 1.0
    displace_vector = [[1, 0.0, 0.0, 1.0]]
  [[solver.param.domain.atom]]
    name = "Si"
    pos_center = [0.3333, 0.3333, 1.2]
    DWfactor = 0.0
    occupancy = 1.0
    displace_vector = [[2, 0, 0.0, 1.0]]
[solver.reference]
  f_in_file = "sic111-r3xr3_f.dat"
[solver.option]
  optional = parameters
"""
    params = tomli.loads(input_data)
    si = SolverInfo(**params["solver"])
    print(si)

