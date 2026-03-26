"""
Script TOP - square of cells in grayscale (black to white) from the SOM grid in script1.

Reads parent().fetch('som_grid'): trained SOM grayscale from script1, or after randomise
a sample-density preview (same grid size). parent.fetch('som_grid_is_preview') is True
for density, False after train. If som_grid missing, fallback gradient. BMP via loadByteArray.

Match resolution on this TOP's common page; each SOM neuron is drawn as a solid square.
"""

import random
import struct

# press 'Setup Parameters' in the OP to call this function to re-create
# the parameters.
def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('SOM')
	page.appendFloat('Organised', label='Organised (else random)')
	return

def onPulse(par):
	return

def _par_toggle(scriptOp, name, default=True):
	"""Custom parameters: use par['Name'], not par.Name."""
	try:
		return bool(int(scriptOp.par[name].eval()))
	except Exception:
		return default

def _bmp_bgra_top(width, height, bgra_flat):
	"""
	32-bit BGRA top-down BMP. bgra_flat length width*height*4, order: row-major, top row first.
	biHeight must be packed as signed (LONG); negative = top-down. Unsigned 'I' breaks on -height.
	"""
	width = int(width)
	height = int(height)
	row_bytes = width * 4
	image_size = row_bytes * height
	# BITMAPFILEHEADER + BITMAPINFOHEADER (40-byte BITMAPINFOHEADER)
	file_size = 14 + 40 + image_size
	header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
	dib = struct.pack(
		'<IIiHHIIIIII',
		40,  # biSize
		width,
		-height,  # LONG, signed - top-down DIB
		1,
		32,
		0,
		image_size,
		2835,
		2835,
		0,
		0,
	)
	return header + dib + bytes(bgra_flat)

def _fill_from_grid(scriptOp, grid, organised):
	"""Paint scriptOp resolution from 2D list of floats 0..1."""
	w = max(1, scriptOp.width)
	h = max(1, scriptOp.height)
	rows = len(grid)
	cols = len(grid[0]) if rows else 1

	# Optional shuffle for "random" layout of the same values
	if not organised:
		flat = [grid[y][x] for y in range(rows) for x in range(cols)]
		random.shuffle(flat)
		g2 = []
		i = 0
		for y in range(rows):
			g2.append(flat[i : i + cols])
			i += cols
		grid = g2

	cell_w = w // cols
	cell_h = h // rows
	cell_w = max(1, cell_w)
	cell_h = max(1, cell_h)

	bgra = bytearray(w * h * 4)
	for py in range(h):
		gy = min(rows - 1, py // cell_h)
		for px in range(w):
			gx = min(cols - 1, px // cell_w)
			v = grid[gy][gx]
			v = max(0.0, min(1.0, float(v)))
			gray = int(round(v * 255.0))
			o = (py * w + px) * 4
			bgra[o + 0] = gray
			bgra[o + 1] = gray
			bgra[o + 2] = gray
			bgra[o + 3] = 255

	return _bmp_bgra_top(w, h, bgra)

def _fallback_gradient(scriptOp, organised):
	"""If script1 has not cooked yet."""
	w = max(1, scriptOp.width)
	h = max(1, scriptOp.height)
	cols = max(2, min(64, w // 8))
	rows = max(2, min(64, h // 8))
	grid = []
	for gy in range(rows):
		row = []
		for gx in range(cols):
			if organised:
				row.append((gx + gy) / float(rows + cols - 2))
			else:
				row.append(random.random())
		grid.append(row)
	return _fill_from_grid(scriptOp, grid, organised)

def onCook(scriptOp):
	p = scriptOp.parent()
	organised = _par_toggle(scriptOp, 'Organised', True)

	grid = None
	if p is not None:
		grid = p.fetch('som_grid', None)

	if grid is None or len(grid) == 0:
		bmp = _fallback_gradient(scriptOp, organised)
	else:
		bmp = _fill_from_grid(scriptOp, grid, organised)

	scriptOp.loadByteArray('.bmp', bmp)
	return

def onGetCookLevel(scriptOp):
	return CookLevel.AUTOMATIC
