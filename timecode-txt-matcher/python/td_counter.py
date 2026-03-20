def seconds_to_timecode(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    return "{:02}:{:02}:{:02}".format(hours, minutes, sec)


def retrieve_lines_by_timecode(store_op, timecode):
    lines = store_op.storage.get('lines', [])
    matching = [line for line in lines if line.startswith(timecode)]
    if len(matching) == 1:
        return matching[0]
    if matching:
        return matching
    return None


def event_trigger(store_op, timecode, action=None):
    matched_line = retrieve_lines_by_timecode(store_op, timecode)
    if not matched_line:
        return
    if action:
        action(matched_line)
    else:
        print("")


def custom_action(matched_line):
    startup = op('/project1/startup').module
    if isinstance(matched_line, list):
        for line in matched_line:
            startup.prepend_text("Found a match: {}".format(line))
    else:
        startup.prepend_text("Found a match: {}".format(matched_line))


def onInitialize(timerop):
    return 0


def onReady(timerop):
    return


def onStart(timerop):
    return


def onTimerPulse(timerop, segment):
    return


def whileTimerActive(timerop, segment, cycle, fraction):
    return


def onSegmentEnter(timerop, segment, interrupt):
    return


def onSegmentExit(timerop, segment, interrupt):
    return


def onCycleEndAlert(timerop, segment, cycle, alertSegment, alertDone, interrupt):
    return


def onCycle(timerop, segment, cycle):
    if cycle % 1 != 0:
        return

    timer_clock = op('/project1/timer_clock')
    main_counter = timer_clock['cycles']
    formatted_timecode = seconds_to_timecode(main_counter)

    startup = op('/project1/startup').module
    startup.prepend_text(formatted_timecode)

    op('/project1/gui/sub_gui2/ui2/ui1/w24').par.Value0 = formatted_timecode

    event_storage_op = op('/project1/gui/sub_gui1/w20/events_text')
    event_trigger(event_storage_op, formatted_timecode, action=custom_action)


def onDone(timerop, segment, interrupt):
    return
