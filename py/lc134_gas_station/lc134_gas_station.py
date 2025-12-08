# https://leetcode.com/problems/gas-station/description/
# There are n gas stations along a circular route, where the amount of gas at the ith station is gas[i].
# You have a car with an unlimited gas tank and it costs cost[i] of gas to travel from the ith station to its next (i + 1) th station.
# You begin the journey with an empty tank at one of the gas stations.
# Given two integer arrays gas and cost, return the starting gas station's index
# if you can travel around the circuit once in the clockwise direction, otherwise return -1.
# If there exists a solution, it is guaranteed to be unique.

# Оптимизированное решение

#
# Оптимизация #1
#
# давайте посчитаем - вообще глобально, можно ли обойти массив хоть откуда-то
#  это просто - сумма доступного бензина >= сумме расхода
#  если это не так - то можно даже не пытаться

#
# Оптимизация #2 (основная)
#
# рассмотрим шаг прохода по массиву последовательно
# gas =  [x1, x2, ... Xn, ...unknown_yet]
# cost = [y1, y2, ... Yn, ...unknown_yet]
#
# идем от базового индекса `b`
# предположим мы дошли до индекса n и у нас положительная сумма sum[b,n) = (gas[b,n) - cost[b,n))
# эта сумма была положительной *для любого n* - иначе мы бы туда не пришли:
#   sum[b, n) > 0
# на этом шаге:
# сумма стала отрицательной:
#   sum[b,n) - sum[b,n+1) < 0
# чтобы улучшить наше положение - нужно найти i > b, чтобы текущая сумма осталась положительной.
# существует ли i in [b,n), для которого sum[i,n) > sum[b,n)
#   такая сумма - это разность полной суммы до n и полной суммы до i
#   sum[i,n) = sum[b,n) - sum[b,i)
#   НО т.к. все суммы положительны, то - sum[b,i) > 0
# значит такая частичная сумма будет меньше полной:
#   sum[b,n) - sum[b,i) < sum[b,n) => sum[i,n) < sum[b,n)
# значит, такого i не существует!
# ! вывод
# !  - если начать поиск заново с любого i <= n, он тоже даст отрицательный результат
# !  - нужно начинать поиск с n = n + 1 (пропустить текущую пару gas(n) = Z, cost(n) = K)

#
# Оптимизация #3
#
# Если доступного бензина хватает на обход и в алгоритме выше мы дошли до конца массива.
# Плюс - утверждение из задачи, что такое решение - единственное (!)
# Тогда нет смысла крутиться в начало, там уже точно хватит.
# мы знаем, что первое число b от которого мы дошли до конца - наилучшее, потому что
#  1. каждая частичная сумма - положительна
#  2. b наименьший индекст для которого это так, т.е. b у нас "наиболее слева"
#  => если брать b1 = b+i, то сумма уменьшится или останется такой же (ибо на весь путь - хватит, мы проверили в оптимизации #1)
#  =  т.е. выход из b - оптимальный по запасу бензина
#  = начать с индекса b+i - возможно, но бензина уже может не хватить, надо проверять
# gas =  [1,2,3,4,5]
# cost = [3,4,5,1,2]
# b = 3
# n = 5 (дошли до конца, past the end)
# sum[b,n) = (4-1) + (5-2) = 6
# sum[0,n) > 0 (= 15)
# sum[0,b) = -6 (как раз)

#
# Оптимизация #4
#
# можно потоково посчитать максимумы/минимумы префиксных сумм по gas/cost
#  это не нужно, если решение единственное, но полезно, если решений несколько
#  нужны именно минимумы/максимумы, чтобы проверять "не ушло оно ниже нуля по ходу дела или нет" без просмотра всех


import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        return self._can_complete_optimized(gas, cost)

    # O(n^2)
    def _can_complete_brute_force(self, gas: List[int], cost: List[int]):
        # the amount of gas available overall needs to be sufficient to travel, given the cost
        worth_trying = sum(gas) >= sum(cost)
        if not worth_trying:
            return -1

        def can_travel_from_i(start_i: int, n_steps: int):
            current_gas = 0
            for i in range(n_steps):
                current_gas += gas[(start_i + i) % n_steps]
                move_cost = cost[(start_i + i) % n_steps]

                # can travel to the next station?
                if current_gas <= 0 or current_gas < move_cost:
                    return False

                # make the move then
                current_gas -= move_cost

            # travelled to the end, we're good
            return True

        n_steps = len(gas)
        for starting_i in range(n_steps):
            if can_travel_from_i(starting_i, n_steps):
                return starting_i
        return -1

    def _can_complete_optimized(self, gas: List[int], cost: List[int]):
        ring_len = len(gas)
        starting_i = 0
        total_gas = 0  # a prefix sum, needs to be > 0, for a way around to exist

        current_gas = 0
        current_i = 0
        while current_i < ring_len:
            fuel_diff = gas[current_i] - cost[current_i]
            total_gas += fuel_diff
            current_gas += fuel_diff
            current_i += 1

            if current_gas < 0:
                current_gas = 0
                starting_i = current_i  # no +1, already incremented

        if total_gas >= 0:  # a way exists
            return starting_i
        else:
            return -1


if __name__ == "__main__":
    with verbose_group("_can_complete_brute_force") as g:
        g.verbose_call(
            Solution()._can_complete_brute_force,
            [1, 2, 3, 4, 5],
            [3, 4, 5, 1, 2],
            expected=3,
        )
        g.verbose_call(
            Solution()._can_complete_brute_force,
            [2, 3, 4],
            [3, 4, 3],
            expected=-1,
        )
        g.verbose_call(
            Solution()._can_complete_brute_force,
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0],
            expected=0,
        )
        g.verbose_call(
            Solution()._can_complete_brute_force,
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0],
            expected=8,  # start right after 'cost=9', offset = 8
        )

    with verbose_group("_can_complete_optimized") as g:
        g.verbose_call(
            Solution()._can_complete_optimized,
            [1, 2, 3, 4, 5],
            [3, 4, 5, 1, 2],
            expected=3,
        )
        g.verbose_call(
            Solution()._can_complete_optimized,
            [2, 3, 4],
            [3, 4, 3],
            expected=-1,
        )
        g.verbose_call(
            Solution()._can_complete_optimized,
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0],
            expected=0,
        )
        g.verbose_call(
            Solution()._can_complete_optimized,
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0],
            expected=8,  # start right after 'cost=9', offset = 8
        )
