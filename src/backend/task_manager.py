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
@File       : task_manager.py

@Author     : hsn

@Date       : 2024/11/12 下午12:10
"""

import asyncio
from collections import deque
from typing import Callable

from src.utils import SingletonMeta, Thread


class Task:
    def __init__(self, name: str, func: Callable, *args, **kwargs):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread = Thread(target=func, name=name, args=args, kwargs=kwargs)

    def run(self):
        self.thread.start()


class TaskManager(metaclass=SingletonMeta):
    def __init__(self, max_workers: int = 10):
        self.tasks = deque()
        self.max_workers = max_workers
        self.running = deque()
        self.results = {}
        self.task_set = set()

    def update(self):
        # remove finished tasks
        pop_tasks = []
        for task in self.running:
            if not task.thread.is_alive():
                pop_tasks.append(task)
                self.results[task.name] = task.thread.result

        for task in pop_tasks:
            self.running.remove(task)

        # add new tasks
        while self.tasks and len(self.running) < self.max_workers:
            task = self.tasks.popleft()
            task.run()
            self.running.append(task)

    def add(self, task: Task):
        self.tasks.append(task)
        self.task_set.add(task.name)

    def check(self):
        return self.tasks, self.running, self.results

    async def async_get_result(self, task_id: str):
        if task_id not in self.task_set:
            raise ValueError(f"Task {task_id} not found")
        self.update()
        while task_id not in self.results:
            self.update()
            await asyncio.sleep(0.1)

        return self.results[task_id]
