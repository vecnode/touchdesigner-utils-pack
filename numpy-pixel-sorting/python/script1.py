"""
TouchDesigner Python TOP — pixel sorting

Same numpy TOP flow: input numpyArray → process RGB in float32 → copyNumpyArray.

Contiguous segments where the sort key is above `Threshold` are reordered by that
key (descending). Axis picks row-wise (horizontal streaks) or column-wise (vertical).

Custom parameters are not auto-synced when you edit this file: select the Script TOP,
open its Setup page, and press "Setup Parameters" so the Pixelsort page appears.
"""

import numpy as np


def onSetupParameters(scriptOp):
    try:
        scriptOp.destroyCustomPars()
    except Exception:
        pass
    page = scriptOp.appendCustomPage("Pixelsort")
    p = page.appendFloat("Threshold", label="Threshold")
    p.default = 0.25
    p.min = 0.0
    p.max = 1.0
    p = page.appendInt("Axis", label="Axis (0=H 1=V)")
    p.default = 0
    p.min = 0
    p.max = 1
    p = page.appendInt("Sortkey", label="Key (0=luma 1=R 2=G 3=B)")
    p.default = 0
    p.min = 0
    p.max = 3
    p = page.appendFloat("Original", label="Blend with original")
    p.default = 0.0
    p.min = 0.0
    p.max = 1.0


def onPulse(par):
    return


def _sort_key(rgb: np.ndarray, key_mode: int) -> np.ndarray:
    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]
    if key_mode == 1:
        return r
    if key_mode == 2:
        return g
    if key_mode == 3:
        return b
    return 0.299 * r + 0.587 * g + 0.114 * b


def _sort_segments_1d(keys_1d: np.ndarray, rgb_2d: np.ndarray, threshold: float) -> None:
    """Sort each contiguous run where keys >= threshold; descending by key. In-place on rgb_2d."""
    mask = keys_1d >= threshold
    if not np.any(mask):
        return
    padded = np.concatenate(([False], mask, [False]))
    d = np.diff(padded.astype(np.int8))
    starts = np.where(d == 1)[0]
    ends = np.where(d == -1)[0]
    for s, e in zip(starts, ends):
        seg_k = keys_1d[s:e]
        seg_rgb = rgb_2d[s:e, :]
        order = np.argsort(-seg_k)
        rgb_2d[s:e, :] = seg_rgb[order]


def _pixel_sort_rgb(
    rgb: np.ndarray, threshold: float, axis: int, key_mode: int
) -> np.ndarray:
    """Float RGB HxWx3 in [0,1], same shape out."""
    out = np.asarray(rgb, dtype=np.float32, order="C").copy()
    keys = _sort_key(out, key_mode)
    t = float(np.clip(threshold, 0.0, 1.0))
    h, w, _ = out.shape

    if axis == 1:
        for x in range(w):
            _sort_segments_1d(keys[:, x], out[:, x, :], t)
    else:
        for y in range(h):
            _sort_segments_1d(keys[y, :], out[y, :, :], t)

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


def onCook(scriptOp):
    inp = scriptOp.inputs[0]
    if inp is None:
        return

    img = inp.numpyArray(delayed=True, writable=False)
    if img is None:
        return

    h, w, c = img.shape
    rgb = np.asarray(img[:, :, :3], dtype=np.float32)

    thr = _par_float(scriptOp, "Threshold", 0.25)
    axis = _par_int(scriptOp, "Axis", 0)
    axis = 1 if axis != 0 else 0
    key_mode = _par_int(scriptOp, "Sortkey", 0)
    key_mode = int(np.clip(key_mode, 0, 3))
    blend = float(np.clip(_par_float(scriptOp, "Original", 0.0), 0.0, 1.0))

    sorted_rgb = _pixel_sort_rgb(rgb, thr, axis, key_mode)
    sorted_rgb = np.clip(sorted_rgb, 0.0, 1.0)

    if blend > 0.0:
        sorted_rgb = (1.0 - blend) * sorted_rgb + blend * rgb

    out = np.empty_like(img, dtype=img.dtype)
    if np.issubdtype(out.dtype, np.integer):
        out[:, :, :3] = np.clip(np.round(sorted_rgb * 255.0), 0, 255).astype(
            out.dtype, copy=False
        )
    else:
        out[:, :, :3] = sorted_rgb.astype(out.dtype, copy=False)
    if c > 3:
        out[:, :, 3:] = img[:, :, 3:]

    scriptOp.copyNumpyArray(out)
