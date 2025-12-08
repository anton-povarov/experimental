# Task 2: Fix a subtle multithreading bug
#
# Provide the candidate with a snippet:
#
# import threading
#
# counter = 0
#
# def worker():
#     global counter
#     for _ in range(100_000):
#         counter += 1
#
# threads = [threading.Thread(target=worker) for _ in range(10)]
# for t in threads: t.start()
# for t in threads: t.join()
#
# print(counter)
#
# Question:
# 	1.	Explain why counter is wrong.
# 	2.	Fix the code in two different ways.
# 	3.	Discuss the tradeoffs of each fix.
#
# What this tests
# 	•	Memory model basics
# 	•	Understanding GIL vs race conditions
# 	•	Proper use of locks, atomic operations, queues


import threading
import queue
import time

n_threads = 50


def buggy_implementation():
    counter = 0

    def worker():
        nonlocal counter
        for _ in range(100_000):
            # advised by chatgpt how to force expose the bug even in the presence of GIL
            # time.sleep(0) forces releasing GIL and reacquiring afterwards
            # slows down this code by around 1000x :)
            # cnt = counter
            # time.sleep(0)
            # counter = cnt + 1
            counter += 1  # read-modify-write of a global variable without a lock or atomic

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(counter)


def fixed_implementation_1_lock():
    counter = 0

    lock = threading.Lock()

    def worker():
        nonlocal counter, lock
        for _ in range(100_000):
            with lock:  # this ads substantial overhead btw, too granular
                counter += 1

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(counter)


def fixed_implementation_2_lock_at_the_end():
    counter = 0

    lock = threading.Lock()

    def worker():
        nonlocal counter
        local_counter = 0
        for _ in range(100_000):
            local_counter += 1

        with lock:
            counter += local_counter

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(counter)


def fixed_implementation_3_return_via_queue():
    global_queue = queue.Queue()

    def worker():
        nonlocal global_queue

        local_counter = 0
        for _ in range(100_000):
            local_counter += 1

        global_queue.put(local_counter)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    counter = 0
    for i in range(len(threads)):
        counter += global_queue.get()

    print(counter)


def time_function(func):
    started = time.time()
    func()
    elapsed = time.time() - started

    print(f"executing {func.__name__} took {elapsed:.6f} seconds")


if __name__ == "__main__":
    time_function(buggy_implementation)
    time_function(fixed_implementation_1_lock)
    time_function(fixed_implementation_2_lock_at_the_end)
    time_function(fixed_implementation_3_return_via_queue)
