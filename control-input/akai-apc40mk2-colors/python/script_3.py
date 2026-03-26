"""Table DAT callback to broadcast one color velocity to APC notes."""

MIDI_CHANNEL = 1
FIRST_NOTE = 1
LAST_NOTE = 40
DEFAULT_VELOCITY = 0
VELOCITY_MIN = 0
VELOCITY_MAX = 127
COLOR_ID_COLUMN = "colorID"


def _clamp(value, low, high):
    return max(low, min(high, value))


def _resolve_midi_out():
    midi_op_name = parent().par.Midioutop.eval()
    if not midi_op_name:
        return None
    return op(midi_op_name)


def _read_velocity_from_table(dat):
    cell = dat[1, COLOR_ID_COLUMN] if dat is not None else None
    if cell is None:
        return DEFAULT_VELOCITY
    try:
        raw_value = int(float(cell.val))
    except Exception:
        return DEFAULT_VELOCITY
    return _clamp(raw_value, VELOCITY_MIN, VELOCITY_MAX)


def onTableChange(dat):
    midi_out = _resolve_midi_out()
    if midi_out is None:
        return

    velocity = _read_velocity_from_table(dat)
    for note in range(FIRST_NOTE, LAST_NOTE + 1):
        midi_out.sendNoteOn(MIDI_CHANNEL, note, velocity)
    return
