# https://habr.com/ru/articles/550088/

import bisect
from collections import defaultdict
from dataclasses import dataclass
import heapq
from tracemalloc import start
from typing import Any, Callable, List, Optional, Tuple


# хелперы, чтобы красиво выводить
def verbose_call(func: Callable, *args, prefix: str | None = None, **kwargs):
    call_str = ""
    if prefix is not None:
        call_str += f"[{prefix}]"
    call_str += f"{func.__name__}("
    if args:
        call_str += f"{', '.join([f'{a!r}' for a in args])}"
    if kwargs:
        call_str += f", {','.join(f'{k}={v!r}' for k, v in kwargs.items())}"
    call_str += ")"
    print(f"{call_str}", end="")
    res = func(*args, **kwargs)
    print(f" -> {res}")


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
        call_str += f"("
        if args:
            call_str += f"{', '.join([f'{a!r}' for a in args])}"
        if kwargs:
            call_str += f", {','.join(f'{k}={v!r}' for k, v in kwargs.items())}"
        call_str += ")"
        print(f"{call_str}", end="")
        res = func(*args, **kwargs)
        print(f" -> {res}", end="")

        if expected is not ARG_NOT_PASSED:
            if expected == res:
                print(" [OK]")
            else:
                print(f" [ERROR] (expected: {expected!r})")
        else:
            print()


# Задача 2
# Ладно, лоу-левел алгоритмическая муть позади, давайте теперь нормальную задачу,
# распарсить там что-нибудь или накидать архитектуру высоконагруженного прило...

# Дана строка (возможно, пустая), состоящая из букв A-Z: AAAABBBCCXYZDDDDEEEFFFAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBB
# Нужно написать функцию RLE, которая на выходе даст строку вида: A4B3C2XYZD4E3F3A6B28
# И сгенерирует ошибку, если на вход пришла невалидная строка.
# Пояснения: Если символ встречается 1 раз, он остается без изменений;
# Если символ повторяется более 1 раза, к нему добавляется количество повторений.


def rle_encode(input: str) -> str:
    if len(input) < 2:
        return input

    output: str = ""

    last_char = input[0]
    last_count = 1
    for i in range(1, len(input)):
        if input[i] == last_char:
            last_count += 1
        else:
            output += f"{last_char}{last_count}"
            last_char = input[i]
            last_count = 1

    output += f"{last_char}{last_count}"
    return output


with verbose_group("rle_encode") as g:
    g.verbose_call(
        rle_encode,
        "AAAABBBCCXYZDDDDEEEFFFAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        expected="A4B3C2X1Y1Z1D4E3F3A6B28",
    )

# Задача 3
# Дан список интов, повторяющихся элементов в списке нет.
# Нужно преобразовать это множество в строку, сворачивая соседние по числовому ряду числа в диапазоны. Примеры:
# [1,4,5,2,3,9,8,11,0] => "0-5,8-9,11"
# [1,4,3,2] => "1-4"
# [1,4] => "1,4"


def collapse_intervals(nums: List[int]) -> str:
    nums = sorted(nums)

    output = []

    while nums:
        # print(f"nums: {nums}")

        i = 0
        while i < len(nums) - 1:
            if nums[i + 1] != nums[i] + 1:
                break
            i += 1

        s = f"{nums[0]}"
        if i != 0:
            s += f"-{nums[i]}"
        output.append(s)

        nums = nums[i + 1 :]

    return ",".join(output)


with verbose_group("collapse_intervals") as g:
    g.verbose_call(collapse_intervals, [1, 4, 5, 2, 3, 9, 8, 11, 0], expected="0-5,8-9,11")
    g.verbose_call(collapse_intervals, [1, 4, 3, 2], expected="1-4")
    g.verbose_call(collapse_intervals, [1, 4], expected="1,4")

# Задача 4
# Я, признаюсь, был готов ко всему, но не к этому:
#
# Дан массив из нулей и единиц.
# Нужно определить, какой максимальный по длине подинтервал единиц можно получить, удалив ровно один элемент массива.
# Пример: [0, 0, 1, 1, 0, 1, 1, 0] -> 4


def interval_after_removing_one_elt(input: List[int]) -> int:
    # antoxa: я забил решать
    # идея1:
    #   идем по массиву (откуда? ну например, с начала)
    #   считаем единички, если встретился 0, скипаем (--счетчик_скипов >= 0) и идем дальше считать
    #   получаем ответ, сравниваем с текущим максимумом, обновляем если больше.
    #   дальше надо понять, откуда можно делать второй прогон - вроде бы должно быть можно с места последнего скипа?
    return 0


# Задача 5
# Даны даты заезда и отъезда каждого гостя.
# Для каждого гостя дата заезда строго раньше даты отъезда
#  (то есть каждый гость останавливается хотя бы на одну ночь).
# В пределах одного дня считается, что сначала старые гости выезжают, а затем въезжают новые.
# Найти максимальное число постояльцев, которые одновременно проживали в гостинице
#  (считаем, что измерение количества постояльцев происходит в конце дня).
# sample = [ (заезд, отъезд), ... ]
# sample = [ (1, 2), (1, 3), (2, 4), (2, 3)]


# this function uses linear extra space
def max_concurrent_guests_v1(inputs: List[Tuple[int, int]], day: int) -> int:
    total_days = 0
    for pair in inputs:
        total_days = max(total_days, *pair)

    # calc how occupancy changes each day
    occupancy_change = [0] * (total_days + 1)
    for start, end in inputs:
        occupancy_change[start] += 1
        occupancy_change[end] -= 1

    # calculate prefix sum up to day x
    res = 0
    for i in range(day + 1):
        res += occupancy_change[i]

    return res


with verbose_group("max_concurrent_guests_v1") as g:
    g.verbose_call(max_concurrent_guests_v1, [(1, 2), (1, 3), (2, 4), (2, 3)], 1, expected=2)
    g.verbose_call(max_concurrent_guests_v1, [(1, 2), (1, 3), (2, 4), (2, 3)], 4, expected=0)


# Задача 6
# Sample Input ["eat", "tea", "tan", "ate", "nat", "bat"]
# Sample Output [ ["ate", "eat", "tea"], ["nat", "tan"], ["bat"] ]
# Т.е. сгруппировать слова по "общим буквам".
# antoxa: это group anagrams из leetcode


def group_anagrams(input: List[str]) -> List[List[str]]:
    d = defaultdict(list[str])

    for s in input:
        d["".join(sorted(s))].append(s)

    return list(d.values())


# prints [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
with verbose_group("group_anagrams") as g:
    g.verbose_call(group_anagrams, ["eat", "tea", "tan", "ate", "nat", "bat"])

# Задача 7
# Слияние отрезков:
# Вход: [1, 3] [100, 200] [2, 4]
# Выход: [1, 4] [100, 200]


def merge_intervals(input: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if len(input) <= 1:
        return input

    sorted_by_start = sorted(input, key=lambda x: x[0])

    output = [sorted_by_start[0]]

    # for i in range(1, len(sorted_by_start)):
    for interval in sorted_by_start[1:]:
        # print(f"s: {sorted_by_start}")
        # print(f"i: {interval}")
        # print(f"o: {output}")
        # can merge right
        if output[-1][1] >= interval[0]:
            # update this range
            output[-1] = (
                # min(output[-1][0], interval[0]),  # not needed as we've sorted intervals by start
                output[-1][0],
                max(output[-1][1], interval[1]),
            )
            # remove the next range, we've just consumed it
        else:
            output.append(interval)

    return output


with verbose_group("merge_intervals") as g:
    g.verbose_call(merge_intervals, [(1, 3), (100, 200), (2, 4)], expected=[(1, 4), (100, 200)])
    g.verbose_call(
        merge_intervals,
        [(1, 3), (100, 200), (2, 4), (3, 6)],
        expected=[(1, 6), (100, 200)],
    )
    g.verbose_call(
        merge_intervals,
        [(1, 3), (100, 200), (2, 4), (3, 6), (50, 250)],
        expected=[(1, 6), (50, 250)],
    )
    g.verbose_call(
        merge_intervals,
        [(1, 3), (100, 200), (2, 4), (3, 6), (-1, 250)],
        expected=[(-1, 250)],
    )


# Задача 8
# Время собеседования подходит к концу,
# но всё-таки можно ещё поболтать про кодинг и поспрашивать практические вопросы,
# например по Django или SqlAlchemy:
#
# Дан массив точек с целочисленными координатами (x, y).
# Определить, существует ли вертикальная прямая, делящая точки на 2 симметричных относительно этой прямой множества.
# Note: Для удобства точку можно представлять не как массив [x, y], а как объект {x, y}


@dataclass
class point:
    x: int
    y: int


# returns a coord for the midpoint curve, or -1 if none exists
def find_midpoint_line_x(points: List[point]) -> float | None:
    # надо понять, что такое "симметричиных относильно прямой"
    # будем считать, что это когда точки на одной высоте - находятся на парно одинаковых расстояниях
    # т.е. для каждой точки слева - есть точка справа на такой же высоте Y и X симметричино отраженной относительно прямой

    # в решении из статьи юзается другой подход
    # 1. сначала находим среднее между всеми x-ами (не знаю, то ли делает mean(point.x for point in points))
    # 2. потом идем по всем точкам и ищем - есть ли у нас такая, с иксом отраженным относительно серединки из #1 выше
    # 3. работы с флоатами в том решении нет, хз

    d = defaultdict(list[int])  # height -> list of points
    for p in points:
        d[p.y].append(p.x)

    midpoint_x = None

    for y, plist in d.items():
        if len(plist) < 2 or len(plist) % 2 != 0:
            return None

        plist = sorted(plist)

        # we're going to be dealing with float distances now, so here's our epsilon
        eps = 0.000001

        # the line is in the middle between two most distant points
        # we've sorted the list, so they should be the fist and last elements
        candidate_x = (plist[-1] - plist[0]) / 2

        # quickly check with midpoint from the previous layer if we have one
        if midpoint_x and abs(candidate_x - midpoint_x) > eps:
            return None

        # for all other pairs, make sure their middle is the same
        for i in range(1, len(plist) // 2):
            # distance from points on both sides to the candidate should be equal
            # written out more verbosely to make it easier to read
            left_d = candidate_x - plist[-i - 1]
            right_d = plist[i] - candidate_x

            # respect the floats, baby
            if abs(left_d - right_d) >= eps:
                return None

        if not midpoint_x or abs(candidate_x - midpoint_x) < eps:
            midpoint_x = candidate_x

    return midpoint_x


with verbose_group("find_midpoint_line_x") as g:
    g.verbose_call(find_midpoint_line_x, [point(1, 2)], expected=None)
    g.verbose_call(
        find_midpoint_line_x, [point(1, 2), point(3, 2), point(0, 2), point(4, 2)], expected=2.0
    )


# Задание 9
# Даны две строки.
# Написать функцию, которая вернёт True, если из первой строки можно получить вторую,
#  совершив не более 1 изменения (== удаление / замена символа).
def can_transform_string(input1: str, input2: str) -> bool:
    len_diff = len(input1) - len(input2)
    if abs(len_diff) > 1:
        return False

    if len_diff == 0:  # заменяем символы
        n_diff_chars = 0
        for i in range(len(input1)):
            if input1[i] != input2[i]:
                n_diff_chars += 1
        return n_diff_chars == 1

    # меняем местами строки так, чтобы всегда надо было искать удаление символа
    # так удобнее, не нужно догадываться какой символ добавлять
    if len_diff == -1:
        input1, input2 = input2, input1

    assert len(input1) == (len(input2) + 1)
    for i in range(len(input1)):
        # удаляем текущий символ и смотрим совпадают ли строки
        if str(input1[:i] + input1[i + 1 :]) == input2:
            return True

    return False


with verbose_group("can_transform_string") as g:
    g.verbose_call(can_transform_string, "abc", "abcd", expected=True)
    g.verbose_call(can_transform_string, "abcE", "abcd", expected=True)
    g.verbose_call(can_transform_string, "abE", "abcd", expected=False)


# Дан список интов и число-цель. Нужно найти такой range, чтобы сумма его элементов давала число-цель.
# elements = [1, -3, 4, 5]
# target = 9
# result = range(2, 4) # because elements[2] + elements[3] == target
# antoxa: idea (borrowed somewhere)
#  сумма внутри range [b, e) - это sum [0,e) - sum [0,b)
#  идем по массиву вперед, записываем в хешик: KEY{частичная сумма [0,x)} -> VALUE{x}
#  на каждом шаге Y - смотрим в хешик, существует ли запись для (sum[0,Y) - target_value)
#  если да, то в value там - для какого префикса X эта сумма
#  соответственно наш ответ [X, Y)
#  (нужно только быть аккуратным с оффсетами, включает или нет)
def find_range_for_sum(nums: List[int], target: int) -> Tuple[int, int]:
    partial_sums = dict[int, int]()  # sum -> offset, such that partial_sum[0,x) = sum
    curr_sum = 0
    for i, val in enumerate(nums):
        curr_sum += val
        partial_sums[curr_sum] = i + 1

        sum_diff = curr_sum - target
        if sum_diff in partial_sums:
            return (partial_sums[sum_diff], i + 1)
    return (0, 0)


with verbose_group("find_range_for_sum") as g:
    g.verbose_call(find_range_for_sum, [1, -3, 4, 5], 9, expected=(2, 4))
    g.verbose_call(find_range_for_sum, [1, -3, 4, 5], 5, expected=(3, 4))

######################################################################
# Задачки, надерганные из коментариев


# эффективно удалить нули из массива
# https://habr.com/ru/articles/550088/#comment_22885586
# antoxa: options
# 0: move with two pointers, copying everything that is not zero to front, then subslice
# 1: copy everything that is not zero to output
# 2: move all zeroes to the end of array (i.e. std::partition, if we can change element order)
def remove_zeroes_v1(nums: List[int]):
    out = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[out] = nums[i]
            out += 1
    return nums[:out]


with verbose_group("remove_zeroes_v1") as g:
    g.verbose_call(remove_zeroes_v1, [0, 0, 0, 0, 0, 0, 1], expected=[1])
    g.verbose_call(remove_zeroes_v1, [0, 1, 0, 0, 0, 0, 1], expected=[1, 1])


# https://habr.com/ru/articles/550088/#comment_22882500
# найти через сколько рукопожатий знакомы два человека в большой социальной сети типа G+.
def find_handshake_count():
    # TODO
    pass


# https://habr.com/ru/articles/550088/#comment_22887904
# Найти в массиве подпоследовательность с максимальной суммой.
# решение придумал через prefix суммы + предвычисление минимальных в интервале за один проход
# довольно громоздко, оказывается есть решение получше - Kadane's Algorithm (ниже функция)
# https://neetcode.io/courses/advanced-algorithms/0
def find_max_sum_subarray(nums: List[int]) -> List[int]:
    # for index i, stores prefix_sum of [0, i)
    prefix_sums = [0]

    # индексы минимальных значений в prefix_sums
    # т.е. по индексу i лежит индекс минимального значения в диапазоне prefix_sums[0,i)
    prefix_min_indexes = [0]

    res_sum = None
    res_range = []

    # считаем префиксные суммы
    sum = 0
    min_sum_index = 0
    for i in range(len(nums)):
        sum += nums[i]
        prefix_sums.append(sum)
        if sum <= prefix_sums[min_sum_index]:
            min_sum_index = i + 1
        prefix_min_indexes.append(min_sum_index)

    # print()
    # print(f"prefix_sums = {prefix_sums}")
    # print(f"min_indexes = {prefix_min_indexes}")

    for i in range(len(nums)):
        min_index = prefix_min_indexes[i]

        # print(f"i = {i}, min_index = {min_index}")
        interval = nums[min_index : i + 1]
        interval_sum = prefix_sums[i + 1] - prefix_sums[min_index]
        # print(f"interval = {interval}, interval_sum = {interval_sum}")

        if res_sum is None or res_sum < interval_sum:
            res_sum = interval_sum
            res_range = interval

    return res_range


# Kadane's doesn't always yield the shortest subarray, like the prefix sums actually do
# the modification to achieve that is to trim the best one down from the front
def find_max_sum_subarray_kadane(nums: List[int]) -> List[int]:
    if len(nums) <= 1:
        return nums

    best_sum = nums[0]
    best_interval = []

    curr_sum = nums[0]
    start_i = 0

    for i in range(1, len(nums)):
        if curr_sum < 0:
            curr_sum = 0
            start_i = i

        curr_sum += nums[i]

        if curr_sum > best_sum:
            best_sum = curr_sum
            best_interval = nums[start_i : i + 1]

    # try to make the array shorter
    # trim front of the array, if there is a shorter array with the same sum
    # do not use extra space, as it will dominate the overall memory complexity of this function then
    # so just a forward pass, since kadane will not extend the interval forward, only the start can lag
    # i.e. [-1, 0, 1, 5] is possible here (last elt heavy), but not [5, 0, 0, -1, 1] (first elt heavy)
    curr_sum = 0
    start_i = None
    for i in range(len(best_interval)):
        curr_sum += best_interval[i]
        if curr_sum == 0:
            start_i = i

    return best_interval[start_i + 1 if start_i is not None else 0 :]


def find_max_sum_subarray_kadane_just_sum(nums: List[int]) -> int:
    if len(nums) <= 1:
        return sum(nums)

    best_sum = nums[0]
    curr_sum = nums[0]

    for i in range(1, len(nums)):
        if curr_sum < 0:
            curr_sum = 0

        curr_sum += nums[i]
        best_sum = max(best_sum, curr_sum)

    return best_sum


with verbose_group("find_max_sum_subarray") as g:
    g.verbose_call(find_max_sum_subarray, [1, 0, -1, 5, -50, 2], expected=[5])
    g.verbose_call(find_max_sum_subarray, [1, 1, -1, 5, -50, 2], expected=[1, 1, -1, 5])
    g.verbose_call(find_max_sum_subarray, [1, -5, 3, 2], expected=[3, 2])
    g.verbose_call(find_max_sum_subarray, [1, 1, 1, 1], expected=[1, 1, 1, 1])
    g.verbose_call(find_max_sum_subarray, [1, -1, 1, -1], expected=[1])
    g.verbose_call(find_max_sum_subarray, [1, -1, 1, 2], expected=[1, 2])
    g.verbose_call(find_max_sum_subarray, [0, 0, 0, 0], expected=[0])
    g.verbose_call(find_max_sum_subarray, [-5, 9, -2, -2, 10, 7, -1], expected=[9, -2, -2, 10, 7])
    g.verbose_call(find_max_sum_subarray, [6, -2, 7], expected=[6, -2, 7])
    g.verbose_call(find_max_sum_subarray, [1, -3, 7], expected=[7])

with verbose_group("find_max_sum_subarray_kadane") as g:
    g.verbose_call(find_max_sum_subarray_kadane, [1, 0, -1, 5, 0, 0, -50, 2], expected=[5])
    g.verbose_call(find_max_sum_subarray_kadane, [1, 0, -1, 5, -50, 2], expected=[5])
    g.verbose_call(find_max_sum_subarray_kadane, [1, 1, -1, 5, -50, 2], expected=[1, 1, -1, 5])
    g.verbose_call(
        find_max_sum_subarray_kadane, [-5, 9, -2, -2, 10, 7, -1], expected=[9, -2, -2, 10, 7]
    )
    g.verbose_call(find_max_sum_subarray_kadane, [6, -2, 7], expected=[6, -2, 7])
    g.verbose_call(find_max_sum_subarray_kadane, [1, -3, 7], expected=[7])

with verbose_group("find_max_sum_subarray_kadane_just_sum") as g:
    g.verbose_call(find_max_sum_subarray_kadane_just_sum, [-5, 9, -2, -2, 10, 7, -1], expected=22)
    g.verbose_call(find_max_sum_subarray_kadane_just_sum, [6, -2, 7], expected=11)
    g.verbose_call(find_max_sum_subarray_kadane_just_sum, [1, -3, 7], expected=7)
