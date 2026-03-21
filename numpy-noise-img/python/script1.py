import numpy as np

NOISE_AMOUNT = 0.08
MONO_NOISE = True


def onSetupParameters(scriptOp):
    return


def onPulse(par):
    return


def onCook(scriptOp):
    inp = scriptOp.inputs[0]
    if inp is None:
        return

    img = inp.numpyArray(delayed=True, writable=True)
    if img is None:
        return

    h, w, _ = img.shape
    rgb = img[:, :, :3]

    if MONO_NOISE:
        grain = np.random.randn(h, w, 1).astype(np.float32)
        grain = np.repeat(grain, 3, axis=2)
    else:
        grain = np.random.randn(h, w, 3).astype(np.float32)

    rgb[:] = np.clip(rgb + NOISE_AMOUNT * grain, 0.0, 1.0)

    scriptOp.copyNumpyArray(img)
