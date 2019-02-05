import inspect
from pathlib import Path
import subprocess

PLIST = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
 <key>KeepAlive</key>
 <true/>
 <key>Label</key>
 <string>net.schinckel.homekit-display-switch</string>
 <key>ProgramArguments</key>
 <array>
  <string>{path}</string>
 </array>
 <key>RunAtLoad</key>
 <true/>
</dict>
</plist>'''  # NOQA

target_file = Path('~/Library/LaunchAgents/net.schinckel.homekit-display-switch.plist').expanduser()


def main():
    # We need to see if we can look at the first item on the stack to see where we were called
    # from, and see if our matching 'homekit-display-switch' command is in there, because
    # we want to use that as the path.
    top = inspect.stack()[-1]
    path = Path(top.filename).parent / 'homekit-display-switch'
    if path.exists():
        data = PLIST.format(path=path.resolve())
        target_file.write_text(data)
        subprocess.call([
            'launchctl', 'load', '-w', target_file
        ])
    else:
        raise Exception('Unable to find "homekit-display-switch".')
