from os import close
import sys
import pytest

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


def check_brackets(s: str):
    BRACKETS = {
        ")": "(",
        "]": "[",
        "}": "{",
        ">": "<",
    }

    stack = []

    for c in s:
        if c in BRACKETS.values():
            stack.append(c)
        elif c in BRACKETS.keys():
            if not stack or stack.pop() != BRACKETS[c]:
                return False

    if stack:
        return False

    return True


@pytest.mark.parametrize(
    "s, expected",
    [
        pytest.param("{}(())", True, id="nested_brackets"),
        pytest.param("{}(())[", False, id="extra_open_bracket"),
        pytest.param("()", True, id="simple_pair"),
        pytest.param("(]", False, id="mismatched_brackets"),
        pytest.param("{[()]}", True, id="complex_nested"),
        pytest.param("{[(])}", False, id="crossed_brackets"),
        pytest.param("", True, id="empty_string"),
        pytest.param("(", False, id="single_open"),
    ],
)
def test_check_brackets(s, expected):
    assert check_brackets(s) == expected


if __name__ == "__main__":
    with verbose_group("brackets") as g:
        g.verbose_call(check_brackets, "{}(())", expected=True)
        g.verbose_call(check_brackets, "{}(())[", expected=False)
