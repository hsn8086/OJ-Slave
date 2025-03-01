#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2024. Suto-Commune
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : runners.py

@Author     : hsn

@Date       : 2024/11/1 下午5:16
"""
import subprocess
import tempfile
from typing import Literal

from pydantic import BaseModel


class Result(BaseModel):
    output: str
    type: Literal["success", "runtime_error", "compile_error","timeout"]


def py(code: str, inp: str, *, version: str = "3") -> Result:
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(code.encode())
        tmp.seek(0)
        # print(f"python{version}", tmp.name)
        try:
            res = subprocess.run([f"python{version}", tmp.name],
                                 input=inp,
                                 text=True,
                                 capture_output=True,
                                 timeout=1
                                 )
        except subprocess.TimeoutExpired:
            return Result(output="Time limit exceeded", type="timeout")
    if res.returncode != 0:
        return Result(output=res.stderr, type="runtime_error")
    return Result(output=res.stdout, type="success")


def gcc(code: str, inp: str) -> Result:
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(code.encode())
        tmp.seek(0)
        res = subprocess.run(["gcc", tmp.name, "-o", tmp.name + ".out"],
                             text=True,
                             capture_output=True)
        if res.returncode != 0:
            return Result(output=res.stderr, type="compile_error")

        res = subprocess.run([tmp.name + ".out"],
                             input=inp,
                             text=True,
                             capture_output=True)
    if res.returncode != 0:
        return Result(output=res.stderr, type="runtime_error")
    return Result(output=res.stdout, type="success")


def gpp(code: str, inp: str) -> Result:
    with tempfile.NamedTemporaryFile(suffix=".cpp") as tmp:
        tmp.write(code.encode())
        tmp.seek(0)
        res = subprocess.run(["g++", tmp.name, "-o", tmp.name + ".out"],
                             text=True,
                             capture_output=True)
        if res.returncode != 0:
            return Result(output=res.stderr, type="compile_error")

        res = subprocess.run([tmp.name + ".out"],
                             input=inp,
                             text=True,
                             capture_output=True)
    if res.returncode != 0:
        return Result(output=res.stderr, type="runtime_error")
    return Result(output=res.stdout, type="success")
