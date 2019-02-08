#!/usr/bin/env python3

import os, shlex, argparse

__title__ = "diarrhouea"
__description__ = "Simple terminal emulator"
__version__ = "1.0.0"

config = {}

arg_parser = None

window = None
terminal = None

CONFIG_FILE_PATH = os.path.expanduser("~/.diarrhouearc")

def main():
	read_config()
	parse_args()
	
	setup_gtk()
	setup_terminal()
	
	window.show_all()
	
	Gtk.main()

def read_config():
	try:
		config_file = open(CONFIG_FILE_PATH, "r")
	except FileNotFoundError:
		open(CONFIG_FILE_PATH, "w+").close()
		
		return
	
	os.sys.argv = (
		os.sys.argv[0:1] +
		shlex.split(config_file.read()) +
		os.sys.argv[1:]
	)
def parse_args():
	global arg_parser
	
	arg_parser = argparse.ArgumentParser(
		__title__, None, __description__
	)
	
	text_blink_modes = ("never", "focused", "unfocused", "always")
	cursor_blink_modes = ("system", "always", "never")
	cursor_shapes = ("block", "ibeam", "underline")
	
	arg_parser.add_argument("-v", "--version",
		action="version",
		version=__title__ + " " + __version__
	)
	
	arg_parser.add_argument("-b", "--no-bold",
		action="store_false",
		dest="allow-bold",
		
		help="disable bold text"
	)
	arg_parser.add_argument("-B", "--yes-bold",
		action="store_true",
		dest="allow-bold",
		
		default=True,
		
		help="enable bold text (default)"
	)
	
	arg_parser.add_argument("-s", "--no-bold-is-bright",
		action="store_false",
		dest="bold-is-bright",
		
		help="disable bold text brightening"
	)
	arg_parser.add_argument("-S", "--yes-bold-is-bright",
		action="store_true",
		dest="bold-is-bright",
		
		default=True,
		
		help="enable bold text brightening (default)"
	)
	
	arg_parser.add_argument("-l", "--no-hyperlinks",
		action="store_false",
		dest="allow-hyperlinks",
		
		help="disable hyperlinks"
	)
	arg_parser.add_argument("-L", "--yes-hyperlinks",
		action="store_true",
		dest="allow-hyperlinks",
		
		default=True,
		
		help="enable hyperlinks (default)"
	)
	
	arg_parser.add_argument("-a", "--no-audible-bell",
		action="store_false",
		dest="audible-bell",
		
		help="disable audible bell"
	)
	arg_parser.add_argument("-A", "--yes-audible-bell",
		action="store_true",
		dest="audible-bell",
		
		default=True,
		
		help="enable audible bell (default)"
	)
	
	arg_parser.add_argument("-c", "--background-color",
		action="store",
		dest="background-color",
		
		help="set background color"
	)
	arg_parser.add_argument("-g", "--foreground-color",
		action="store",
		dest="foreground-color",
		
		help="set foreground color"
	)
	
	arg_parser.add_argument("-p", "--palette",
		action="store",
		dest="palette",
		
		help="set palette (8, 16 or 256 colors separated by colons)"
	)
	
	arg_parser.add_argument("-t", "--text-blink-mode",
		choices=text_blink_modes,
		dest="text-blink-mode",
		
		default="always",
		
		help="set text blink mode (always is default)"
	)
	
	arg_parser.add_argument("-C", "--cursor-background-color",
		action="store",
		dest="cursor-background-color",
		
		help="set cursor background color"
	)
	arg_parser.add_argument("-G", "--cursor-foreground-color",
		action="store",
		dest="cursor-foreground-color",
		
		help="set cursor foreground color"
	)
	
	arg_parser.add_argument("-T", "--cursor-blink-mode",
		choices=cursor_blink_modes,
		dest="cursor-blink-mode",
		
		default="system",
		
		help="set cursor blink mode (system is default)"
	)
	
	arg_parser.add_argument("-x", "--cursor-shape",
		choices=cursor_shapes,
		dest="cursor-shape",
		
		default="block",
		
		help="set cursor shape (block is default)"
	)
	
	arg_parser.add_argument("-f", "--font",
		action="store",
		dest="font",
		
		help="set used font"
	)
	
	arg_parser.add_argument("-w", "--no-rewrap-on-resize",
		action="store_false",
		dest="rewrap-on-resize",
		
		help="disable rewrapping on resize"
	)
	arg_parser.add_argument("-W", "--yes-rewrap-on-resize",
		action="store_true",
		dest="rewrap-on-resize",
		
		default=True,
		
		help="enable rewrapping on resize (default)"
	)
	
	arg_parser.add_argument("-k", "--no-scroll-on-keystroke",
		action="store_false",
		dest="scroll-on-keystroke",
		
		help="disable scrolling on keystroke"
	)
	arg_parser.add_argument("-K", "--yes-scroll-on-keystroke",
		action="store_true",
		dest="scroll-on-keystroke",
		
		default=True,
		
		help="enable scrolling on keystroke (default)"
	)
	
	arg_parser.add_argument("-o", "--no-scroll-on-output",
		action="store_false",
		dest="scroll-on-output",
		
		help="disable scrolling on output"
	)
	arg_parser.add_argument("-O", "--yes-scroll-on-output",
		action="store_true",
		dest="scroll-on-output",
		
		default=True,
		
		help="enable scrolling on output (default)"
	)
	
	arg_parser.add_argument("-r", "--scrollback-lines",
		action="store",
		dest="scrollback-lines",
		
		type=int,
		default=4096,
		
		help="set number of scrollback lines (negative values result infinite scrollback)"
	)
	
	args = vars(arg_parser.parse_args())
	
	for arg in (
		"allow-bold",
		"bold-is-bright",
		"allow-hyperlinks",
		"audible-bell",
		"background-color",
		"foreground-color",
		"palette",
		"cursor-background-color",
		"cursor-foreground-color",
		"rewrap-on-resize",
		"scroll-on-keystroke",
		"scroll-on-output",
		"scrollback-lines",
		"font"
	):
		config[arg] = args[arg]
	
	config["text-blink-mode"] = text_blink_modes.index(
		args["text-blink-mode"]
	)
	config["cursor-blink-mode"] = cursor_blink_modes.index(
		args["cursor-blink-mode"]
	)
	config["cursor-shape"] = cursor_shapes.index(
		args["cursor-shape"]
	)

def setup_gtk():
	global gi, GLib, Gdk, Gtk, Pango, Vte
	global terminal, window
	
	import gi
	
	gi.require_version("GLib", "2.0")
	gi.require_version("Gdk", "3.0")
	gi.require_version("Gtk", "3.0")
	gi.require_version("Pango", "1.0")
	gi.require_version("Vte", "2.91")
	
	from gi.repository import GLib, Gdk, Gtk, Pango, Vte
	
	window = Gtk.Window()
	terminal = Vte.Terminal()
	
	window.add(terminal)
	
	window.connect("destroy", Gtk.main_quit)
	
	terminal.connect("child-exited", Gtk.main_quit)
def setup_terminal():
	def parse_color(color):
		if not color:
			return None
		
		rgba = Gdk.RGBA()
		
		if not rgba.parse(color):
			arg_parser.error("'{}' is not a valid color".format(color))
		
		return rgba
	def parse_palette(raw_palette):
		if not raw_palette:
			return None
		
		palette = raw_palette.split(":")
		
		if not len(palette) in (8, 16, 256):
			arg_parser.error("{} is not a valid palette size".format(
				len(palette)
			))
		
		rgba_list = []
		
		for color in palette:
			if not color:
				arg_parser.error("all of palette colors must be specified")
			
			rgba_list.append(parse_color(color))
		
		return rgba_list
	
	terminal.set_allow_bold(config["allow-bold"])
	terminal.set_bold_is_bright(config["bold-is-bright"])
	terminal.set_allow_hyperlink(config["allow-hyperlinks"])
	terminal.set_audible_bell(config["audible-bell"])
	terminal.set_colors(
		parse_color(config["foreground-color"]),
		parse_color(config["background-color"]),
		parse_palette(config["palette"])
	)
	terminal.set_text_blink_mode(config["text-blink-mode"])
	terminal.set_color_cursor(parse_color(
		config["cursor-background-color"]
	))
	terminal.set_color_cursor_foreground(parse_color(
		config["cursor-foreground-color"]
	))
	terminal.set_cursor_blink_mode(config["cursor-blink-mode"])
	terminal.set_cursor_shape(config["cursor-shape"])
	terminal.set_font(Pango.FontDescription.from_string(
		config["font"]
	) if config["font"] else None)
	terminal.set_rewrap_on_resize(config["rewrap-on-resize"])
	terminal.set_scroll_on_keystroke(config["scroll-on-keystroke"])
	terminal.set_scroll_on_output(config["scroll-on-output"])
	terminal.set_scrollback_lines(config["scrollback-lines"])
	
	terminal.spawn_sync(
		Vte.PtyFlags.DEFAULT, # Do nothing
		None, # Keep initial child cwd the same as parent cwd
		[os.getenv("SHELL", "/bin/sh")], # Set path (zeroth argv) as currently used shell
		None, # Don't do anything with environment variables
		GLib.SpawnFlags.DEFAULT, # Do nothing (DO_NOT_REAP_CHILD is provided automatically)
		None, # Don't do any child setup
		None, # See comment above
		None # Don't do anything with event cancelability
	)

if __name__ == "__main__":
	main()
