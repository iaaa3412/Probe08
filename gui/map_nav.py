"""Middle-mouse-drag panning, for both kinds of map in this GUI.

Every map here is either a plain tk.Canvas (WaferMapPanel and friends) or a
matplotlib axes (Wafer Builder's Die Map, the PMA wafer view, NanoZ). They
pan by completely different mechanisms, so there are two functions - but the
gesture is the same on both, which is the point: hold the middle button and
drag, anywhere, on any map.

Middle rather than left BECAUSE left is already taken on most of them - it
picks a die, types an ID, toggles a touchdown. Adding pan to it would mean
guessing whether a press was a click or the start of a drag. The middle
button is unused everywhere, so this is additive: nothing that worked
before changes.
"""
from __future__ import annotations


def bind_middle_pan_tk(canvas, on_pan=None):
    """Middle-drag panning on a tk.Canvas, via its own scan_mark/scan_dragto.

    scan_dragto only moves the view inside the scrollregion, and several of
    these canvases never set one until the first zoom - so a middle drag did
    nothing at all until you happened to scroll first. Setting it from the
    current bbox on press fixes that without changing what zoom does.
    """
    def press(event):
        if not canvas.cget("scrollregion"):
            bb = canvas.bbox("all")
            if bb:
                pad = 500
                canvas.configure(scrollregion=(bb[0] - pad, bb[1] - pad,
                                               bb[2] + pad, bb[3] + pad))
        canvas.scan_mark(event.x, event.y)
        return "break"

    def drag(event):
        canvas.scan_dragto(event.x, event.y, gain=1)
        if on_pan:
            on_pan()
        return "break"

    canvas.bind("<ButtonPress-2>", press, add="+")
    canvas.bind("<B2-Motion>", drag, add="+")


def bind_middle_pan_mpl(canvas, get_ax=None, on_pan=None):
    """Middle-drag panning on a matplotlib axes.

    Shifts the limits by the drag distance, always computed from the limits
    as they were when the button went down. Deriving each step from the
    CURRENT limits instead would compound its own rounding every motion
    event and let the map drift away under a slow drag.

    Works with an inverted y axis - which all the wafer maps use - without a
    special case: the stored ylim is simply high-to-low there, so the same
    arithmetic produces the flipped sign on its own.

    get_ax names the one pannable axes, or is left out on a figure with
    several (the NanoZ chart stacks three) to pan whichever the cursor is
    over. Either way the axes is captured on press and held for the whole
    drag, so crossing a subplot boundary mid-drag cannot switch targets.
    """
    state: dict = {}

    def press(event):
        if event.button != 2 or event.inaxes is None:
            return
        ax = get_ax() if get_ax is not None else event.inaxes
        if ax is None or event.inaxes is not ax:
            return
        state["ax"] = ax
        state["xy"] = (event.x, event.y)
        state["xlim"], state["ylim"] = ax.get_xlim(), ax.get_ylim()

    def motion(event):
        if "xy" not in state:
            return
        ax = state.get("ax")
        if ax is None:
            return
        bbox = ax.get_window_extent()
        if not bbox.width or not bbox.height:
            return
        (px, py), (x0, x1), (y0, y1) = state["xy"], state["xlim"], state["ylim"]
        dx = (px - event.x) * (x1 - x0) / bbox.width
        dy = (py - event.y) * (y1 - y0) / bbox.height
        ax.set_xlim(x0 + dx, x1 + dx)
        ax.set_ylim(y0 + dy, y1 + dy)
        canvas.draw_idle()
        if on_pan:
            on_pan()

    def release(event):
        if event.button == 2:
            state.clear()

    canvas.mpl_connect("button_press_event", press)
    canvas.mpl_connect("motion_notify_event", motion)
    canvas.mpl_connect("button_release_event", release)
