import tkinter as tk

# The original VB6 forms use ScaleMode = 1 (vbTwips) and every Left/Top/Width/
# Height in the .frm files is in twips. VB6's default is 1440 twips per inch,
# and we're targeting a standard 96 DPI screen (96 px per inch), so:
#   1 twip = 96 / 1440 px = 1 / 15 px
TWIPS_PER_PIXEL = 15


def tw(twips: int) -> int:
    """Convert a VB6 twips measurement (from a .frm Left/Top/Width/Height) to pixels."""
    return round(twips / TWIPS_PER_PIXEL)


# VB6 controls left their colors as the Windows system defaults (no BackColor/
# ForeColor override appears anywhere in frmOpening.frm or frmRunTime.frm), so
# instead of hardcoding RGB values we use Tk's symbolic Windows system colors -
# this way the clone re-themes itself exactly like the original did if the
# system's classic-theme colors ever change, instead of being frozen to one
# color scheme.
VB_FORM_BG = "SystemButtonFace"
VB_FRAME_BG = "SystemButtonFace"
VB_FIELD_BG = "SystemWindow"

# VB6's own IDE default form font is "MS Sans Serif" 8.25pt. Tk font sizes are
# integers, so 8.25 -> 8 and the couple of explicit BeginProperty Font blocks
# found in the .frm files (13.5 -> 14, 8.25 -> 8) round the same way.
VB_FONT = ("MS Sans Serif", 8)
VB_FONT_BOLD = ("MS Sans Serif", 8, "bold")


class ModeAwareMixin:
    """
    Reproduces the original app's Tag = "View=XXX;" convention.

    frmOpening.frm tags txtWaferID/txtProcessStep/txtOperatorID/Label2-4/Label8
    with Tag="View=Full;", and frmRunTime.frm tags Frame1 ("Engineering Mode")
    and Frame2 ("Switch Powering") with Tag="View=Manual;". Binary Ninja's
    decompilation of frmOpening's Proc_0_10_40C480 (sub_40c480) and the tag
    comparison inside frmRunTime's Form_Load (binaryninja.txt ~line 12548,
    "__vbaStrCmp(u"Manual", ...)" / "__vbaStrCmp(u"Full", ...)") both walk
    every control on the form and compare its Tag string against the current
    run mode, calling ctrl.Visible = (tag matches, or no tag at all).

    Here that's modeled directly instead of parsing a "View=X;" string: each
    tagged widget is registered with a plain mode name ("Full" or "Manual")
    and apply_mode() shows/hides by re-placing/place_forget()-ing it.
    """

    def __init__(self):
        self._tagged_widgets = []  # list of (widget, mode_tag, place_kwargs)

    def register_view_tag(self, widget, mode_tag, left, top, width=None, height=None):
        place_kwargs = place(widget, left, top, width, height)
        self._tagged_widgets.append((widget, mode_tag, place_kwargs))

    def apply_mode(self, mode: str):
        for widget, mode_tag, place_kwargs in self._tagged_widgets:
            if mode_tag is None or mode_tag == mode:
                widget.place(**place_kwargs)
            else:
                widget.place_forget()


def place(widget, left, top, width=None, height=None):
    """place() a control using its raw VB6 twips Left/Top/Width/Height."""
    kwargs = {"x": tw(left), "y": tw(top)}
    if width is not None:
        kwargs["width"] = tw(width)
    if height is not None:
        kwargs["height"] = tw(height)
    widget.place(**kwargs)
    return kwargs


def client_size(width_twips, height_twips):
    return tw(width_twips), tw(height_twips)


def make_frame(parent, caption, left, top, width, height, font=VB_FONT_BOLD):
    """VB.Frame -> a tk LabelFrame placed at an absolute position on its parent.

    Children inside it must be placed using coordinates relative to the frame
    (exactly like VB6, where a control's Left/Top inside a Frame are already
    relative to the frame's own client origin).
    """
    frame = tk.LabelFrame(parent, text=caption, bg=VB_FRAME_BG, font=font)
    place(frame, left, top, width, height)
    return frame
