from .projects.pybuild import CXXToolchain as PamCXXToolchain
from .projects.toolchain import ToolchainExtender
from .tools.gnu import GNUToolFactory

tools = GNUToolFactory()
gcc = PamCXXToolchain("linux-gcc")
tools.configure(gcc)

