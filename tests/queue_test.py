# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019-2020 Damien P. George

from asyncio import Queue, run as run_task
import sys


def test_single_queue():
    async def run_single_queue():
        print(sys.path)
        print(Queue)

        queue = Queue()

        for i in range(5):
            await queue.put(("Hello world", i))

        assert await queue.get() == ("Hello world", 0)
        assert await queue.get() == ("Hello world", 1)
        assert await queue.get() == ("Hello world", 2)
        assert await queue.get() == ("Hello world", 3)
        assert await queue.get() == ("Hello world", 4)

    run_task(run_single_queue())
