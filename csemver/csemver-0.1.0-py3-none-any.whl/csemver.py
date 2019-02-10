import semver as sv;
import copy
__author__ = "Sebastian Tilders"
__version__ = "0.1.0"

class csemver:
	""" Representation of an semantic software version """

	__slots__ = ['major', 'minor', 'patch', 'prerelease', 'build', '_version', '_vInfo'];
	def __init__(self, version:str = "0.1.0"):
		""" Initialises a new Version instance"""
		self._version = sv.parse(version);
		self._updateVI();
	
	@property
	def number(self):
		"""
		Propery which contains directory for the current version.
		
		Delete this property to reset the version to 0.1.0
		"""
		return self._version;

	@number.setter
	def number(self,value):
		""" Setter for the version number """
		self._version = sv.parse(value);
		self._updateVI();

	@number.deleter
	def number(self):
		""" Resets version number to 0.1.0 """
		self._version = sv.parse("0.1.0");
		self._updateVI();

	def incPatch(self, incBy:int=1):
		""" Increase patch version x.y.z -> x.y.(z+incBy) """
		verStr = self._bumpN(sv.bump_patch, incBy);
		self._version = sv.parse(verStr);
		self._updateVI();
		return self;

	def incMinor(self,incBy:int=1):
		""" Increase minor version x.y.z -> x.(y+incBy).0 """
		verStr = self._bumpN(sv.bump_minor,incBy);
		self._version = sv.parse(verStr);
		self._updateVI();
		return self;

	def incMajor(self, incBy:int=1):
		""" Increase major version x.y.z -> (x+incBy).0.0 """
		verStr = self._bumpN(sv.bump_major, incBy);
		self._version = sv.parse(verStr);
		self._updateVI();
		return self;

	def __getitem__(self, key):
		""" Returns either major, minor, patch, prerelease or build """
		return self._version[key];

	def __str__(self):
		""" Returns a string representation of the semantic version """
		return sv.format_version(self._version['major'], self._version['minor'], self._version['patch'], self._version['prerelease'], self._version['build']);

	def _convertToVersion(self, val):
		return sv.VersionInfo(self._version['major'], self._version['minor'], self._version['patch'], self._version['prerelease'], self._version['build']);

	def _updateVI(self):
		self._vInfo = self._convertToVersion(self._version);

	def _bumpN(self, func, incBy):
		verStr = str(self);
		for i in range(0, incBy):
			verStr = func(verStr);
		return verStr;

	def __eq__(self, value):
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		return self._vInfo == value._vInfo;

	def __gt__(self, value):
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		return self._vInfo > value._vInfo;

	def __lt__(self, value):
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		return self._vInfo < value._vInfo;

	def __le__(self, value):
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		return self._vInfo <= value._vInfo;

	def __ge__(self, value):
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		return self._vInfo >= value._vInfo;

	def __ne__(self, value):
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		return self._vInfo != value._vInfo;

	def __add__(self, value):
		"""
		Suppports addition of versions. The addition respects the semver rules
		"""
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		newV = copy.deepcopy(self);
		newV.incMajor(value['major']);
		newV.incMinor(value['minor']);
		newV.incPatch(value['patch']);
		return newV;

	def __iadd__(self, value):
		"""
		Suppports addition + assignment of versions. The addition respects the semver rules
		"""
		if not isinstance(value,csemver):
			raise TypeError("This type combination is not supported!");
		self.incMajor(value['major']);
		self.incMinor(value['minor']);
		self.incPatch(value['patch']);
		return self;

	def __repr__(self):
		return "{:}<{:}> instance at 0x{:016X}".format(self.__class__.__name__,self.__str__(), id(self));

def parse(version):
	return csemver(version);