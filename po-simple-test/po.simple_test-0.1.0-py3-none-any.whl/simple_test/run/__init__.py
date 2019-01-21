from .run import createRun
import subprocess

run = createRun(subprocess.run)

__all__ = ["run"]
