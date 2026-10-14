"""The localhost link to the Logi plugin (docs/protocol.md).

Each client gets the current keys on connecting and again whenever they change.
Presses run one at a time on a worker thread, so a slow osascript never stalls
the link.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from . import faces, protocol
from .navigator import Navigator
from .pages import Action

log = logging.getLogger("bambukeypad")

MAX_LINE = 64 * 1024


class Bridge:
    def __init__(self, navigator: Navigator, run_action: Callable[[Action], str]):
        self._navigator = navigator
        self._run_action = run_action
        self._clients: set[asyncio.StreamWriter] = set()
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="action")

    def keys(self) -> dict:
        return protocol.keys_message(self._navigator.layout, faces.faces(self._navigator.slots()))

    async def serve(self, port: int) -> asyncio.Server:
        server = await asyncio.start_server(self._client, "127.0.0.1", port, limit=MAX_LINE)
        log.info("listening on 127.0.0.1:%d", port)
        return server

    async def _client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        log.info("plugin connected")
        self._clients.add(writer)
        try:
            writer.write(protocol.encode(self.keys()))
            await writer.drain()
            while line := await reader.readline():
                if not line.strip():
                    continue
                try:
                    message = protocol.decode(line)
                except protocol.ProtocolError as error:
                    log.warning("dropping a client that sent %s", error)
                    break
                await self.handle(message)
        except (ConnectionError, asyncio.LimitOverrunError, ValueError) as error:
            log.warning("client link error: %s", error)
        finally:
            self._clients.discard(writer)
            writer.close()
            log.info("plugin disconnected")

    async def handle(self, message: dict) -> None:
        press = protocol.press(message)
        if press is None:
            log.info("ignored a message: %.80s", message)
            return
        before = self._navigator.layout
        action = self._navigator.press(*press)
        if self._navigator.layout != before:
            await self.broadcast()
        if action is not None:
            asyncio.get_running_loop().run_in_executor(self._worker, self._run, action)

    def _run(self, action: Action) -> None:
        try:
            log.info("%s: %s", action.label, self._run_action(action))
        except Exception as error:  # an action that fails must never stop the bridge
            log.warning("%s failed: %s", action.label, error)

    async def broadcast(self) -> None:
        data = protocol.encode(self.keys())
        for writer in list(self._clients):
            try:
                writer.write(data)
                await writer.drain()
            except ConnectionError:
                self._clients.discard(writer)
