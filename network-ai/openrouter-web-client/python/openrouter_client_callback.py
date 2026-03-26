import json


def _sibling_op(webClientDAT, name):
    # Callbacks run where relative op() often fails; resolve from Web Client DAT.
    if webClientDAT is None:
        return None
    parent = webClientDAT.parent()
    if parent:
        r = parent.op(name)
        if r is not None:
            return r
    return webClientDAT.op(name)


def _write_cell_or_text(dat, text):
    if dat is None:
        return
    s = str(text)
    try:
        dat[0, 0] = s
    except TypeError:
        dat.text = s


def _write_output_json_table(dat, text):
    # Table DAT: assign .text so newlines become rows (not one giant [0,0] cell).
    if dat is None:
        return
    dat.text = str(text)


def onResponse(webClientDAT, statusCode, headerDict, data):
    reply = _sibling_op(webClientDAT, 'openrouter_reply')
    output_json = _sibling_op(webClientDAT, 'output_json')
    try:
        resp = json.loads(data)
        # OpenRouter (OpenAI-compatible): choices[0].message.content
        # Other chat APIs: top-level message.content
        if resp.get('choices'):
            content = resp['choices'][0].get('message', {}).get('content', '')
        else:
            content = resp.get('message', {}).get('content', '')
        _write_cell_or_text(reply, content)
        _write_output_json_table(output_json, json.dumps(resp, indent=2))
    except Exception as e:
        _write_cell_or_text(reply, 'Error: {}'.format(e))
        _write_output_json_table(output_json, data if data else str(e))
    return
