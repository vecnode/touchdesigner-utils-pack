"""
Script DAT - trains a 2D Kohonen Self-Organizing Map on toy 2D data (no external libs).

Output: this DAT is filled with tab-separated grayscale values (one row per map row).
Also stores the grid on the parent COMP as som_grid for the Script TOP (script2).

Sibling Table DAT `data` is filled with
columns role, x, y, gx, gy: training samples (input), codebook before training (init),
and after training (node). gx/gy are grid indices. Use for Scatter CHOP / geometry.

Cook script1 before script2 (e.g. place script1 earlier in the network or pulse it first).

Text DAT runners (script3 / script4): parent().store('som_command', 'randomise'|'train') then
script1.cook(force=True) - avoids op('script1').module (TD can fail to compile that path).
By default onCook does not train. Float Autotrain=1 trains on every cook (legacy).
"""

import copy
import math
import queue
import random
import threading
import time

_training_busy = False
_train_result_queue = queue.Queue()

# press 'Setup Parameters' in the OP to call this function to re-create the
# parameters.
def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('SOM')
	page.appendFloat('Grid', label='Grid size')
	page.appendFloat('Epochs', label='Epochs')
	page.appendFloat('Learnrate', label='Learn rate')
	page.appendFloat('Sigma0', label='Sigma start')
	page.appendFloat('Seed', label='Random seed')
	page.appendFloat('Autotrain', label='Train on cook')
	return

def onPulse(par):
	return

def _par_toggle(scriptOp, name, default=False):
	try:
		return bool(int(scriptOp.par[name].eval()))
	except Exception:
		return default

def _par_float(scriptOp, name, default, zero_is_default=True):
	"""Custom parameters must use par['Name']; dot access (par.Grid) is not valid in TD."""
	try:
		p = scriptOp.par[name]
		v = float(p.eval())
	except Exception:
		return default
	if zero_is_default and v == 0.0:
		return default
	return v

def _som_toy_data(n_per_cluster=80, seed=0, random_centers=False):
	"""Three 2D clusters in [0, 1]^2 - fixed layout, or random centers when randomising."""
	rng = random.Random(seed)
	if random_centers:
		centers = [(rng.uniform(0.12, 0.88), rng.uniform(0.12, 0.88)) for _ in range(3)]
	else:
		centers = [(0.2, 0.25), (0.75, 0.35), (0.45, 0.78)]
	sigma = rng.uniform(0.04, 0.09) if random_centers else 0.06
	data = []
	for cx, cy in centers:
		for _ in range(n_per_cluster):
			data.append(
				(
					max(0.0, min(1.0, cx + rng.gauss(0, sigma))),
					max(0.0, min(1.0, cy + rng.gauss(0, sigma))),
				)
			)
	rng.shuffle(data)
	return data

def _learn_som(data, grid_w, grid_h, epochs, learn0, sigma0, seed=0):
	"""Pure-Python SOM weight update; weights on a 2D grid, 2D codebook (matches data)."""
	rng = random.Random(seed)
	# random init in [0,1]
	weights = [
		[[rng.random(), rng.random()] for _ in range(grid_w)]
		for _ in range(grid_h)
	]
	initial = copy.deepcopy(weights)

	t0 = time.perf_counter()

	for e in range(epochs):
		t = e / max(epochs - 1, 1)
		lr = learn0 * (1.0 - t)
		sigma = max(0.35, sigma0 * (1.0 - t))

		if e == 0 or (e + 1) % 10 == 0 or e == epochs - 1:
			elapsed = time.perf_counter() - t0
			print(
				'  SOM epoch {:>5}/{:<5}  lr={:.5f}  sigma={:.4f}  ({:.2f}s)'.format(
					e + 1, epochs, lr, sigma, elapsed
				)
			)

		for sample in data:
			bx, by = 0, 0
			best = float('inf')
			for gy in range(grid_h):
				for gx in range(grid_w):
					w = weights[gy][gx]
					d = (sample[0] - w[0]) ** 2 + (sample[1] - w[1]) ** 2
					if d < best:
						best = d
						bx, by = gx, gy

			sig2 = 2.0 * (sigma ** 2) + 1e-12
			for gy in range(grid_h):
				for gx in range(grid_w):
					nd = (gx - bx) ** 2 + (gy - by) ** 2
					h = math.exp(-nd / sig2)
					w = weights[gy][gx]
					w[0] += lr * h * (sample[0] - w[0])
					w[1] += lr * h * (sample[1] - w[1])

	return weights, initial

def _quantization_error_stats(data, weights, grid_w, grid_h):
	"""
	Mean quantization error (MQE): average Euclidean distance from each sample to its BMU weight.
	Also returns max distance. Same BMU rule as training (min squared distance).
	"""
	n = len(data)
	if n == 0:
		return 0.0, 0.0
	s = 0.0
	mxe = 0.0
	for sample in data:
		best = float('inf')
		for gy in range(grid_h):
			for gx in range(grid_w):
				w = weights[gy][gx]
				d = (sample[0] - w[0]) ** 2 + (sample[1] - w[1]) ** 2
				if d < best:
					best = d
		dist = math.sqrt(best)
		s += dist
		if dist > mxe:
			mxe = dist
	return s / n, mxe

def _samples_to_density_grid(data, grid_n):
	"""
	Bin 2D samples in [0,1]^2 into a grid_n x grid_n density map (0..1) for Script TOP preview.
	Row 0 = top of image; y increases upward in data space (y=1 near top row).
	"""
	grid_n = max(4, int(grid_n))
	counts = [[0 for _ in range(grid_n)] for _ in range(grid_n)]
	for x, y in data:
		sx = min(0.999999, max(0.0, x))
		sy = min(0.999999, max(0.0, y))
		ix = min(grid_n - 1, int(sx * grid_n))
		iy = min(grid_n - 1, int((1.0 - sy) * grid_n))
		counts[iy][ix] += 1
	mx = 0
	for row in counts:
		for v in row:
			if v > mx:
				mx = v
	mx = float(mx) if mx > 0 else 1.0
	return [[counts[gy][gx] / mx for gx in range(grid_n)] for gy in range(grid_n)]

def _cook_script_top(parent_op):
	if parent_op is None:
		return
	t = parent_op.op('script2')
	if t is not None and t.valid:
		try:
			t.cook(force=True)
		except Exception:
			pass

def _weights_to_grayscale(weights):
	"""Map 2D weights to single channel 0..1 (average of normalized coords)."""
	rows = []
	for gy in range(len(weights)):
		line = []
		for gx in range(len(weights[gy])):
			w0, w1 = weights[gy][gx]
			line.append((w0 + w1) * 0.5)
		rows.append(line)
	return rows

def _write_plot_inputs_only(plot_dat, data):
	plot_dat.clear()
	plot_dat.appendRow(['role', 'x', 'y', 'gx', 'gy'])
	for x, y in data:
		plot_dat.appendRow(['input', '{:.6f}'.format(x), '{:.6f}'.format(y), '', ''])

def _write_plot_dat(plot_dat, data, weights, initial):
	"""
	Fill a Table DAT for scatter: samples, initial codebook (pre-training), final codebook.
	Columns: role, x, y, gx, gy - role is input | init | node.
	"""
	plot_dat.clear()
	plot_dat.appendRow(['role', 'x', 'y', 'gx', 'gy'])
	for x, y in data:
		plot_dat.appendRow(['input', '{:.6f}'.format(x), '{:.6f}'.format(y), '', ''])
	for gy in range(len(initial)):
		for gx in range(len(initial[gy])):
			w0, w1 = initial[gy][gx]
			plot_dat.appendRow(['init', '{:.6f}'.format(w0), '{:.6f}'.format(w1), str(gx), str(gy)])
	for gy in range(len(weights)):
		for gx in range(len(weights[gy])):
			w0, w1 = weights[gy][gx]
			plot_dat.appendRow(
				['node', '{:.6f}'.format(w0), '{:.6f}'.format(w1), str(gx), str(gy)]
			)

def _resolve_som_dat(scriptOp):
	if scriptOp is not None and scriptOp.valid:
		return scriptOp
	s = op('script1')
	return s if s is not None and s.valid else None

def randomise_data(scriptOp=None):
	"""
	New toy cluster samples; stored on parent as som_samples. Table DAT `data` shows inputs only.
	Text DAT: parent.store('som_command','randomise'); script1.cook(force=True)
	"""
	scriptOp = _resolve_som_dat(scriptOp)
	if scriptOp is None:
		return
	seed = random.randrange(0, 2**31 - 1)
	data = _som_toy_data(seed=seed, random_centers=True)
	p = scriptOp.parent()
	if p is not None:
		p.store('som_samples', data)
		p.store('som_samples_seed', seed)
		g = _par_float(scriptOp, 'Grid', 32.0)
		grid_n = max(4, int(g))
		preview = _samples_to_density_grid(data, grid_n)
		p.store('som_grid', preview)
		p.store('som_grid_is_preview', True)
		_cook_script_top(p)
	d = p.op('data') if p else None
	if d is not None and d.valid and hasattr(d, 'appendRow') and hasattr(d, 'clear'):
		_write_plot_inputs_only(d, data)

def _commit_training(scriptOp, gray, data, weights, initial, grid, p):
	"""Main-thread only: write Script DAT, stores, Table, Script TOP."""
	scriptOp.clear()
	for row in gray:
		scriptOp.appendRow(['{:.6f}'.format(v) for v in row])
	if p is not None:
		p.store('som_grid', gray)
		p.store('som_grid_n', grid)
		p.store('som_grid_is_preview', False)
		_cook_script_top(p)
		d = p.op('data')
		if d is not None and d.valid and hasattr(d, 'appendRow') and hasattr(d, 'clear'):
			_write_plot_dat(d, data, weights, initial)

def _training_worker(data, grid, epochs, lr, sigma0, seed, script_path):
	"""Background thread: SOM math only (no TouchDesigner API). Main thread picks up via queue."""
	global _training_busy
	try:
		t_train = time.perf_counter()
		weights, initial = _learn_som(data, grid, grid, epochs, lr, sigma0, seed=seed)
		dt = time.perf_counter() - t_train
		mqe0, mx0 = _quantization_error_stats(data, initial, grid, grid)
		mqe1, mx1 = _quantization_error_stats(data, weights, grid, grid)
		print('--- Quantization error (||x - w_BMU|| in input space; lower after train is better) ---')
		print('  before train: mean={:.6f}  max={:.6f}'.format(mqe0, mx0))
		print('  after train:  mean={:.6f}  max={:.6f}'.format(mqe1, mx1))
		print(
			'--- SOM train done | total {:.3f}s | main thread will commit (CookLevel.ALWAYS) ---'.format(dt)
		)
		gray = _weights_to_grayscale(weights)
		_train_result_queue.put((gray, data, weights, initial, grid, script_path))
	except Exception as ex:
		print('SOM train error:', ex)
		_train_result_queue.put(None)

def train_som(scriptOp=None):
	"""
	Train on parent som_samples if set; else same built-in toy data as before.
	Writes this Script DAT, som_grid, and full `data` plot.
	Text DAT: parent.store('som_command','train'); script1.cook(force=True)
	"""
	scriptOp = _resolve_som_dat(scriptOp)
	if scriptOp is None:
		return
	g = _par_float(scriptOp, 'Grid', 32.0)
	grid = max(4, int(g))
	ep = _par_float(scriptOp, 'Epochs', 400.0)
	epochs = max(10, int(ep))
	lr = _par_float(scriptOp, 'Learnrate', 0.08)
	sigma0 = float(max(0.5, _par_float(scriptOp, 'Sigma0', 8.0)))
	seed = int(_par_float(scriptOp, 'Seed', 42.0, zero_is_default=False))

	p = scriptOp.parent()
	data = None
	used_stored = False
	if p is not None:
		data = p.fetch('som_samples', None)
		if data is not None:
			used_stored = True
	if data is None:
		data = _som_toy_data(seed=seed + 11, random_centers=False)

	global _training_busy
	if _training_busy:
		print('SOM: training already running; ignored')
		return

	src = 'stored som_samples' if used_stored else 'built-in toy'
	print(
		'--- SOM train start (async) | samples={} | grid={}x{} | epochs={} | {} | learn={:.4f} sigma0={:.4f} seed={} ---'.format(
			len(data), grid, grid, epochs, src, lr, sigma0, seed
		)
	)
	_training_busy = True
	path = scriptOp.path
	threading.Thread(
		target=_training_worker,
		args=(data, grid, epochs, lr, sigma0, seed, path),
		daemon=True,
	).start()

def onCook(scriptOp):
	global _training_busy
	while True:
		try:
			item = _train_result_queue.get_nowait()
		except queue.Empty:
			break
		if item is None:
			_training_busy = False
			continue
		gray, data, weights, initial, grid, path = item
		sop = op(path)
		if sop is None or not sop.valid:
			_training_busy = False
			continue
		_commit_training(sop, gray, data, weights, initial, grid, sop.parent())
		_training_busy = False

	p = scriptOp.parent()
	if p is not None:
		cmd = p.fetch('som_command', '')
		if cmd == 'randomise':
			randomise_data(scriptOp)
			p.store('som_command', '')
			return
		if cmd == 'train':
			train_som(scriptOp)
			p.store('som_command', '')
			return
	# Heavy training; skip unless Autotrain float is 1.
	if _par_toggle(scriptOp, 'Autotrain', False):
		train_som(scriptOp)
	return

def onGetCookLevel(scriptOp):
	# Worker must not use run()/op(); main thread cooks every frame while training so onCook can drain the queue.
	# Do not use queue.empty() here (not reliable across threads).
	if _training_busy:
		return CookLevel.ALWAYS
	return CookLevel.AUTOMATIC
