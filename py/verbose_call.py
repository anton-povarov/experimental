from dataclasses import dataclass
from typing import Any, Callable


ARG_NOT_PASSED = object()


@dataclass
class verbose_group:
    name: str
    n_calls: int = 0

    def __enter__(self):
        print(f"{self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print()

    def verbose_call(self, func: Callable, *args, expected: Any | None = ARG_NOT_PASSED, **kwargs):
        call_str = ""
        self.n_calls += 1
        call_str += f"  [{self.n_calls}] "

        # call_str += f"{func.__name__}("
        call_str += "("
        if args:
            call_str += f"{', '.join([f'{a!r}' for a in args])}"
        if kwargs:
            call_str += f", {','.join(f'{k}={v!r}' for k, v in kwargs.items())}"
        call_str += ")"
        print(f"{call_str}", end="")
        res = func(*args, **kwargs)
        res_str = f"{res!r}" if isinstance(res, str) else f"{res}"
        print(f" -> {res_str}", end="")

        if expected is not ARG_NOT_PASSED:
            if expected == res:
                print(" [OK]")
            else:
                print(f" [ERROR] (expected: {expected!r})")
        else:
            print()
