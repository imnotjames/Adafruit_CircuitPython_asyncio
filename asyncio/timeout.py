try:
    from typing import Optional
except ImportError:
    pass

import time

from . import core


async def _timeout_wait(delay: float):
    await core.sleep(delay)


class Timeout:
    def __init__(self, when: Optional[float]):
        self._when = when
        self._current_task = None
        self._timeout_task = None

    def when(self) -> Optional[float]:
        """Return the current deadline."""
        return self._when

    def reschedule(self, when: Optional[float]):
        """Reschedule the timeout."""
        if self._current_task is None:
            raise RuntimeError("Timeout has not been entered")

        if not self._current_task.state:
            raise RuntimeError("Cannot change state of finished Timeout")

        # Create a timeout handler
        self._when = when

        if self._timeout_task is not None:
            if self._timeout_task.state is self._on_timeout:
                self._timeout_task.state = True
            self._timeout_task.cancel()

        if when is not None:
            delay = when - time.time()
            self._timeout_task = core.create_task(_timeout_wait(delay))
            self._timeout_task.state = self._on_timeout


    def expired(self) -> bool:
        """Is timeout expired during execution?"""
        if self._timeout_task is None:
            return False

        return isinstance(self._timeout_task.data, StopIteration)

    async def __aenter__(self) -> Timeout:
        if self._current_task is not None:
            raise RuntimeError("Timeout has already been entered")

        self._current_task = core.cur_task
        if self._current_task is None:
            raise RuntimeError("Timeout should be used inside a task")

        self.reschedule(self._when)

        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        # Clean up
        if self._timeout_task is not None:
            if self._timeout_task.state:
                self._timeout_task.state = True

            if self._timeout_task.cancel():
                try:
                    await self._timeout_task
                except core.CancelledError:
                    pass

        if self.expired():
            raise core.TimeoutError from exc_val

        return None

    def _on_timeout(self, task: core.Task, er):
        self._current_task.cancel()

def timeout(delay: Optional[float]) -> Timeout:
    """Timeout async context manager.

    Useful in cases when you want to apply timeout logic around block
    of code or in cases when asyncio.wait_for is not suitable. For example:

    >>> async with asyncio.timeout(10):  # 10 seconds timeout
    ...     await long_running_task()


    delay - value in seconds or None to disable timeout logic

    long_running_task() is interrupted by raising asyncio.CancelledError,
    the top-most affected timeout() context manager converts CancelledError
    into TimeoutError.
    """
    return Timeout((time.time() + delay) if delay is not None else None)


def timeout_at(when: Optional[float]) -> Timeout:
    """Schedule the timeout at absolute time.

    Like timeout() but argument gives absolute time in the same clock system
    as loop.time().

    Please note: it is not POSIX time but a time with
    undefined starting base, e.g. the time of the system power on.

    >>> async with asyncio.timeout_at(loop.time() + 10):
    ...     await long_running_task()


    when - a deadline when timeout occurs or None to disable timeout logic

    long_running_task() is interrupted by raising asyncio.CancelledError,
    the top-most affected timeout() context manager converts CancelledError
    into TimeoutError.
    """
    return Timeout(when)