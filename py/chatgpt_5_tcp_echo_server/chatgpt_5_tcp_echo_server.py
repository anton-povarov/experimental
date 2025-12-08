# Task 5: Build an async TCP echo server with metrics
#
# Implement:
# async def echo_server(port: int):
# ...
#
# Requirements:
# 	•	No third-party libs
# 	•	Log connection lifecycle (connect/disconnect)
# 	•	Track metrics in a global object:
# 		•	active connections
# 		•	bytes received
# 		•	bytes sent
# 	•	Print metrics every 2 seconds in a background task

# What this tests
# 	•	Async networking
# 	•	Task lifecycle
# 	•	Synchronizing shared state in asyncio
# 	•	Clean architecture and shutdown handling

import contextlib
from dataclasses import dataclass
import socket
import asyncio
import logging
from typing import Awaitable, Callable

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.DEBUG,
    # datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("")


@dataclass
class Metrics:
    active_connections: int = 0
    bytes_received: int = 0
    bytes_sent: int = 0


G_metrics = Metrics()


async def handle_connection(sock: socket.socket):
    reader, writer = await asyncio.open_connection(sock=sock, limit=1024)

    try:
        G_metrics.active_connections += 1

        while True:
            line = bytes()
            try:
                line = await reader.readuntil(b"\r\n")

                G_metrics.bytes_received += len(line)

                line = line.decode("utf-8")
                line = line.strip()
            except asyncio.exceptions.IncompleteReadError:
                raise ConnectionError("connection closed by peer before sending a full message")
            except asyncio.exceptions.LimitOverrunError:
                raise ConnectionError("message is longer than limit")

            logger.info(f"received line: {line!r}")

            if line == "quit":
                return

            response = f"{line}\r\n".encode("utf-8")

            G_metrics.bytes_sent += len(response)

            writer.write(response)
            await writer.drain()

    finally:
        # force finish any pending writes (i.e. cancelled during write wait in the normal path)
        try:
            await writer.drain()
        except asyncio.CancelledError:
            await writer.drain()
            raise
        G_metrics.active_connections -= 1


async def echo_server(port: int):
    connections = dict[socket.socket, asyncio.Task[None]]()

    loop = asyncio.get_running_loop()

    async def connection_handler(sock: socket.socket, handler_func: Callable[..., Awaitable]):
        nonlocal connections

        async with contextlib.AsyncExitStack() as stack:
            stack.enter_context(sock)

            this_task = asyncio.current_task()
            assert this_task is not None
            connections[sock] = this_task
            stack.callback(lambda: connections.pop(sock, None))

            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)

            try:
                logger.info(f"connection_handler: started, sock {sock}")
                await handler_func(sock)
            except ConnectionError as e:
                logger.info(f"connection_handler: connection error: {e}")
            except asyncio.CancelledError:
                logger.warning(f"connection_handler: cancelled for sock {sock}")
                # do not propagate this exception, our handler is proactive in cancelling us
                # raise
            except Exception as e:
                logger.warning(
                    f"connection_handler: unhandled exception for sock {sock}: [{type(e)}] {e}"
                )
            finally:
                logger.info(f"connection_handler: connection closed for sock {sock}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as listen_sock:
            listen_sock.setblocking(False)
            listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            listen_sock.bind(("0.0.0.0", port))
            listen_sock.listen(1024)
            logger.info(f"waiting for connections on :{port}")

            while True:
                client_sock, client_addr = await loop.sock_accept(listen_sock)
                logger.info(f"new connection accepted from {client_addr}, sock: {client_sock}")

                asyncio.create_task(connection_handler(client_sock, handle_connection))

    except asyncio.CancelledError:
        logger.info("echo_server cancelled")

        # copy connections list as they will be removing themselves from the list as they're cancelled
        copied_connections = connections.copy()

        # first: send cancel signals to all tasks
        for sock, task in copied_connections.items():
            task.cancel()

        # second: wait for cancellation to actually happen before exiting
        for sock, task in copied_connections.items():
            try:  # connection handlers do not rethrow when cancelled, but be safe anyway
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.warning(f"unexpected exception in accept loop: {e}")
        raise
    finally:
        logger.info("echo_server exiting")


async def periodic_ticker(period: float, func: Callable):
    next_tick = asyncio.get_running_loop().time() + period

    while True:
        sleep_for = next_tick - asyncio.get_running_loop().time()
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)

        # avoid ticker skew, as `func` might take some time to run
        next_tick += period

        # function can run for longer than our tick period
        # in that case - we'll tick as soon as function completes
        # which i think is reasonable
        func()


def print_metrics():
    logger.info(f"metrics: {G_metrics}")


async def main():
    ticker = asyncio.create_task(periodic_ticker(2.0, print_metrics))

    try:
        await echo_server(3000)
    finally:
        ticker.cancel()


if __name__ == "__main__":
    asyncio.run(main())
