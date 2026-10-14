"""Key faces: the label and image each slot shows."""

from __future__ import annotations

from . import icons
from .navigator import Nav, Target
from .pages import Action, Page

BLANK = {"label": "", "image": None}


def face(target: Target | None) -> dict:
    if target is None:
        return dict(BLANK)
    if target is Nav.BACK:
        return {"label": "‹ Back", "image": icons.image("back")}
    if target is Nav.MORE:
        return {"label": "More ›", "image": icons.image("more")}
    if isinstance(target, Page):
        return {"label": f"{target.name} ›", "image": icons.image(target.icon)}
    assert isinstance(target, Action)
    return {"label": target.label, "image": icons.image(target.icon)}


def faces(slots: list[Target | None]) -> list[dict]:
    return [face(target) for target in slots]
