# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test fairness of cancelling a task
# That tasks which continuously cancel each other don't take over the scheduler
import asyncio


async def task(id, other):
    for i in range(3):
        try:
            print("start", id)
            await asyncio.sleep(0)
            print("done", id)
        except asyncio.CancelledError as er:
            print("cancelled", id)
        if other is not None:
            print(id, "cancels", other)
            tasks[other].cancel()


async def main():
    global tasks
    tasks = [
        asyncio.create_task(task(0, 1)),
        asyncio.create_task(task(1, 0)),
        asyncio.create_task(task(2, None)),
    ]
    await tasks[2]


asyncio.run(main())
