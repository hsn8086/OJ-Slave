# !/usr/bin/env python
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
@File       : runner.py

@Author     : hsn

@Date       : 2024/11/1 下午5:02
"""

import asyncio
from celery.result import AsyncResult
from fastapi import APIRouter
from pydantic import BaseModel

from ..backend import runners


block_router = APIRouter(prefix="/block")
router = APIRouter(prefix="/runner")
router.include_router(block_router)


class Code(BaseModel):
    code: str
    input: str


@router.post("/get_result")
@router.get("/get_result")
async def get_result(task_id: str) -> runners.Result:
    async_task = AsyncResult(task_id)
    while not async_task.successful():
        await asyncio.sleep(0.1)
    return async_task.get()
    # tm = TaskManager()
    # return await tm.async_get_result(task_id)


@router.post("/py")
async def py_runner(
    code: Code, version: str = "3", memory_limit: int = 256, timeout: int = 1
) -> str:
    return runners.py.delay(
        code.code,
        code.input,
        version=version,
        memory_limit=memory_limit,
        timeout=timeout,
    ).id
    # task_id = f"py{version}_runner-{hashlib.sha256(code.code.encode()).hexdigest()}"
    # tm = TaskManager()
    # task = Task(task_id, runners.py, code.code, code.input, version=version)
    # tm.add(task)

    # return task_id


@router.post("/pypy")
async def pypy_runner(
    code: Code, version: str = "3", memory_limit: int = 256, timeout: int = 1
) -> str:
    return runners.pypy.delay(
        code.code,
        code.input,
        version=version,
        memory_limit=memory_limit,
        timeout=timeout,
    ).id
    # task_id = f"pypy{version}_runner-{hashlib.sha256(code.code.encode()).hexdigest()}"
    # tm = TaskManager()
    # task = Task(task_id, runners.pypy, code.code, code.input, version=version)
    # tm.add(task)
    # return task_id


@router.post("/codon")
async def codon_runner(code: Code, memory_limit: int = 256, timeout: int = 1) -> str:
    return runners.codon.delay(
        code.code,
        code.input,
        memory_limit=memory_limit,
        timeout=timeout,
    ).id


@router.post("/gcc")
def gcc_runner(code: Code, memory_limit: int = 256, timeout: int = 1) -> str:
    return runners.gcc.delay(
        code.code,
        code.input,
        memory_limit=memory_limit,
        timeout=timeout,
    ).id
    # task_id = f"gcc_runner-{hashlib.sha256(code.code.encode()).hexdigest()}"
    # tm = TaskManager()
    # task = Task(task_id, runners.gcc, code.code, code.input)
    # tm.add(task)
    # return task_id
    # res = runners.gcc(code.code, code.input)

    # return res


@router.post("/gpp")
def gpp_runner(code: Code, memory_limit: int = 256, timeout: int = 1) -> str:
    return runners.gpp.delay(
        code.code,
        code.input,
        memory_limit=memory_limit,
        timeout=timeout,
    ).id
    # task_id = f"gpp_runner-{hashlib.sha256(code.code.encode()).hexdigest()}"
    # tm = TaskManager()
    # task = Task(task_id, runners.gpp, code.code, code.input)
    # tm.add(task)
    # return task_id
    # res = runners.gpp(code.code, code.input)

    # return res
