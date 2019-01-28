import pip
from subprocess import call
from pip._internal.utils.misc import get_installed_distributions


for dist in get_installed_distributions():
	"""Auto upgrade all the pip outdate package. """
    call("pip install --upgrade " + dist.project_name, shell=True)
