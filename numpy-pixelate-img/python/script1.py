"""
TouchDesigner Python TOP — pixelate (mosaic).

Each cell is the mean RGB of a square block; the result is upscaled by repeating
that color. Vectorized numpy only; onCook → copyNumpyArray.
"""

import numpy as np


def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage("Pixelate")
    p = page.appendInt("Blocksize", label="Block size (px)")
    p.default = 12
    p.min = 1
    p.max = 2048
    p = page.appendFloat("Original", label="Blend with original")
    p.default = 0.0
    p.min = 0.0
    p.max = 1.0
    p = page.appendToggle("Grid", label="Grid lines")


def onPulse(par):
    return


def _pixelate_rgb(rgb: np.ndarray, block_size: int) -> np.ndarray:
    """Float RGB HxWx3 in [0,1], same shape out."""
    h, w, _ = rgb.shape
    bs = max(1, min(int(block_size), h, w))
    if bs == 1:
        return rgb

    hb = h // bs
    wb = w // bs
    if hb < 1 or wb < 1:
        return rgb

    bh, bw = hb * bs, wb * bs
    trimmed = rgb[:bh, :bw, :]
    blocks = trimmed.reshape(hb, bs, wb, bs, 3).mean(axis=(1, 3))
    out = np.repeat(np.repeat(blocks, bs, axis=0), bs, axis=1)

    if bh < h or bw < w:
        out = np.pad(
            out,
            ((0, h - bh), (0, w - bw), (0, 0)),
            mode="edge",
        )
    return out


def _par_float(scriptOp, name: str, default: float) -> float:
    try:
        return float(getattr(scriptOp.par, name))
    except Exception:
        return default


def _par_int(scriptOp, name: str, default: int) -> int:
    try:
        return int(getattr(scriptOp.par, name))
    except Exception:
        return default


def _par_bool(scriptOp, name: str, default: bool) -> bool:
    try:
        return bool(getattr(scriptOp.par, name))
    except Exception:
        return default


def onCook(scriptOp):
    inp = scriptOp.inputs[0]
    if inp is None:
        return

    img = inp.numpyArray(delayed=True, writable=False)
    if img is None:
        return

    h, w, c = img.shape
    rgb = np.asarray(img[:, :, :3], dtype=np.float32)

    bs_user = _par_int(scriptOp, "Blocksize", 12)
    bs = max(1, min(int(bs_user), h, w))
    blend = float(np.clip(_par_float(scriptOp, "Original", 0.0), 0.0, 1.0))
    show_grid = _par_bool(scriptOp, "Grid", False)

    pix = _pixelate_rgb(rgb, bs_user)
    pix = np.clip(pix, 0.0, 1.0)

    if show_grid and bs >= 2:
        pix[bs::bs, :, :] *= 0.62
        pix[:, bs::bs, :] *= 0.62

    if blend > 0.0:
        pix = (1.0 - blend) * pix + blend * rgb

    out = np.empty_like(img, dtype=img.dtype)
    if np.issubdtype(out.dtype, np.integer):
        out[:, :, :3] = np.clip(np.round(pix * 255.0), 0, 255).astype(
            out.dtype, copy=False
        )
    else:
        out[:, :, :3] = pix.astype(out.dtype, copy=False)
    if c > 3:
        out[:, :, 3:] = img[:, :, 3:]

    scriptOp.copyNumpyArray(out)
