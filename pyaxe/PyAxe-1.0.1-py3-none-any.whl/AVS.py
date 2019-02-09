import os


class Path:
    def __init__(self, version):
        """
        :param version: a number such as 9, 10, 12
        """
        if os.name == 'nt':
            self.CommonTools = os.environ['VS%d0COMNTOOLS' % version]
        else:
            self.CommonTools = ''
        self.Root = os.path.normpath(os.path.join(self.CommonTools, '..', '..'))
        self.IDE = os.path.normpath(os.path.join(self.CommonTools, '..', 'IDE'))
        self.VC = os.path.join(self.Root, 'VC')
        self.VC_Bin = os.path.join(self.VC, 'bin')

        self.DevenvEXE = os.path.join(self.IDE, 'devenv.exe')
        self.MSBuildEXE = r'"C:\Program Files (x86)\MSBuild\%d.0\Bin\MSBuild.exe"' % version
        
