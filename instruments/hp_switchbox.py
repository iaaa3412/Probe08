"""HP/Agilent relay cards in the E1300A mainframe, addressed as switchboxes.

WHAT IS ACTUALLY ON THE BENCH
-----------------------------
There is ONE physical relay box: an HP 75000 Series B (E1300A) mainframe. It
holds three relay cards, and each card group is published on GPIB as its own
"switchbox" instrument at primary address 9 with a different secondary address.
Three GPIB addresses, one box - they are not three separate chassis:

    GPIB0::9::0    E1300A mainframe itself (the system instrument)
    GPIB0::9::15   SWITCHBOX, card 1: E1343A  16-ch HV relay MULTIPLEXER
    GPIB0::9::10   SWITCHBOX, card 1: E1364A  16-ch form C SWITCH
    GPIB0::9::14   SWITCHBOX, card 1: E1364A  16-ch form C SWITCH

Secondary address is the card's VXI logical address divided by 8, so SA 10/14/15
are logical addresses 80/112/120. (The E1326B manual's own example calls the
switchbox at "secondary address 14" logical address 112 - 112/8 = 14.)

Also in the mainframe, but NOT answering on GPIB: two E1326B 5.5-digit
multimeters, installed internally, broken out to banana terminals by E1326-80005
adapters. A bus scan finds no secondary address for either, so they are fitted
but not configured as instruments in the mainframe's instrument definition.

An E1343A multiplexes many channels onto one common bus; an E1364A is 16
independent form C (SPDT) relays. Do not assume a channel number means the same
thing on both.

CHANNEL NUMBERING is 00-15, and the SCPI channel spec is (@ccnn) - card number
then two-digit channel - per the HP E1343A/44A/45A/47A manual in references/:

    [ROUT:]CLOS  (@ccnn)     close channel nn on card cc
    [ROUT:]OPEN  (@ccnn)     open it
    [ROUT:]CLOS? (@ccnn)     query closure -> "1" closed, "0" open
    *RST                     opens ALL channels
    SYST:ERR?                error queue - use it to prove a channel spec is legal
"""

from instruments.gpib_base import GPIBInstrument

CHANNELS = tuple(range(16))          # E1364A channels are numbered 00-15

# From references/hpe1364 manual.pdf, all confirmed against this bench:
#
#   "the Form C Switch consists of 16 channels (channels 00 through 15)"
#   "CLOSe ... to connect the normally open (NO) terminal to the common (C)"
#   "When the relay is open, the NC terminal is connected to the C terminal"
#   "(@ccnn) where cc = switch card number (01-99) and nn = channel numbers"
#   "the module with the lowest logical address is card number 01"
#
# THE RELAYS ARE LATCHING. "Since the relays are latching, the relay remains in
# the last state during power-up or power-down. When a reset occurs, all channel
# commons (C) are connected to the corresponding normally closed (NC) contacts."
#
# So the card powers up holding whatever it was left in - all-open is NOT the
# power-on state, only the post-reset state. Nothing may assume the guarded
# state until open_all() has actually been sent. Call it before trusting
# anything, which is what the GUI panel does on connect.
_LATCHING = True

# Contact ratings, per channel: 250 V dc or 250 V ac peak (177 V ac RMS),
# 1 A dc or ac RMS non-inductive, 30 W or 40 VA. Closure takes about 15 ms,
# so the ceiling on any scan is roughly 50 Hz.
MAX_VOLTAGE_DC = 250
MAX_CURRENT_A = 1.0
CHANNEL_SETTLE_S = 0.015


# ---------------------------------------------------------------------------
# probe03 wiring - transcribed from references/probe03mapping
# ---------------------------------------------------------------------------
# WHAT THE MEASUREMENT IS. The prober lands on a 2x2 shot and the relays then
# select each of the four dies in turn. Two pins per die, eight coax in total.
# The test forces a current and measures the resulting voltage, to verify
# electrical isolation - so a high reading is the pass.
#
# On a form C relay, CLOSE energises the coil and connects Common to NO; OPEN
# de-energises it and connects Common to NC. On this card every Common carries
# one coax to the probe card, every NO goes to a multimeter terminal, and every
# NC is daisy-chained into a single node that reaches ground via CH15 NC.
#
#   CH0 NC - CH1 NC - CH2 NC - CH3 NC - CH11 NC - CH10 NC - CH9 NC - CH8 NC
#            - CH15 NC -> ground (green wires, also soldered to the coax shields)
#
# So an OPEN channel grounds its probe pin. All-open is the guarded safe state,
# not a floating state, and that is what *RST gives you.
#
# The NO side lands on the bottom E1326B's adapter terminals, in four nodes:
#
#   CH0 NO  - CH2 NO  - Input HI     CH8 NO  - CH10 NO - Current HI
#   CH1 NO  - CH3 NO  - Input LO     CH9 NO  - CH11 NO - Current LO
#
# Line that up against the coax numbers and the pattern is exact: the coax run
# 3..10 alternates HI, LO, HI, LO, ... so consecutive coax form four HI/LO
# pairs, one per die. Two of the pairs land on the meter's Input (sense)
# terminals and two on its Current (source) terminals.
#
#   die 1  coax 3 (HI) + coax 4 (LO)    CH00 + CH01    on Input HI / Input LO
#   die 2  coax 5 (HI) + coax 6 (LO)    CH02 + CH03    on Input HI / Input LO
#   die 3  coax 7 (HI) + coax 8 (LO)    CH08 + CH09    on Current HI / Current LO
#   die 4  coax 9 (HI) + coax 10 (LO)   CH10 + CH11    on Current HI / Current LO
#
# OPEN QUESTION - VERIFY BEFORE MEASURING. Two pins per die means the current
# has to be forced down the same pair the voltage is read from, so Input HI and
# Current HI must be commoned, and Input LO with Current LO. Otherwise dies 1-2
# can only be sensed (no current path) and dies 3-4 can only be driven (no
# sense), and no die is measurable. probe03mapping does not record a strap
# between those terminals. Either it exists and was not noted, or the meter
# commons them internally, or the build is missing it. A continuity check at
# the adapter settles it in seconds: Input HI to Current HI, Input LO to
# Current LO.
#
# Note the E1326B has no current-measuring function at all - the Current
# terminals are the internal current SOURCE it uses for resistance. The manual
# is also explicit that measurements taken at the meter's own terminals "must be
# configured as 4-wire" (MEAS:FRES?), because a stand-alone E1326B has no 2-wire
# mode; the strap above is what makes it electrically 2-wire while the command
# stays FRES. Ceiling is 1.048 MOhm, which may not be enough headroom for an
# isolation test - LaMP used a Keithley 2400 SMU for this, not the E1326B.

COAX_OF_CHANNEL = {0: 3, 1: 4, 2: 5, 3: 6, 8: 7, 9: 8, 10: 9, 11: 10}

# channel -> which multimeter terminal its NO contact reaches
NODE_OF_CHANNEL = {
    0: "IN_HI", 2: "IN_HI",       # Input HI    - voltage sense +
    1: "IN_LO", 3: "IN_LO",       # Input LO    - voltage sense -
    8: "CUR_HI", 10: "CUR_HI",    # Current HI  - current source +
    9: "CUR_LO", 11: "CUR_LO",    # Current LO  - current source -
}

NODE_LABELS = {
    "IN_HI": "Input HI (sense +)",
    "IN_LO": "Input LO (sense -)",
    "CUR_HI": "Current HI (source +)",
    "CUR_LO": "Current LO (source -)",
}

# Which side of the die each channel drives. One HI and one LO closed at a time
# is the whole operating rule, and it holds whether or not the Input/Current
# terminals turn out to be strapped.
POLARITY_OF_CHANNEL = {ch: ("HI" if node.endswith("HI") else "LO")
                       for ch, node in NODE_OF_CHANNEL.items()}

# The four dies of the 2x2 shot. Each is exactly two channels: one HI, one LO.
DIE_SETS = {
    1: (0, 1),      # coax 3, 4
    2: (2, 3),      # coax 5, 6
    3: (8, 9),      # coax 7, 8
    4: (10, 11),    # coax 9, 10
}

# Channels that must never be closed together. Two HI channels closed at once
# shorts two probe pins through the HI terminal - same for two LO. This is the
# one way to damage something here, so it is checked rather than trusted.
CONFLICT_GROUPS = ((0, 2, 8, 10), (1, 3, 9, 11))

# CH15's NC terminal is the ground entry point for the whole NC chain. The
# ground wire lands on the terminal, not through the contact, so operating CH15
# does not break the ground bus - but there is no reason to touch it either.
GROUND_TERMINAL_CHANNEL = 15

UNWIRED_CHANNELS = tuple(c for c in CHANNELS if c not in COAX_OF_CHANNEL)


def describe_channel(channel: int) -> str:
    """One line saying what closing this channel actually connects."""
    channel = int(channel)
    if channel == GROUND_TERMINAL_CHANNEL:
        return "CH15 - NC terminal is the ground entry for the NC bus; not switched"
    coax = COAX_OF_CHANNEL.get(channel)
    if coax is None:
        return f"CH{channel:02d} - not wired on probe03"
    return (f"CH{channel:02d} - coax {coax} -> {NODE_LABELS[NODE_OF_CHANNEL[channel]]} "
            f"[die {die_of_channel(channel)} {POLARITY_OF_CHANNEL[channel]}] "
            f"(open = coax {coax} grounded)")


def die_of_channel(channel: int):
    """Which die of the 2x2 shot this channel belongs to, or None."""
    for die, channels in DIE_SETS.items():
        if int(channel) in channels:
            return die
    return None


def conflicts_with(channel: int, already_closed) -> list:
    """Which of `already_closed` clash with `channel`.

    Two channels clash when they drive the same side of the measurement - two
    HI or two LO - because closing both shorts their probe pins together.
    """
    channel = int(channel)
    side = POLARITY_OF_CHANNEL.get(channel)
    if side is None:
        return []
    return [c for c in already_closed
            if int(c) != channel and POLARITY_OF_CHANNEL.get(int(c)) == side]


def _chan_spec(channel, card: int = 1) -> str:
    """(@ccnn) - card number then two-digit channel, per the manual."""
    return f"(@{int(card):02d}{int(channel):02d})"


class HPSwitchbox(GPIBInstrument):
    """One switchbox (a card group at a GPIB secondary address).

    `card` is the card number within the switchbox. Every unit in this mainframe
    reports a card in slot 1 and NONE in 2-4, so 1 is the default.
    """

    def __init__(self, config_key: str, card: int = 1):
        super().__init__(config_key)
        self.card = card

    def get_id(self) -> str:
        return self.query("*IDN?") or ""

    def card_type(self, slot: int = 1) -> str:
        """SYST:CTYP? - which relay card is actually in this slot."""
        return self.query(f"SYST:CTYP? {int(slot)}") or ""

    def cards(self, slots=range(1, 5)) -> list:
        """[(slot, card type)] for every slot that holds a card."""
        out = []
        for slot in slots:
            try:
                card = (self.card_type(slot) or "").strip()
            except Exception:
                break
            if card and not card.upper().startswith("NONE"):
                out.append((slot, card))
        return out

    def error(self) -> str:
        """SYST:ERR? - one entry off the error queue ('+0,"No error"' if clean)."""
        return self.query("SYST:ERR?") or ""

    def drain_errors(self, limit: int = 10) -> list:
        """Empty the error queue, returning everything that was in it."""
        found = []
        for _ in range(limit):
            entry = self.error()
            if not entry or entry.strip().startswith(("+0,", "0,")):
                break
            found.append(entry)
        return found

    # -- primitives ---------------------------------------------------------

    def close_channel(self, channel):
        self.write(f"CLOS {_chan_spec(channel, self.card)}")

    def open_channel(self, channel):
        self.write(f"OPEN {_chan_spec(channel, self.card)}")

    def open_all(self):
        """*RST - opens every channel.

        On probe03 that is also the guarded state: every open channel sits on
        its NC contact, which is tied to the grounded NC bus. Go here before
        changing routing and when finished.

        Send it at startup too. The relays latch, so the card comes up holding
        whatever it was left in - possibly with probe pins connected to the
        meter - and only a reset puts every common back on NC.
        """
        self.write("*RST")

    def read_channel(self, channel) -> bool:
        resp = self.query(f"CLOS? {_chan_spec(channel, self.card)}")
        return str(resp).strip() == "1"

    def closed_channels(self, channels=CHANNELS) -> list:
        """Which of `channels` currently read as closed. Read-only."""
        return [c for c in channels if self.read_channel(c)]

    def channel_states(self, channels=CHANNELS) -> dict:
        """{channel: is_closed} for the whole card in one pass."""
        return {c: self.read_channel(c) for c in channels}

    # -- guarded routing ----------------------------------------------------

    def close_only(self, channel, verify: bool = True) -> bool:
        """Open everything, then close exactly one channel.

        Opening first matters: closing on top of an existing closure leaves two
        coax lines on the same multimeter terminal, which shorts two probe pins
        and makes any reading meaningless.

        Returns whether the channel reads back closed (verify=False returns True
        without the readback).
        """
        self.open_all()
        self.close_channel(channel)
        if not verify:
            return True
        return self.read_channel(channel)

    def close_set(self, channels, verify: bool = True, guard: bool = True) -> dict:
        """Open everything, then close exactly `channels`.

        With guard=True (the default) a set containing two channels wired to the
        same multimeter terminal is refused before anything is switched.

        Returns {channel: reads_back_closed}.
        """
        channels = [int(c) for c in channels]
        if guard:
            for i, ch in enumerate(channels):
                clash = conflicts_with(ch, channels[i + 1:])
                if clash:
                    raise ValueError(
                        f"CH{ch:02d} and CH{clash[0]:02d} are both "
                        f"{POLARITY_OF_CHANNEL[ch]} side; closing both shorts "
                        f"coax {COAX_OF_CHANNEL[ch]} to coax {COAX_OF_CHANNEL[clash[0]]}")
        self.open_all()
        for ch in channels:
            self.close_channel(ch)
        if not verify:
            return {c: True for c in channels}
        return {c: self.read_channel(c) for c in channels}

    def route_die(self, die: int, verify: bool = True) -> dict:
        """Select one die of the 2x2 shot - closes its HI and LO channels.

        Every other channel is opened, and therefore grounded, so the three
        dies that are not being measured stay guarded.
        """
        key = int(die)
        if key not in DIE_SETS:
            raise KeyError(f"die {die!r} is not on this shot (known: {sorted(DIE_SETS)})")
        return self.close_set(DIE_SETS[key], verify=verify)

    def verify_wiring_assumptions(self) -> list:
        """Cheap read-only sanity checks. Returns a list of complaints, empty if
        the card looks like what probe03mapping describes.

        Does not switch anything - CLOS? is a query.
        """
        problems = []
        card = (self.card_type(self.card) or "").strip()
        if card and "E1364" not in card.upper():
            problems.append(f"slot {self.card} holds {card}, not an E1364A - "
                            "probe03mapping describes an E1364A form C switch")
        self.drain_errors()
        for probe in (0, 15):
            try:
                self.read_channel(probe)
            except Exception as e:
                problems.append(f"CLOS? on CH{probe:02d} failed: {e}")
                continue
            err = self.error()
            if err and not err.strip().startswith(("+0,", "0,")):
                problems.append(f"CH{probe:02d} rejected by the card: {err}")
        return problems
