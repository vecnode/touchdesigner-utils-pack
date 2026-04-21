## TouchDesigner utilities pack

A set of TouchDesigner utilities and projects, tested Windows 11 and RTX 3090/3070.


- [audio](audio)

  - [audio-mixer-fades](audio/audio-mixer-fades/): Trigger independent audio track fade in/out on button click, able to range, and master on/off (from 0-1).

  - [audio-play-callback](audio/audio-play-callback): Custom callback on sample length of an Audio Play CHOP to allow logic when audio files stop playing (trigger a panel when audio finishes).

  - [audio-get-metadata](audio/audio-get-metadata): Get audio file metadata and operator load using Python, tested TouchDesigner 2025.32460.


- [control-input](control-input)

  - [akai-apc40mk2-colors](control-input/akai-apc40mk2-colors): Control 8x5 pad colors on Akai APC40MK2 MIDI Controller, tested TouchDesigner 2025.32460.

  - [akai-apc40mk2-midi](control-input/akai-apc40mk2-midi): MIDI template for Akai APC40MK2 MIDI Controller, tested TouchDesigner 2022.32120. Requires to set the MIDI mapping dialog as device in. The MIDI codes are set for callback automatically at startup.

  - [link-two-containers](control-input/link-two-containers): A Select CHOP operator showing widget on container A triggered on container B (same logic as "send" and "receive" in MaxMSP).
  
  - [midi-to-vst](control-input/midi-to-vst): Boolean to send `onNoteOn()` and `onNoteOff()` to arbitrary VST3s, tested TouchDesigner 2022.32120.


- [data-utilities](data-utilities)

  - [csv-reader](data-utilities/csv-reader): Reads CSV files into a Table DAT using raw Python.

  - [dir-mapper-2d-slider](data-utilities/dir-mapper-2d-slider): Creates a GLSL grid map from the number of files within an input directory, 2D Slider file navigator.

  - [dir-watcher](data-utilities/dir-watcher): Populate a Table DAT with arbitrary directory (files with sizes and last-modified, also hidden).

  - [extensions](data-utilities/extensions): Template for abstractions (e.g.): `op('xyz').myFunction()` wrapped within a Container object with GUI visibility.

  - [get-running-apps](data-utilities/get-running-apps): Populate Table DAT with running processes, PID, session name and memory usage (like task manager, hides CMD).

  - [info-getter](data-utilities/info-getter): A Text DAT execution on video file finish, creates a callback from video info channel.

  - [open-apps](data-utilities/open-apps): Launch `.exe` applications found in provided paths, e.g. `"C:\\Program Files (x86)"`, threaded search from string input.

  - [resolume-xml-parser](data-utilities/resolume-xml-parser): Parse a Resolume XML file with mapping values into a Table DAT (composition example with 2 layers).

  - [subprocess](data-utilities/subprocess): Execute a request from a file on the same folder deriving paths (hides CMD using opened TD session).

  - [timecode-txt-matcher](data-utilities/timecode-txt-matcher): Matches the cycles of a Timer CHOP with a text file with timecodes per line: `00:00:05, chan3, random`, a continuous event executor. Tested TouchDesigner 2025.32460.

  - [venv-creator](data-utilities/venv-creator): Creates a separate `venv\` (blocking), installs numpy and adds to `sys`, `import numpy as np` works then.



- [graphics](graphics)


  - [feedback-blur](graphics/feedback-blur): Fragment shader combining two input textures using additive blending with opacity control.

  - [feedback-shape-saver](graphics/feedback-shape-saver): Primitive shape color feedback with Movie File Out TOP export (composite on transparent background).

  - [ffmpeg-export-img](graphics/ffmpeg-export-img): Use `FFMPEG` to export an image from a Null TOP of the same size, tested TouchDesigner 2025.32460.

  - [glsl1-barrel](graphics/glsl1-barrel): `BarrelDistortion.frag` shader on input video file, affects 4 corners.

  - [glsl2-pingpong](graphics/glsl2-pingpong): Ping-Pong Delay shader, feedback 0-1 (using `.vs` file).

  - [glsl3-kaleidoscope](graphics/glsl3-kaleidoscope): Kaleidoscope GLSL shader, exposes division and rotation controls (using `.frag` file).

  - [kohonen-map-2d](graphics/kohonen-map-2d): A 2D Kohonen Self-Organising Map in raw Python training 400 epochs (async mode does not break UI), tested TouchDesigner 2025.32460.

  - [numpy-feedback-img](graphics/numpy-feedback-img): A script using `numpyArray` with Script TOP to create feedback on incoming video, tested TouchDesigner 2025.32460.

  - [numpy-noise-img](graphics/numpy-noise-img): A script using `numpyArray` with Script TOP to create noise on incoming video, tested TouchDesigner 2025.32460.

  - [numpy-pixel-sorting](graphics/numpy-pixel-sorting): A script using `numpyArray` with Script TOP with pixel sorting effect, tested TouchDesigner 2025.32460.

  - [numpy-pixelate-img](graphics/numpy-pixelate-img): A script using `numpyArray` with Script TOP to pixelate (mosaic) incoming video, tested TouchDesigner 2025.32460.

  - [timer-subtitles-3d](graphics/timer-subtitles-3d): Reads randomly generated sentences from a Table DAT, works on timer and displays with geometry to texture.

  - [video-mosaic-wall](graphics/video-mosaic-wall): Creates a 10x10 video mosaic in Geometry from `Texture 3D`.


- [network-ai](network-ai)


  - [ig20-iegeekcam](network-ai/ig20-iegeekcam): IG-20 ieGeek IP camera video stream player for TouchDesigner, tested: 2022.32120. Comes with an `arp` scanner for local network and blob track. The equipment has sensor-triggered night vision shown in the floating window.

  - [ollama-web-client](network-ai/ollama-web-client): Communication with Ollama using Web Client DAT, tested TouchDesigner 2025.32460 and `gemma3:1b` model.

  - [openrouter-web-client](network-ai/openrouter-web-client): Communication with OpenRouter API using Web Client DAT, tested TouchDesigner 2025.32460 and `nvidia/nemotron-nano-12b-v2-vl:free` model.

  - [openstreetmap-search](network-ai/openstreetmap-search): Search OpenStreetMap and render to texture, input a string with the location, tested TouchDesigner 2025.31310.

  - [tcp-io](network-ai/tcp-io): Server with TCP io between TouchDesigner session DAT and CMD (start `tcp_server.py` first).

  - [web-server-internal](network-ai/web-server-internal): Internal Web Server DAT with external communication such as `tcp-io` folder.



References:
1. https://derivative.ca/
2. https://www.resolume.com/
3. https://ollama.com/
4. https://www.akaipro.com/
5. https://openrouter.ai/
6. https://www.openstreetmap.org/
