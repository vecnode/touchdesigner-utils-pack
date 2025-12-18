

# vecnode 18-12-2025

# chop - the Audio VST CHOP
# channel - the MIDI channel
# bytes - the MIDI bytes

def onReceiveMidi(chop, channel, bytes):
    print(channel, bytes)
    return
