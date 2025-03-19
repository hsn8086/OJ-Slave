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
import psutil
import time
from typing import Literal
from pydantic import BaseModel
from subprocess import Popen
from typing import Callable
from ..celery_app import app


class Result(BaseModel):
    output: str
    type: Literal[
        "success", "runtime_error", "compile_error", "timeout", "memory_limit_exceeded"
    ]
    time: float = 0
    memory: float = 0


class RunProcessResult(BaseModel):
    status: Literal[
        "success", "runtime_error", "compile_error", "timeout", "memory_limit_exceeded"
    ] = "success"
    stdout: str
    stderr: str
    time: float
    memory: float


def run_p(cmd: list, inp: str = "", *, memory_limit: int = 256, timeout: int = 1):
    with Popen(
        cmd, text=True, stdin=-1, stdout=-1, stderr=-1
    ) as p:  # set stdin to -1 for input and stdout stderr to -1 for capture output.
        start = time.time()
        p.stdin.write(inp)
        p.stdin.flush()  # input and flush the buffer
        max_memory = 0
        while True:
            state = p.poll()  # check process state
            if state is not None:
                return RunProcessResult(
                    stdout=p.stdout.read(),
                    stderr=p.stderr.read(),
                    time=time.time() - start,
                    memory=max_memory,
                )

            child_process = psutil.Process(
                p.pid
            )  # use psutil tu monitoring process status

            mem_use = child_process.memory_full_info().uss / (1024**2)
            max_memory = max(max_memory, mem_use)
            if mem_use > memory_limit:  # check memory
                child_process.kill()
                child_process.terminate()
                return RunProcessResult(
                    status="memory_limit_exceeded",
                    stdout=p.stdout.read(),
                    stderr=p.stderr.read(),
                    time=time.time() - start,
                    memory=max_memory,
                )

            if time.time() - start >= timeout:  # check timeout
                child_process.kill()
                child_process.terminate()
                return RunProcessResult(
                    status="timeout",
                    stdout=p.stdout.read(),
                    stderr=p.stderr.read(),
                    time=time.time() - start,
                    memory=max_memory,
                )


def run(
    code: str,
    inp: str,
    cmd: str,
    *,
    memory_limit: int = 256,
    timeout: int = 1,
    compile_func: Callable | None = None,
):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(code.encode())
        tmp.seek(0)
        # print(f"python{version}", tmp.name)
        file_name = tmp.name
        if compile_func:
            try:
                file_name = compile_func(file_name)
            except Exception as e:
                return Result(output=str(e), type="compile_error", time=0, memory=0)
        try:
            rst = run_p(
                cmd.format(file_name=file_name).split(),
                inp=inp,
                timeout=timeout,
                memory_limit=memory_limit,
            )
            stdout = rst.stdout
            stderr = rst.stderr
            time = rst.time
            memory = rst.memory
            status = rst.status
        except Exception as e:
            return Result(output=str(e), type="runtime_error", time=0, memory=0)
        if status == "timeout":
            return Result(output=stdout, type="timeout", time=time, memory=memory)
        elif status == "memory_limit_exceeded":
            return Result(
                output=stdout, type="memory_limit_exceeded", time=time, memory=memory
            )

        if stderr:
            return Result(output=stderr, type="runtime_error", time=time, memory=memory)
        return Result(output=stdout, type="success", time=time, memory=memory)


@app.task
def py(
    code: str,
    inp: str,
    *,
    memory_limit: int = 256,
    timeout: int = 1,
    version: str = "3",
) -> Result:
    return run(
        code=code,
        inp=inp,
        cmd=f"python{version} {{file_name}}",
        memory_limit=memory_limit,
        timeout=timeout,
    )


@app.task
def pypy(
    code: str,
    inp: str,
    *,
    memory_limit: int = 256,
    timeout: int = 1,
    version: str = "3",
) -> Result:
    return run(
        code=code,
        inp=inp,
        cmd=f"pypy{version} {{file_name}}",
        memory_limit=memory_limit,
        timeout=timeout,
    )


def codon_compile(file_name: str) -> str:
    res = subprocess.run(
        ["/root/.codon/bin/codon", "build", "-release", file_name, "-o", file_name + ".out"],
        text=True,
        capture_output=True,
    )
    if res.returncode != 0:
        raise Exception(res.stderr)
    return file_name + ".out"


@app.task
def codon(
    code: str,
    inp: str,
    *,
    memory_limit: int = 256,
    timeout: int = 1,
) -> Result:
    return run(
        code=code,
        inp=inp,
        cmd="{file_name}",
        memory_limit=memory_limit,
        timeout=timeout,
        compile_func=codon_compile,
    )


def gcc_compile(code_type: Literal["gcc", "gpp"]) -> str:
    def warp(file_name: str) -> str:
        exe = "gcc" if code_type == "gcc" else "g++"
        opition = "-xc" if code_type == "gcc" else "-xc++"
        res = subprocess.run(
            [exe, opition, file_name, "-o", file_name + ".out"],
            text=True,
            capture_output=True,
        )
        if res.returncode != 0:
            raise Exception(res.stderr)
        return file_name + ".out"

    return warp


@app.task
def gcc(code: str, inp: str, *, memory_limit: int = 256, timeout: int = 1) -> Result:
    return run(
        code=code,
        inp=inp,
        cmd="{file_name}",
        compile_func=gcc_compile(code_type="gcc"),
        memory_limit=memory_limit,
        timeout=timeout,
    )


@app.task
def gpp(code: str, inp: str, *, memory_limit: int = 256, timeout: int = 1) -> Result:
    return run(
        code=code,
        inp=inp,
        cmd="{file_name}",
        compile_func=gcc_compile(code_type="gpp"),
        memory_limit=memory_limit,
        timeout=timeout,
    )
