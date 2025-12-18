## TouchDesigner utilities pack

A set of TouchDesigner utilities and projects for audiovisual work, tested on Windows 11 and RTX 3090/3070.


- **audio-mixer-fades**
    Trigger independent audio track fade in/out on button click, able to range, and master on/off (from 0-1).
- **audio-play-callback**
    Custom callback on sample length of an Audio Play CHOP to allow logic when audio files stop playing (trigger a panel when audio finishes).
- **dir-mapper-2d-slider**
    Creates a GLSL grid map from the number of files within an input directory, 2D Slider file navigator.
- **dir-watcher**
    Populate a Table DAT with arbitrary directory (files with sizes and last-modified, also hidden).
- **extensions**
    Template for abstractions (e.g.): `op('xyz').myFunction()` wrapped within a Container object with GUI visibility.
- **feedback-shape-saver**
    Simple primitive shape color feedback with Movie File Out TOP export (composite on transparent background).
- **get-running-apps**
    Populate Table DAT with running processes, PID, session name and memory usage (like task manager, hides CMD).
- **glsl1-barrel** 
    BarrelDistortion.frag shader on input video file, affects 4 corners.
- **glsl2-pingpong** 
    Ping-Pong Delay shader, feedback 0-1 (using .vs file).
- **info-getter**
    A Text DAT execution on video file finish, creates a callback from video info channel.
- **link-two-containers**
    A simple Select CHOP operator showing widget on container A triggered on container B (same logic as "send" and "receive" in MaxMSP).
- **midi-to-vst**
    Simple boolean logic to send `onNoteOn()` and `onNoteOff()` to arbitrary VST3s.
- **open-apps**
    Launch .exe applications found in provided paths, e.g. `"C:\\Program Files (x86)"`, threaded search from string input.
- **resolume-xml-parser**
    Parse a Resolume XML file with mapping values into a Table DAT (composition example with 2 layers).
- **subprocess**
    Execute a request from a file on the same folder deriving paths (hides CMD using opened TD session).
- **tcp-io**
    Simple server to illustrate TCP io between TouchDesigner session DAT and CMD (start `tcp_server.py` first).
- **timer-subtitles-3d**
    Reads randomly generated sentences from a Table DAT, works on timer and displays with geometry to texture.

- **web-server-internal**
    Internal Web Server DAT with external communication such as `tcp-io` folder.


Related repositories:
1. https://github.com/vecnode/touchdesigner-apc40mk2-midi
2. https://github.com/vecnode/touchdesigner-ig20-iegeekcam

