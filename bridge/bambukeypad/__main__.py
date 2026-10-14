"""python3 -m bambukeypad [serve | check | icons DIR]"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from . import config, icons, macos
from .navigator import Navigator
from .pages import HOME, Menu, all_actions
from .server import Bridge


def serve(port: int) -> None:
    async def main() -> None:
        server = await Bridge(Navigator(HOME), macos.run).serve(port)
        async with server:
            await server.serve_forever()

    asyncio.run(main())


def check() -> int:
    """Confirm every menu item in pages.py exists in the running Bambu Studio."""
    problems = 0
    for action in all_actions():
        for step in action.run:
            macos.validate(step)
            if isinstance(step, Menu):
                status = macos.menu_status(step)
                problems += status != "ok"
                print(f"{status:8} {action.label:14} {' > '.join(step.path)}")
    print("all menu items found" if not problems else f"{problems} problem(s)")
    return 1 if problems else 0


def write_icons(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name in sorted(icons.NAMES):
        (folder / f"{name}.svg").write_text(icons.svg(name), "utf-8")
    print(f"wrote {len(icons.NAMES)} icons to {folder}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="bambukeypad")
    commands = parser.add_subparsers(dest="command", required=True)
    serve_cmd = commands.add_parser("serve", help="run the bridge for the Logi plugin")
    serve_cmd.add_argument("--port", type=int, default=None)
    commands.add_parser("check", help="check every menu item against the running Bambu Studio")
    icons_cmd = commands.add_parser("icons", help="write the key icons as .svg files")
    icons_cmd.add_argument("folder", type=Path)
    args = parser.parse_args()

    if args.command == "serve":
        config.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[logging.FileHandler(config.LOG_PATH), logging.StreamHandler(sys.stderr)],
        )
        serve(args.port or config.port())
        return 0
    if args.command == "check":
        return check()
    write_icons(args.folder)
    return 0


if __name__ == "__main__":
    sys.exit(main())
