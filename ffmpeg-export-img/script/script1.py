import os
import subprocess
import threading
import traceback

import numpy as np

# -----------------------------------------------------------------------------
# TouchDesigner Text DAT script
# Captures a TOP frame from /project1/null1 and encodes it to PNG with FFmpeg.
# Non-blocking: work is done on a daemon thread.
# -----------------------------------------------------------------------------

TOP_PATH = "/project1/null1"
OUTPUT_REL_PATH = os.path.join("script", "img.png")
FFMPEG_EXE = "ffmpeg"  # FFmpeg is assumed to be available in PATH.
ENCODE_TIMEOUT_SEC = 12.0
RUN_ON_TEXTDAT_EXECUTE = True

_state_lock = threading.Lock()
_worker_thread = None


def _log(msg):
	# Print to Textport with consistent tag.
	print("[FFMPEG_EXPORT] {}".format(msg))


def _top_to_rgba_bytes(top):
	"""
	Returns (raw_bytes, width, height) in RGBA8 layout for FFmpeg rawvideo input.
	"""
	# delayed=False grabs the most current cooked frame without forcing async delay.
	arr = top.numpyArray(delayed=False)
	if arr is None:
		raise RuntimeError("TOP numpyArray() returned None: {}".format(TOP_PATH))
	if arr.ndim != 3 or arr.shape[2] < 3:
		raise RuntimeError("Unexpected TOP array shape: {}".format(arr.shape))

	h, w = arr.shape[0], arr.shape[1]

	# TouchDesigner TOP numpy arrays are typically float32 [0..1].
	if arr.dtype.kind == "f":
		arr = np.clip(arr, 0.0, 1.0)
		arr = (arr * 255.0 + 0.5).astype(np.uint8)
	elif arr.dtype != np.uint8:
		arr = np.clip(arr, 0, 255).astype(np.uint8)

	# Ensure RGBA for ffmpeg -pix_fmt rgba.
	if arr.shape[2] == 3:
		alpha = np.full((h, w, 1), 255, dtype=np.uint8)
		arr = np.concatenate((arr, alpha), axis=2)
	elif arr.shape[2] > 4:
		arr = arr[:, :, :4]

	# TouchDesigner TOP data is commonly bottom-up for image export use cases.
	# Flip vertically so PNG matches what you see in the viewer.
	arr = np.flipud(arr)

	# Ensure contiguous bytes.
	arr = np.ascontiguousarray(arr)
	return arr.tobytes(), w, h


def _encode_png_ffmpeg(raw_rgba_bytes, width, height, output_path):
	cmd = [
		FFMPEG_EXE,
		"-hide_banner",
		"-loglevel",
		"error",
		"-y",
		"-f",
		"rawvideo",
		"-pix_fmt",
		"rgba",
		"-s",
		"{}x{}".format(width, height),
		"-i",
		"-",
		"-frames:v",
		"1",
		output_path,
	]

	_log("Starting FFmpeg process.")
	_log("FFmpeg target: {} ({}x{})".format(output_path, width, height))
	proc = None
	try:
		proc = subprocess.Popen(
			cmd,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			bufsize=0,
		)
		_, stderr_data = proc.communicate(input=raw_rgba_bytes, timeout=ENCODE_TIMEOUT_SEC)
		if proc.returncode != 0:
			raise RuntimeError(
				"FFmpeg failed (code {}): {}".format(
					proc.returncode, stderr_data.decode("utf-8", errors="replace").strip()
				)
			)
		_log("Encode complete.")
	finally:
		# Strong cleanup to prevent process handle leaks.
		if proc is not None:
			try:
				if proc.poll() is None:
					proc.kill()
			except Exception:
				pass
			for stream_name in ("stdin", "stdout", "stderr"):
				stream = getattr(proc, stream_name, None)
				if stream is not None:
					try:
						stream.close()
					except Exception:
						pass


def _worker(raw_bytes, width, height, out_path):
	try:
		_log("Worker started.")
		_encode_png_ffmpeg(raw_bytes, width, height, out_path)
		_log("Saved {} ({}x{})".format(out_path, width, height))
	except subprocess.TimeoutExpired:
		_log("FFmpeg encode timed out after {}s".format(ENCODE_TIMEOUT_SEC))
	except Exception as exc:
		_log("ERROR: {}".format(exc))
		_log(traceback.format_exc())
	finally:
		global _worker_thread
		with _state_lock:
			_worker_thread = None
		_log("Worker finished and released.")


def export_top_to_png_async():
	"""
	Call this from a button callback / parameter execute / command:
	    mod('script1').export_top_to_png_async()
	"""
	# IMPORTANT:
	# All TouchDesigner OP access must happen on the main thread.
	top = op(TOP_PATH)
	if top is None:
		_log("ERROR: TOP not found: {}".format(TOP_PATH))
		return False
	_log("Found TOP: {}".format(TOP_PATH))

	raw_bytes, width, height = _top_to_rgba_bytes(top)
	_log("Captured frame from TOP at {}x{}".format(width, height))

	out_path = os.path.join(project.folder, OUTPUT_REL_PATH)
	out_dir = os.path.dirname(out_path)
	if out_dir and not os.path.exists(out_dir):
		os.makedirs(out_dir, exist_ok=True)
		_log("Created output directory: {}".format(out_dir))

	global _worker_thread
	with _state_lock:
		if _worker_thread is not None and _worker_thread.is_alive():
			_log("Encode already running; skip to keep UI/cook non-blocking.")
			return False
		_worker_thread = threading.Thread(
			target=_worker,
			args=(raw_bytes, width, height, out_path),
			name="ffmpeg_png_export",
			daemon=True,
		)
		_worker_thread.start()
	_log("Encode thread started.")
	return True


if RUN_ON_TEXTDAT_EXECUTE:
	# Clicking "Run Script" on this Text DAT triggers one async export.
	export_top_to_png_async()


