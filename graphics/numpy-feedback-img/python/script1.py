import numpy as np

# Fraction of previous frame to mix in (higher = longer trails / stronger feedback).
FEEDBACK = 0.88

# Optional: absolute path to source TOP (e.g. "/project1/moviefilein1"). None = input 0.
SOURCE_TOP_PATH = None

# Previous blended RGB per Script TOP path — kept in Python so TD does not treat feedback
# as an operator self-dependency (store/fetch on scriptOp can trigger "Cook dependency loop").
_PREV_RGB_BY_PATH = {}


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def _source_top(scriptOp):
    if SOURCE_TOP_PATH:
        o = op(SOURCE_TOP_PATH)
        if o is not None:
            return o, True
    inp = scriptOp.inputs[0]
    if inp is None:
        return None, False
    return inp, False


def onCook(scriptOp):
    # Blend current video input with last cooked frame in numpy for image feedback.
    top, use_direct_path = _source_top(scriptOp)
    if top is None:
        return

    # Current frame only — delayed=True ties to TD's frame-delay buffer and can look like
    # feedback on the same input in the cook graph.
    if use_direct_path:
        raw = top.numpyArray(delayed=False, writable=False)
        if raw is None:
            return
        img = np.array(raw, copy=True)
    else:
        img = top.numpyArray(delayed=False, writable=True)
        if img is None:
            return

    h, w, _ = img.shape
    rgb = np.asarray(img[:, :, :3], dtype=np.float32)

    path = scriptOp.path
    prev = _PREV_RGB_BY_PATH.get(path)
    if prev is not None and prev.shape == rgb.shape:
        rgb[:] = np.clip(
            FEEDBACK * prev + (1.0 - FEEDBACK) * rgb,
            0.0,
            1.0,
        )

    _PREV_RGB_BY_PATH[path] = rgb.copy()

    if img.dtype == np.uint8:
        img[:, :, :3] = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    else:
        img[:, :, :3] = rgb

    scriptOp.copyNumpyArray(img)
