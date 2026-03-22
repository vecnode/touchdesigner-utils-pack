## TouchDesigner utilities pack

A set of TouchDesigner utilities and projects, tested Windows 11 and RTX 3090/3070.

- [akai-apc40mk2-colors](akai-apc40mk2-colors): Control 8x5 pad colors on Akai APC40MK2 MIDI Controller, tested TouchDesigner 2025.32460.

- [akai-apc40mk2-midi](akai-apc40mk2-midi): MIDI template for Akai APC40MK2 MIDI Controller, tested TouchDesigner 2022.32120. Requires to set the MIDI mapping dialog as device in. The MIDI codes are set for callback automatically at startup.

- [audio-mixer-fades](audio-mixer-fades): Trigger independent audio track fade in/out on button click, able to range, and master on/off (from 0-1).

- [audio-play-callback](audio-play-callback): Custom callback on sample length of an Audio Play CHOP to allow logic when audio files stop playing (trigger a panel when audio finishes).

- [dir-mapper-2d-slider](dir-mapper-2d-slider): Creates a GLSL grid map from the number of files within an input directory, 2D Slider file navigator.

- [dir-watcher](dir-watcher): Populate a Table DAT with arbitrary directory (files with sizes and last-modified, also hidden).

- [extensions](extensions): Template for abstractions (e.g.): `op('xyz').myFunction()` wrapped within a Container object with GUI visibility.

- [feedback-blur](feedback-blur): Fragment shader combining two input textures using additive blending with opacity control.

- [feedback-shape-saver](feedback-shape-saver): Primitive shape color feedback with Movie File Out TOP export (composite on transparent background).

- [get-running-apps](get-running-apps): Populate Table DAT with running processes, PID, session name and memory usage (like task manager, hides CMD).

- [glsl1-barrel](glsl1-barrel): `BarrelDistortion.frag` shader on input video file, affects 4 corners.

- [glsl2-pingpong](glsl2-pingpong): Ping-Pong Delay shader, feedback 0-1 (using `.vs` file).

- [ig20-iegeekcam](ig20-iegeekcam): IG-20 ieGeek IP camera video stream player for TouchDesigner, tested: 2022.32120. Comes with an arp scanner for local network and blob track. The equipment has sensor-triggered night vision shown in the floating window.

- [info-getter](info-getter): A Text DAT execution on video file finish, creates a callback from video info channel.

- [link-two-containers](link-two-containers): A Select CHOP operator showing widget on container A triggered on container B (same logic as "send" and "receive" in MaxMSP).

- [midi-to-vst](midi-to-vst): Boolean logic to send `onNoteOn()` and `onNoteOff()` to arbitrary VST3s.

- [numpy-feedback-img](numpy-feedback-img): A script using `numpyArray` with Script TOP to create feedback on incoming video, tested TouchDesigner 2025.32460.

- [numpy-noise-img](numpy-noise-img): A script using `numpyArray` with Script TOP to create noise on incoming video, tested TouchDesigner 2025.32460.

- [numpy-pixel-sorting](numpy-pixel-sorting): A script using `numpyArray` with Script TOP with pixel sorting effect, tested TouchDesigner 2025.32460.

- [numpy-pixelate-img](numpy-pixelate-img): A script using `numpyArray` with Script TOP to pixelate (mosaic) incoming video, tested TouchDesigner 2025.32460.

- [ollama-web-client](ollama-web-client): Communication with Ollama using Web Client DAT, tested TouchDesigner 2025.32460 and `gemma3:1b` model.

- [open-apps](open-apps): Launch `.exe` applications found in provided paths, e.g. `"C:\\Program Files (x86)"`, threaded search from string input.

- [resolume-xml-parser](resolume-xml-parser): Parse a Resolume XML file with mapping values into a Table DAT (composition example with 2 layers).

- [subprocess](subprocess): Execute a request from a file on the same folder deriving paths (hides CMD using opened TD session).

- [tcp-io](tcp-io): Server with TCP io between TouchDesigner session DAT and CMD (start `tcp_server.py` first).

- [timecode-txt-matcher](timecode-txt-matcher): Matches the cycles of a Timer CHOP with a text file with timecodes per line: `00:00:05, chan3, random`, a continuous event executor. Tested TouchDesigner 2025.32460.

- [timer-subtitles-3d](timer-subtitles-3d): Reads randomly generated sentences from a Table DAT, works on timer and displays with geometry to texture.

- [venv-creator](venv-creator): Creates a separate `venv\` (blocking), installs numpy and adds to `sys`, `import numpy as np` works then.

- [video-mosaic-wall](video-mosaic-wall): Creates a 10x10 video mosaic in Geometry from `Texture 3D`.

- [web-server-internal](web-server-internal): Internal Web Server DAT with external communication such as `tcp-io` folder.


References:
1. https://derivative.ca/
2. https://www.resolume.com/
3. https://ollama.com/
4. https://www.akaipro.com/
