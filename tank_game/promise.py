import sys
from types import TracebackType
from typing import Any, Optional, Tuple, Type, Union
from threading import Thread


_ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
_OptExcInfo = Union[_ExcInfo, Tuple[None, None, None]]


class PromisingThread(Thread):
    done: bool
    return_value: Any
    exception: _OptExcInfo

    pass_self: bool = True

    canceled: bool

    # This code was copied from threading.py:877
    def run(self) -> None:
        self.done = False
        self.return_value = None
        self.exception = None
        self.canceled = False
        ret = None
        try:
            if self._target:
                args = self._args if not self.pass_self else (self,) + self._args
                ret = self._target(*args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            self.done = True
            self.return_value = ret
            self.exception = sys.exc_info()
            del self._target, self._args, self._kwargs

    def cancel(self) -> None:
        self.canceled = True

    def join(self, timeout: Optional[float] = None) -> Any:
        super().join(timeout=timeout)
        if self.exception[0] != None:
            raise self.exception[0] from None
        return self.return_value
