from bambukeypad.navigator import SLOT_COUNT, Nav, Navigator
from bambukeypad.pages import EDIT, FILE, HOME, Action, Keys, Page


def act(n: int) -> Action:
    return Action(f"A{n}", "slice", Keys("a"))


def test_home_fills_nine_keys_with_no_back():
    nav = Navigator(HOME)
    assert nav.slots() == list(HOME.items)
    assert Nav.BACK not in nav.slots()


def test_page_key_opens_page_with_back_first():
    nav = Navigator(HOME)
    slot = HOME.items.index(EDIT)
    assert nav.press(slot, nav.layout) is None
    slots = nav.slots()
    assert slots[0] is Nav.BACK
    assert slots[1:1 + len(EDIT.items)] == list(EDIT.items)


def test_back_returns_to_parent():
    nav = Navigator(HOME)
    nav.press(HOME.items.index(EDIT), nav.layout)
    nav.press(0, nav.layout)
    assert nav.page is HOME
    assert nav.slots() == list(HOME.items)


def test_action_key_returns_action_and_stays_put():
    nav = Navigator(HOME)
    layout = nav.layout
    assert nav.press(1, layout) is HOME.items[1]
    assert nav.layout == layout
    assert nav.page is HOME


def test_stale_layout_is_ignored():
    nav = Navigator(HOME)
    stale = nav.layout
    nav.press(HOME.items.index(EDIT), stale)
    assert nav.press(1, stale) is None  # slot 1 meant Slice on Home, now Move
    assert nav.page is EDIT


def test_out_of_range_slot_is_ignored():
    nav = Navigator(HOME)
    assert nav.press(SLOT_COUNT, nav.layout) is None
    assert nav.press(-1, nav.layout) is None


def test_blank_key_does_nothing():
    small = Page("Root", "home", [Page("Sub", "file", [act(1)])])
    nav = Navigator(small)
    nav.press(0, nav.layout)
    layout = nav.layout
    assert nav.slots()[5] is None
    assert nav.press(5, layout) is None
    assert nav.layout == layout


def test_overflowing_page_gets_more_and_wraps():
    nav = Navigator(HOME)
    nav.press(HOME.items.index(FILE), nav.layout)  # 9 items under a Back key
    first = nav.slots()
    assert first[0] is Nav.BACK and first[-1] is Nav.MORE
    assert first[1:8] == list(FILE.items[:7])
    nav.press(8, nav.layout)
    second = nav.slots()
    assert second[0] is Nav.BACK and second[-1] is Nav.MORE
    assert second[1:3] == list(FILE.items[7:])
    assert second[3:8] == [None] * 5
    nav.press(8, nav.layout)
    assert nav.slots() == first


def test_root_overflow_has_more_without_back():
    root = Page("Root", "home", [act(n) for n in range(12)])
    nav = Navigator(root)
    slots = nav.slots()
    assert slots[:8] == list(root.items[:8]) and slots[8] is Nav.MORE
    nav.press(8, nav.layout)
    assert nav.slots()[:4] == list(root.items[8:])


def test_exactly_full_subpage_has_no_more():
    nav = Navigator(HOME)
    nav.press(HOME.items.index(EDIT), nav.layout)
    assert len(EDIT.items) == SLOT_COUNT - 1
    assert Nav.MORE not in nav.slots()


def test_layout_changes_on_every_move_and_home_resets():
    nav = Navigator(HOME)
    seen = {nav.layout}
    nav.press(HOME.items.index(FILE), nav.layout)
    seen.add(nav.layout)
    nav.press(8, nav.layout)
    seen.add(nav.layout)
    assert len(seen) == 3
    nav.home()
    assert nav.page is HOME and nav.screen == 0 and nav.layout not in seen
    layout = nav.layout
    nav.home()  # already home: nothing changes
    assert nav.layout == layout
