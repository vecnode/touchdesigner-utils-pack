import os


def prepend_text(new_text):
    text_op = op('/project1/gui/sub_gui2/ui2/ui2/base1/text_display')
    text_op.par.text = new_text + "\n" + text_op.par.text


def update_operator_from_file(op_target, filepath):
    with open(filepath, 'r', encoding='utf-8', newline='') as file:
        content = file.read()
    lines = content.split('\n')
    op_target.storage['lines'] = lines
    op_target.par.text += content + "\n"


def onStart():
    text_display = op('/project1/gui/sub_gui2/ui2/ui2/base1/text_display')
    text_display.par.text = ""

    current_dir = os.path.abspath(os.curdir)

    op('/project1/gui/sub_gui2/ui2/ui1/w22').par.Value0 = 0
    op('/project1/gui/sub_gui2/ui2/ui1/w24').par.Value0 = "00:00:00"

    events_file = os.path.join(current_dir, "timecodes.txt")

    events_op = op('/project1/gui/sub_gui1/w20/events_text')
    events_op.par.text = ""
    update_operator_from_file(events_op, events_file)

    timer_clock = op('/project1/timer_clock')
    if timer_clock.par.active == 1:
        timer_clock.par.active = 0


def onExit():
    op('/project1/timer').par.active = 0
    op('/project1/gui/sub_gui1/w3').par.Value0 = 0

