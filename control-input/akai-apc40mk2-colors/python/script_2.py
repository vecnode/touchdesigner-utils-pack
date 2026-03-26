"""CHOP Execute DAT callback for sending MIDI note velocity."""

MIDI_CHANNEL = 1
NOTE_OFFSET = 1
VELOCITY_MIN = 0
VELOCITY_MAX = 127


def _clamp(value, low, high):
    return max(low, min(high, value))


def _resolve_midi_out():
    midi_op_name = parent().par.Midioutop.eval()
    if not midi_op_name:
        return None
    return op(midi_op_name)


def onValueChange(channel, sampleIndex, val, prev):
    midi_out = _resolve_midi_out()
    if midi_out is None:
        return

    note = int(channel.index) + NOTE_OFFSET
    velocity = _clamp(int(round(val)), VELOCITY_MIN, VELOCITY_MAX)
    midi_out.sendNoteOn(MIDI_CHANNEL, note, velocity)

