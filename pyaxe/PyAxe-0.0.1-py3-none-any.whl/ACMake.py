import os
import multiprocessing
from . import AOS, AVS


class BuildParams:
    OS_CALL_TYPE_SYSTEM = 0  # AOS.system
    OS_CALL_TYPE_PROCESS = 1  # AOS.process

    def __init__(self, buildDir, sourceDir, installDir, buildTypes):
        """
        :param buildDir: 构建目录
        :param sourceDir: 根 CMakeLists.txt 所在目录；如果是相对路径，则为相对于buildDir的路径
        :param installDir: 安装目录（--prefix）
        :param buildTypes: 构建类型列表(Debug or Release)
        """
        self.buildDir = buildDir
        self.sourceDir = sourceDir
        self.installDir = installDir
        self.buildTypes = buildTypes

        self.extraCMakeOptions = ''  # 额外的CMake选项，比如 -Dxxx=yyy

        # 生成64位程序
        # Linux下若要编译32位，需要修改CMakeLists.txt: set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m32")
        self.x64 = True

        self.win32_vsVersion = 12  # 在Windows上构建时，使用的VS版本号

        self.unix_makeEncoding = 'iso-8859-1'  # 执行make时使用的encoding（仅当osCallType为OS_CALL_TYPE_PROCESS时才需要指定）
        self.unix_makeJobCount = multiprocessing.cpu_count() - 2  # 执行make时的并发job数量

        self.osCallType = self.OS_CALL_TYPE_SYSTEM  # 调用命令行的方式

    @property
    def generator(self):
        if os.name == 'nt':
            return ('Visual Studio %d' % self.win32_vsVersion) + (' Win64' if self.x64 else '')
        else:
            return 'Unix Makefiles'

    @property
    def unix_makeJobCountStr(self):
        if self.unix_makeJobCount >= 2:
            return '-j%d' % self.unix_makeJobCount
        else:
            return ''

    @property
    def osCall(self):
        def wrapperSystem(cmd, encoding=None):
            return AOS.system(cmd)

        if self.osCallType == self.OS_CALL_TYPE_SYSTEM:
            return wrapperSystem
        elif self.osCallType == self.OS_CALL_TYPE_PROCESS:
            return AOS.process
        else:
            assert False


def _cmake_win32(buildParams):
    AOS.makeDir(buildParams.buildDir)
    with AOS.ChangeDir(buildParams.buildDir):
        buildParams.osCall('cmake -G "%s" %s -DCMAKE_INSTALL_PREFIX="%s" %s' % (
            buildParams.generator,
            buildParams.sourceDir,
            buildParams.installDir,
            buildParams.extraCMakeOptions
        ))
        for buildType in buildParams.buildTypes:
            # 注意/t:INSTALL会失败
            buildParams.osCall(
                r'%s %s /t:build /p:Configuration=%s /p:BuildInParallel=true /m'
                % (AVS.Path(buildParams.win32_vsVersion).MSBuildEXE, 'INSTALL.vcxproj', buildType)
            )

def _cmake_unix(buildParams):
    for buildType in buildParams.buildTypes:
        buildDir = os.path.join(buildParams.buildDir, buildType)
        AOS.makeDir(buildDir)
        with AOS.ChangeDir(buildDir):
            buildParams.osCall('cmake -G "%s" %s -DCMAKE_INSTALL_PREFIX="%s" -DCMAKE_BUILD_TYPE=%s %s' % (
                buildParams.generator,
                buildParams.sourceDir,
                buildParams.installDir,
                buildType,
                buildParams.extraCMakeOptions
            ))
            buildParams.osCall('make VERBOSE=1 %s' % buildParams.unix_makeJobCountStr, buildParams.unix_makeEncoding)
            buildParams.osCall('make install', buildParams.unix_makeEncoding)

def cmake(buildParams):
    if os.name == 'nt':
        _cmake_win32(buildParams)
    else:
        _cmake_unix(buildParams)
