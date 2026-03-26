def timecode_to_seconds(timecode):
    hours, minutes, seconds = map(int, str(timecode).split(':'))
    return hours * 3600 + minutes * 60 + seconds


def onOffToOn(channel, sampleIndex, val, prev):
    return


def whileOn(channel, sampleIndex, val, prev):
    return


def onOnToOff(channel, sampleIndex, val, prev):
    return


def whileOff(channel, sampleIndex, val, prev):
    return


def onValueChange(channel, sampleIndex, val, prev):
    v = int(val)
    clock = op('/project1/timer_clock')
    startup = op('/project1/startup').module

    if v == 1:
        startup.prepend_text("[-] starting the timer!")
        clock.par.active = 1
        clock.par.start.pulse()
        start_tick = timecode_to_seconds(op('/project1/gui/sub_gui2/ui2/ui1/w24').par.Value0)
        clock.goTo(seconds=int(start_tick))

    if v == 0:
        startup.prepend_text("[-] stopping the timer!")
        clock.par.active = 0
        clock.par.start = 0
