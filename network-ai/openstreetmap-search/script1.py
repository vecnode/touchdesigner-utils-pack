"""
TouchDesigner + OpenStreetMap
"""

import json
import math
import os
import urllib.parse
import urllib.request


NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
OSM_TILE_ENDPOINT_TEMPLATE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
OSM_STATICMAP_ENDPOINT = "https://staticmap.openstreetmap.de/staticmap.php"
OSM_EMBED_ENDPOINT = "https://www.openstreetmap.org/export/embed.html"
AUTO_RUN_ON_EXECUTE = True
ALLOW_OSM_TILE_DOWNLOAD = False
WRITE_IMAGES_TO_DISK = False


def _log(*parts):
	"""Consistent debug output in TouchDesigner Textport."""
	print("[OSM DEBUG]", *parts)


def _nominatim_search(place_name, limit=1):
	"""Return a list of search matches from Nominatim."""
	if not place_name or not place_name.strip():
		raise ValueError("Place name is empty")

	_log("Searching Nominatim for:", place_name)

	params = {
		"q": place_name.strip(),
		"format": "json",
		"limit": str(limit),
		"addressdetails": "1",
	}
	url = NOMINATIM_ENDPOINT + "?" + urllib.parse.urlencode(params)

	req = urllib.request.Request(
		url,
		headers={
			# Nominatim usage policy asks for a valid User-Agent.
			"User-Agent": "TouchDesigner-OSM-Search/1.0 (local patch)"
		},
	)
	with urllib.request.urlopen(req, timeout=10) as resp:
		data = resp.read().decode("utf-8")

	_log("Nominatim response bytes:", len(data))

	return json.loads(data)


def _make_osm_url(lat, lon, zoom=13):
	"""Build an OpenStreetMap URL centered at lat/lon with a marker."""
	return (
		f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"
		f"#map={int(zoom)}/{lat}/{lon}"
	)


def _set_url_on_operator(target_op, url):
	"""Set URL on common TouchDesigner ops (Web Render TOP / Web Browser COMP)."""
	if target_op is None:
		raise RuntimeError("Target operator is None")

	# Different operators expose different parameter names/cases.
	for parm_name in ("Url", "url", "Address", "address"):
		parm = getattr(target_op.par, parm_name, None)
		if parm is not None:
			parm.val = url
			return

	raise RuntimeError(
		f"Operator '{target_op.path}' has no URL-like parameter (Url/url/Address/address)"
	)


def _set_source_on_operator(target_op, source):
	"""Set source on URL or file-based operators (Web Render, Movie File In, etc.)."""
	if target_op is None:
		raise RuntimeError("Target operator is None")

	for parm_name in ("Url", "url", "Address", "address", "File", "file"):
		parm = getattr(target_op.par, parm_name, None)
		if parm is not None:
			parm.val = source
			return parm_name

	raise RuntimeError(
		f"Operator '{target_op.path}' has no source-like parameter (Url/url/Address/address/File/file)"
	)


def _download_url_to_local_png(url, filename="osm_static_map.png"):
	"""Download an image URL to a stable local path and return that file path."""
	base_folder = "."
	if "project" in globals() and getattr(project, "folder", None):
		base_folder = project.folder

	cache_dir = os.path.join(base_folder, "osm_cache")
	os.makedirs(cache_dir, exist_ok=True)
	local_path = os.path.join(cache_dir, filename)

	_log("Downloading map image to:", local_path)
	with urllib.request.urlopen(url, timeout=12) as resp:
		img_data = resp.read()

	if not img_data:
		raise RuntimeError("Downloaded map image is empty")

	with open(local_path, "wb") as f:
		f.write(img_data)

	_log("Downloaded bytes:", len(img_data))
	return local_path


def _latlon_to_tile(lat, lon, zoom):
	"""Convert lat/lon to slippy map tile coordinates (x, y) for a zoom level."""
	lat_f = float(lat)
	lon_f = float(lon)
	z = int(zoom)

	# Clamp to Web Mercator valid latitude range.
	lat_f = max(min(lat_f, 85.05112878), -85.05112878)
	n = 2 ** z
	x = int((lon_f + 180.0) / 360.0 * n)
	lat_rad = math.radians(lat_f)
	y = int((1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

	x = max(0, min(x, n - 1))
	y = max(0, min(y, n - 1))
	return x, y


def _make_osm_tile_url(lat, lon, zoom=13):
	"""Build direct OSM raster tile URL (map texture only, no site UI)."""
	x, y = _latlon_to_tile(lat, lon, zoom)
	return OSM_TILE_ENDPOINT_TEMPLATE.format(z=int(zoom), x=x, y=y)


def _make_osm_static_map_url(lat, lon, zoom=13, width=1280, height=720, with_marker=True):
	"""Build full-frame static map image URL centered on lat/lon."""
	# staticmap.openstreetmap.de supports up to 2048x2048.
	w = max(64, min(int(width), 2048))
	h = max(64, min(int(height), 2048))
	params = {
		"center": f"{lat},{lon}",
		"zoom": str(int(zoom)),
		"size": f"{w}x{h}",
	}
	if with_marker:
		params["markers"] = f"{lat},{lon},red-pushpin"
	return OSM_STATICMAP_ENDPOINT + "?" + urllib.parse.urlencode(params)


def _zoom_to_degree_span(zoom):
	"""Approximate lon/lat span in degrees for an embed bbox around center."""
	# Tuned for practical framing in OSM embed mode.
	z = max(1, min(int(zoom), 19))
	return 360.0 / (2 ** (z - 1))


def _make_osm_embed_map_url(lat, lon, zoom=13, with_marker=True):
	"""Build map-only OpenStreetMap embed URL (no full website chrome)."""
	lat_f = float(lat)
	lon_f = float(lon)
	span = _zoom_to_degree_span(zoom)

	bbox_min_lon = lon_f - span * 0.5
	bbox_max_lon = lon_f + span * 0.5
	bbox_min_lat = lat_f - span * 0.3
	bbox_max_lat = lat_f + span * 0.3

	params = {
		"bbox": f"{bbox_min_lon},{bbox_min_lat},{bbox_max_lon},{bbox_max_lat}",
		"layer": "mapnik",
	}
	if with_marker:
		params["marker"] = f"{lat_f},{lon_f}"

	return OSM_EMBED_ENDPOINT + "?" + urllib.parse.urlencode(params)


def search_place(place_name, zoom=13):
	"""Return dict with display_name, lat, lon, and URL for the first result."""
	matches = _nominatim_search(place_name, limit=1)
	_log("Matches found:", len(matches))
	if not matches:
		raise LookupError(f"No OpenStreetMap results for: {place_name}")

	first = matches[0]
	lat = first["lat"]
	lon = first["lon"]
	return {
		"display_name": first.get("display_name", place_name),
		"lat": lat,
		"lon": lon,
		"url": _make_osm_url(lat, lon, zoom=zoom),
		"embed_url": _make_osm_embed_map_url(lat, lon, zoom=zoom, with_marker=True),
		"tile_url": _make_osm_tile_url(lat, lon, zoom=zoom),
		"static_map_url": _make_osm_static_map_url(lat, lon, zoom=zoom),
	}


def search_and_show(place_dat="place_input", render_target="map_render", zoom=13):
	"""
	Read place from a Text DAT, geocode it, and update a URL-capable render target.

	Typical target:
	- Web Render TOP named map_render

	Also works with:
	- Web Browser COMP

	Returns True on success, False on failure.
	"""
	try:
		place_op = op(place_dat)
		target_op = op(render_target)
		_log("search_and_show() called")
		_log("place_dat:", place_dat, "render_target:", render_target, "zoom:", zoom)

		if place_op is None:
			raise RuntimeError(f"Operator not found: {place_dat}")
		if target_op is None:
			raise RuntimeError(f"Operator not found: {render_target}")

		_log("place_op path:", place_op.path)
		_log("target_op path:", target_op.path)

		place_name = place_op.text.strip()
		_log("place_input value:", place_name)
		result = search_place(place_name, zoom=zoom)

		_set_url_on_operator(target_op, result["url"])
		_log("URL set on target:", result["url"])

		print(
			"OSM result:",
			result["display_name"],
			"lat=", result["lat"],
			"lon=", result["lon"],
		)
		return True

	except Exception as exc:
		_log("OSM search error:", exc)
		return False


def search_and_show_map_only(place_dat="place_input", render_target="map_render", zoom=13, with_marker=True):
	"""Set Web Render TOP to OSM embed page (map-only view, minimal UI)."""
	try:
		place_op = op(place_dat)
		target_op = op(render_target)
		_log("search_and_show_map_only() called")
		_log("place_dat:", place_dat, "render_target:", render_target, "zoom:", zoom)

		if place_op is None:
			raise RuntimeError(f"Operator not found: {place_dat}")
		if target_op is None:
			raise RuntimeError(f"Operator not found: {render_target}")

		place_name = place_op.text.strip()
		result = search_place(place_name, zoom=zoom)
		embed_url = _make_osm_embed_map_url(result["lat"], result["lon"], zoom=zoom, with_marker=with_marker)
		_set_url_on_operator(target_op, embed_url)
		_log("Embed map URL set on target:", embed_url)
		return True

	except Exception as exc:
		_log("OSM map-only error:", exc)
		return False


def search_and_show_texture(
	place_dat="place_input",
	texture_target="map_texture",
	zoom=13,
	width=1280,
	height=720,
	with_marker=True,
	use_single_tile=False,
):
	"""
	Set a second TOP to a map texture-only image source.

	Recommended target:
	- Movie File In TOP named map_texture

	Can also work with URL-based targets depending on operator parameters.

	Default mode uses a full static map frame (better than one tile).
	Set use_single_tile=True to force one raw tile only.

	Warning:
	- Direct OSM tile/static image download can be blocked by policy.
	- Prefer setup_texture_copy_from_render() for a policy-safe second TOP.
	"""
	try:
		if not ALLOW_OSM_TILE_DOWNLOAD:
			_log(
				"Texture download disabled by policy. Use setup_texture_copy_from_render()",
			)
			return False

		place_op = op(place_dat)
		texture_op = op(texture_target)
		_log("search_and_show_texture() called")
		_log(
			"place_dat:",
			place_dat,
			"texture_target:",
			texture_target,
			"zoom:",
			zoom,
			"size:",
			f"{int(width)}x{int(height)}",
			"with_marker:",
			with_marker,
			"use_single_tile:",
			use_single_tile,
		)

		if place_op is None:
			raise RuntimeError(f"Operator not found: {place_dat}")
		if texture_op is None:
			raise RuntimeError(f"Operator not found: {texture_target}")

		place_name = place_op.text.strip()
		_log("place_input value:", place_name)
		result = search_place(place_name, zoom=zoom)
		source_url = result["tile_url"] if use_single_tile else _make_osm_static_map_url(
			result["lat"],
			result["lon"],
			zoom=zoom,
			width=width,
			height=height,
			with_marker=with_marker,
		)
		used_parm = _set_source_on_operator(texture_op, source_url)

		if WRITE_IMAGES_TO_DISK and str(used_parm).lower() == "file":
			local_file = _download_url_to_local_png(source_url, filename="map_texture.png")
			_set_source_on_operator(texture_op, local_file)
			_log("Texture file cached at:", local_file)
		else:
			_log("Texture URL assigned (no disk write):" , source_url)

		_log("Texture source set using parm:", used_parm)
		return True

	except Exception as exc:
		_log("Texture map error:", exc)
		return False


def setup_texture_copy_from_render(source_top="map_render", copy_top="map_texture"):
	"""
	Create/update a local TOP copy from Web Render output (no extra web requests).

	This is the recommended and policy-safe way to get a second texture-only TOP.
	If copy_top exists but is not a Select TOP, it will be replaced with one.
	"""
	try:
		source_op = op(source_top)
		if source_op is None:
			raise RuntimeError(f"Operator not found: {source_top}")

		copy_op = op(copy_top)

		# If copy_op exists but is wrong type (e.g., Movie File In from old flow),
		# delete it and create fresh Select TOP.
		if copy_op is not None:
			op_type = str(copy_op.type).lower() if hasattr(copy_op, "type") else ""
			is_select = "select" in op_type
			if not is_select:
				_log("Replacing", copy_op.path, "(type:", op_type, ") with Select TOP")
				parent = copy_op.parent()
				copy_op.destroy()
				copy_op = parent.create(selectTOP, copy_top)
				_log("Created fresh Select TOP:", copy_op.path)

		if copy_op is None:
			copy_op = source_op.parent().create(selectTOP, copy_top)
			_log("Created Select TOP:", copy_op.path)

		top_parm = getattr(copy_op.par, "Top", None)
		if top_parm is None:
			top_parm = getattr(copy_op.par, "top", None)
		if top_parm is None:
			raise RuntimeError(f"Select TOP '{copy_op.path}' has no Top parameter")

		top_parm.val = source_op.path
		_log("Texture copy wired:", copy_op.path, "<-", source_op.path)
		return True

	except Exception as exc:
		_log("setup_texture_copy_from_render error:", exc)
		_log("Manual fallback: create a Select TOP and set its Top to /project1/map_render")
		return False


def on_search_button_click():
	"""Optional helper to call from a Button COMP callback."""
	return search_and_show_map_only(place_dat="place_input", render_target="map_render", zoom=13, with_marker=True)


def search_and_show_via_local_server(
	place_dat="place_input",
	render_target="map_render",
	server_base_url="http://127.0.0.1:9980/index.html",
	zoom=13,
):
	"""
	Optional mode: build local server URL with query params and set it on render target.

	Expected local page reads query string keys:
	- lat
	- lon
	- zoom
	"""
	try:
		place_op = op(place_dat)
		target_op = op(render_target)
		_log("search_and_show_via_local_server() called")
		_log("place_dat:", place_dat, "render_target:", render_target, "zoom:", zoom)
		_log("server_base_url:", server_base_url)

		if place_op is None:
			raise RuntimeError(f"Operator not found: {place_dat}")
		if target_op is None:
			raise RuntimeError(f"Operator not found: {render_target}")

		place_name = place_op.text.strip()
		_log("place_input value:", place_name)
		result = search_place(place_name, zoom=zoom)

		query = urllib.parse.urlencode(
			{
				"lat": result["lat"],
				"lon": result["lon"],
				"zoom": str(int(zoom)),
			}
		)
		local_url = f"{server_base_url}?{query}"
		_set_url_on_operator(target_op, local_url)

		_log("Local map URL:", local_url)
		return True

	except Exception as exc:
		_log("Local server map error:", exc)
		return False


def debug_run_once(place_dat="place_input", render_target="map_render", zoom=13):
	"""Manual debug entry point: validates ops, prints diagnostics, and runs once."""
	_log("--- debug_run_once start ---")
	place_op = op(place_dat) if "op" in globals() else None
	target_op = op(render_target) if "op" in globals() else None

	_log("TouchDesigner op() available:", "op" in globals())
	_log("place_op exists:", place_op is not None)
	_log("target_op exists:", target_op is not None)

	if place_op is not None:
		_log("place_op path:", place_op.path)
		_log("place_input raw text:", repr(place_op.text))

	if target_op is not None:
		_log("target_op path:", target_op.path)

	success = search_and_show_map_only(place_dat=place_dat, render_target=render_target, zoom=zoom, with_marker=True)
	copy_success = setup_texture_copy_from_render(source_top=render_target, copy_top="map_texture")
	_log("search_and_show_map_only success:", success)
	_log("setup_texture_copy_from_render success:", copy_success)
	_log("--- debug_run_once end ---")
	return success and copy_success


if AUTO_RUN_ON_EXECUTE:
	try:
		if "op" in globals():
			_log("Text DAT executed. Auto-running debug search.")
			debug_run_once(place_dat="place_input", render_target="map_render", zoom=13)
		else:
			_log("Text DAT executed outside TouchDesigner. Skipping auto-run.")
	except Exception as _auto_exc:
		_log("Auto-run crashed:", _auto_exc)

