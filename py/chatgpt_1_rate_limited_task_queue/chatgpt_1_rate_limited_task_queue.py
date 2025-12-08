# ✅ Task Set 1 — Concurrency, Correctness, and Design
# Task 1: Implement a rate-limited worker
# Implement a small library:
# class RateLimitedWorker:
#     def __init__(self, rate_per_second: float):
#         ...
#     async def submit(self, coro: Coroutine) -> Any:
#         """Schedules the coroutine to run while respecting the rate limit."""
# Requirements:
# 	•	Use asyncio (not threading)
# 	•	Enforce the rate limit accurately (i.e., can’t burst more than allowed)
# 	•	Ensure queue backpressure — submit() should wait if the system is overloaded
# 	•	Demonstrate usage with a short script

# What this tests
# 	•	Async primitives (queues, locks, sleep scheduling)
# 	•	Understanding of backpressure and flow control
# 	•	Clean API design

from typing import Awaitable, Callable, Coroutine
import asyncio
import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


class RateLimitedWorker:
    rate: float
    capacity: int
    tokens_left: float
    last_refill: float

    _submit_waiters: list[tuple[asyncio.Event, asyncio.Task]]  # [event, coroutine]
    _runq: asyncio.Queue[tuple[asyncio.Event, asyncio.Task]]

    def __init__(self, rate_per_second: float, capacity: int):
        self.rate = rate_per_second
        self.capacity = capacity
        self.tokens_left = self.capacity
        self.last_refill = 0

        # size 1 is a compromise here
        # 1 item will always be writeable, but it's ok, since our bucket starts full
        self._runq = asyncio.Queue(1)

        # todo: await this at some point
        asyncio.create_task(self._task_executor())

    async def submit(self, coro: Callable[..., Awaitable], timeout: float | None = None):
        """Schedules the coroutine to run while respecting the rate limit."""

        async def task_trampoline(ev: asyncio.Event, coro: Callable):
            # logger.info(f"task {asyncio.current_task().get_name()} - waiting for ev")
            await ev.wait()
            # logger.info(f"task {asyncio.current_task().get_name()} - executing coro")
            res = await coro()
            # logger.info(f"task {asyncio.current_task().get_name()} - returning res {res}")
            return res

        async def wait_for_submission(ev: asyncio.Event, task: asyncio.Task):
            try:
                # logger.info(f"waiting for queue: {coro}")
                await self._runq.put((ev, task))
                # logger.info(f"waiting for event unblock: {coro}")
                await ev.wait()
                # logger.info(f"returning from task: {task.get_name()}")
            except asyncio.CancelledError:
                task.cancel()
                try:
                    await task
                finally:
                    pass
                raise

        # block here, in case there is not enough tokens for us to run yet
        # when this is unblocked, means our task is ready to run
        ev = asyncio.Event()
        task = asyncio.create_task(task_trampoline(ev, coro))

        try:
            await asyncio.wait_for(wait_for_submission(ev, task), timeout)
            return task
        except asyncio.TimeoutError as e:
            # logger.info(f"timeout for task {task}: {e}")
            raise TimeoutError("Rate Limited timeout")

    async def _task_executor(self):
        while True:
            curr_tm = asyncio.get_running_loop().time()
            tokens_current = min(
                self.capacity, self.tokens_left + (curr_tm - self.last_refill) * self.rate
            )
            # logger.info(f"tm: {curr_tm}, tokens_current: {tokens_current}")

            if tokens_current < 1:  # don't have tokens to spend
                need_tokens = 1 - tokens_current
                wait_time = need_tokens * (1 / self.rate)
                # logger.info(f"sleeping for {wait_time}")
                await asyncio.sleep(wait_time)

            while tokens_current >= 1:
                # logger.info(f"waiting for tasks, tokens: {tokens_current}")
                ev, task = await self._runq.get()  # blocking, but don't need the result

                # logger.info(
                #     f"executor checking; cancelled: {task.cancelled()}, done: {task.done()}, task: {task}"
                # )

                if task.done():  # caller has cancelled or timed out or exception
                    continue

                # unblock task execution
                # this also unblocks the caller waiting on submit() if he hasn't cancelled yet
                ev.set()

                # token is spent now
                tokens_current -= 1

            self.tokens_left = tokens_current
            self.last_refill = curr_tm

            # spent tokens, but might've been blocked in _runq.get()
            # loop around to recheck the tokens
            continue

    def _current_token_count(self):
        curr_tm = time.time()
        return int(min(self.capacity, self.tokens_left + (curr_tm - self.last_refill) * self.rate))

    async def cancel(self):
        """
        Shuts down the rate limiter.
        Unblocks all submitters.
        Does not affect already running tasks.
        """
        # TODO: hehe
        pass


async def submit_and_get_result(worker: RateLimitedWorker, coro_id: int, coro: Callable):
    task: asyncio.Task = await worker.submit(coro)
    res = await task
    logger.info(f"worker {coro_id} task {task.get_name()} result {res}")


class RLSubmitter:
    """
    A class that enables submitting multiple tasks with rate limiting and then
    waiting for them to complete concurrently.
    Results are delivered via a queue.
    This essentially enables multiple concurrent callers to submit tasks to a RateLimitedWorker
    and fetch results independently.
    """

    _worker: RateLimitedWorker
    _queue: asyncio.Queue[asyncio.Task]  # Task instead of Future, to use get_name()
    _inprogress: set[asyncio.Task]

    def __init__(self, w: RateLimitedWorker) -> None:
        self._worker = w
        self._queue = (
            asyncio.Queue()
        )  # can be sized if we want extra backpressure from the consumer
        self._inprogress = set()

    def result_queue(self):
        return self._queue

    async def submit_with_queue(self, coro: Callable, timeout: float | None = None):
        async def worker_wrapper():
            res = await coro()
            this_task = asyncio.current_task()
            assert this_task is not None
            await self.result_queue().put(this_task)
            return res

        return await self._worker.submit(worker_wrapper, timeout)

    async def submit_and_get_future(self, coro: Callable):
        """
        Submit with backpressure from the Rate Limiter and get an awaitable future.
        """
        return await self._worker.submit(coro)

    async def shutdown(self):
        """
        Shuts down the submitter.
        Unblocks all submitters if they're blocked on submit_*().
        Cancels all running tasks (they will return an asyncio.CancelledError).
        """
        for t in self._inprogress:
            t.cancel()


async def worker_func(i: int):
    logger.info(f"i'm a worker {i}")
    return i


async def example1_submit_and_await():
    logger.info("")
    logger.info("example_1")

    worker = RateLimitedWorker(rate_per_second=1.0, capacity=5)
    for i in range(10):
        await submit_and_get_result(worker, i, lambda: worker_func(i))

    await asyncio.sleep(1)

    for i in range(5):
        await submit_and_get_result(worker, i, lambda: worker_func(i))


async def example2_submit_and_read_queue(
    submitter: RLSubmitter, submit_count: int, timeout: float | None = None
):
    logger.info("")
    logger.info("example_2")

    n_tasks = submit_count
    n_submitted = 0

    async def producer():
        nonlocal n_submitted
        try:
            for i in range(n_tasks):
                try:
                    await submitter.submit_with_queue(lambda: worker_func(i), timeout)
                    n_submitted += 1
                except TimeoutError:
                    logger.info(f"timed out while submitting task {i}, skipped")
                    continue
        finally:
            logger.info("example_2: producer exiting")

    producer_task = asyncio.create_task(producer())

    queue = submitter.result_queue()
    for i in range(n_submitted):
        fut = await queue.get()
        try:
            res = await fut
            logger.info(f"got result from task {fut.get_name()} -> {res}")
        except asyncio.CancelledError:
            logger.info(f"task {fut.get_name()} cancelled early")

    await producer_task  # prevent premature GC


async def main():
    worker = RateLimitedWorker(rate_per_second=1.0, capacity=5)
    submitter = RLSubmitter(worker)

    await example2_submit_and_read_queue(submitter, submit_count=7, timeout=0.1)
    await asyncio.sleep(3.0)
    await example2_submit_and_read_queue(submitter, submit_count=5, timeout=1.1)


if __name__ == "__main__":
    asyncio.run(main())

    # async def submit_with_queue_waiter(self, coro: Coroutine):
    #     # FIXME: this function does not support cancellation
    #     # submit can block, so we need an async waiter
    #     # waiter will put done tasks onto a queue, that will be read by the caller
    #     # waiter is modified from both the waiter and this function concurrently
    #     # it works only because we're single-threaded
    #     # would need a more complicated queues setup for multithreading
    #     async def waiter():
    #         while self._inprogress:
    #             done, pending = await asyncio.wait(self._inprogress, return_when="FIRST_COMPLETED")
    #             for t in done:
    #                 await self._queue.put(t)
    #             self._inprogress = pending

    #     task = await self._worker.submit(coro)
    #     self._inprogress.add(task)

    #     # start a new waiter if there is no existing one
    #     if len(self._inprogress) == 1:
    #         asyncio.create_task(waiter())
