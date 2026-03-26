"""Map image RGB samples to the nearest APC palette index.

Inputs expected on the Script CHOP:
  - input 0: colors CHOP with channels [r, g, b] (palette samples)
  - input 1: image CHOP with channels [r0,g0,b0,r1,g1,b1,...] (grid samples)
Output:
  - one channel per pad: n1, n2, ... with value = nearest palette index
"""

CHANNEL_PREFIX = "n"
DEFAULT_DISTANCE = float("inf")


def onSetupParameters(scriptOp):
    """Create custom parameter page (safe to call repeatedly)."""
    page = scriptOp.appendCustomPage("Custom")
    page.appendFloat("Valuea", label="Value A")
    page.appendFloat("Valueb", label="Value B")
    return


def onPulse(par):
    """TouchDesigner callback placeholder."""
    return


def _validate_inputs(colors, image):
    if colors is None or image is None:
        raise ValueError("Script CHOP requires two inputs: colors and image.")
    if int(colors.numChans) < 3:
        raise ValueError("Colors input must provide at least 3 channels (r, g, b).")
    if int(image.numChans) % 3 != 0:
        raise ValueError("Image input channel count must be divisible by 3.")


def _nearest_palette_index(colors, r, g, b):
    best_index = 0
    smallest_distance = DEFAULT_DISTANCE
    palette_size = int(colors.numSamples)

    for idx in range(palette_size):
        dr = colors[0][idx] - r
        dg = colors[1][idx] - g
        db = colors[2][idx] - b
        distance = (dr * dr) + (dg * dg) + (db * db)
        if distance < smallest_distance:
            smallest_distance = distance
            best_index = idx

    return best_index


def onCook(scriptOp):
    """Recompute output channels from current color and image inputs."""
    scriptOp.clear()
    scriptOp.numSamples = 1

    colors = scriptOp.inputs[0] if len(scriptOp.inputs) > 0 else None
    image = scriptOp.inputs[1] if len(scriptOp.inputs) > 1 else None
    _validate_inputs(colors, image)

    rows = int(image.numChans / 3)
    columns = int(image.numSamples)

    for y in range(rows):
        for x in range(columns):
            pad_index = x + (y * columns) + 1
            channel_name = CHANNEL_PREFIX + str(pad_index)
            scriptOp.appendChan(channel_name)

            image_r = image["r" + str(y)][x]
            image_g = image["g" + str(y)][x]
            image_b = image["b" + str(y)][x]
            nearest_idx = _nearest_palette_index(colors, image_r, image_g, image_b)
            scriptOp[channel_name][0] = nearest_idx
