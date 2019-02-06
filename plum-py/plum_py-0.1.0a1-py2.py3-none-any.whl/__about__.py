
__all__ = ('__title__', '__summary__', '__uri__', '__version_info__',
           '__version__', '__author__', '__maintainer__', '__email__',
           '__copyright__', '__license__')

__title__        = "plum-py"
__summary__      = "Pack/Unpack Memory."
__uri__          = "https://gitlab.com/dangass/plum"
__version_info__ = type("version_info", (), dict(serial=1,
                        major=0, minor=1, micro=0, releaselevel="alpha"))
__version__      = "{0.major}.{0.minor}.{0.micro}{1}{2}".format(__version_info__,
                   dict(final="", alpha="a", beta="b", rc="rc")[__version_info__.releaselevel],
                   "" if __version_info__.releaselevel == "final" else __version_info__.serial)
__author__       = "Dan Gass"
__maintainer__   = "Dan Gass"
__email__        = "dan.gass@gmail.com"
__copyright__    = "Copyright 2019 Daniel Mark Gass"
__license__      = "MIT License ; http://opensource.org/licenses/MIT"
