"""
Parameter Execute DAT (recommended for this use-case)

Detect when `audiofilein1` Play is toggled to 1, then grab metadata.

How to use:
- Create a Parameter Execute DAT and paste this script.
- In the Parameter Execute DAT parameters:
  - Parameter: play
  - Enable: Value Change

"""

import os

AUDIO_OP = 'audiofilein1'  # rename if your Audio File In CHOP differs


def _safe_par_eval(aop, par_name):
	try:
		p = getattr(aop.par, par_name)
		return p.eval()
	except Exception:
		return None


def _add_info_chop_channels(aop, meta):
	"""
	Read all available info channels from the operator's Info CHOP.
	This is usually the richest source of runtime file/audio details.
	"""
	try:
		ichop = aop.infoCHOP
	except Exception:
		ichop = None

	if not ichop:
		return

	try:
		for ch in ichop.chans():
			try:
				meta[f'info.{ch.name}'] = ch.eval()
			except Exception:
				pass
	except Exception:
		pass


def _get_audio_metadata(aop):
	# Force cook so info fields are current (safe/no-op if not needed)
	try:
		aop.cook(force=True)
	except Exception:
		pass

	info = getattr(aop, 'info', None)
	meta = {
		'op': aop.path,
		'file': aop.par.file.eval() if hasattr(aop.par, 'file') else '',
	}

	# Common parameter values (if present on this build/operator).
	for k in ('play', 'loop', 'speed', 'cuepulse', 'cuepoint', 'reloadpulse'):
		v = _safe_par_eval(aop, k)
		if v is not None:
			meta[f'par.{k}'] = v

	# File system metadata for the loaded file.
	file_path = meta.get('file') or ''
	if file_path:
		try:
			meta['file.exists'] = os.path.exists(file_path)
			if meta['file.exists']:
				meta['file.size_bytes'] = os.path.getsize(file_path)
				meta['file.modified_unix'] = os.path.getmtime(file_path)
		except Exception:
			pass

	# Info fields vary across builds; read what exists as attributes.
	for k in ('duration', 'length', 'numSamples', 'sampleRate', 'rate', 'numChannels', 'channels', 'fileType'):
		try:
			meta[k] = getattr(info, k)
		except Exception:
			pass

	# Include all Info CHOP channel values (best source for extra data).
	_add_info_chop_channels(aop, meta)

	return meta


def onValueChange(par, prev):
	# Fires when `play` changes (as configured in the Parameter Execute DAT).
	if par.name != 'play':
		return

	# Strict rising-edge trigger only: print once when play goes 0 -> 1.
	try:
		current = int(par.eval())
		previous = int(prev)
	except Exception:
		return

	if not (previous == 0 and current == 1):
		return

	aop = op(AUDIO_OP)
	if aop is None:
		debug(f'Audio op not found: {AUDIO_OP}')
		return

	meta = _get_audio_metadata(aop)

	print('--- audio metadata (on play=1) ---')
	for k, v in meta.items():
		print(f'{k}: {v}')

	# Store for use elsewhere in the network
	parent().store('audioMeta', meta)
	return
