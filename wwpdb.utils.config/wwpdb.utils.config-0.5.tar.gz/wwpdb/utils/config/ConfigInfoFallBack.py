##
# File:    ConfigInfoFallBack.py
# Date:    4-Apr-2016
#
# Updates:
#       4-Apr-2016  jdw split these methods out of ConfigInfoFile()
##
"""
Utilities for accessing and managing legacy configuration options.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


import sys
import string
import traceback

from wwpdb.utils.config.ConfigInfoData import ConfigInfoData


class ConfigInfoFallBack(object):
    """
    Utilities for accessing and managing legacy configuration options.

    """

    def __init__(self, verbose=False, log=sys.stderr):
        self.__versbose = verbose
        self.__lfh = log
        self.__debug = False
        #

    def getSiteFallbackDictionary(self, siteId):
        """ Return the fallback dictionary of options and values bypassing any existing cache files.

            This method is used primarily for testing configuration file data relative to legacy inline configuration.

        """
        cI = ConfigInfoData(siteId=siteId, useCache=False)
        cD = cI.getConfigDictionary()
        return cD

    def getFallBackConfig(self, siteId):
        """ Get the current default fallback settings for the input siteId.

        Skip any cache processing.

        Options are returned for easy packaging in configuration data files including the automatic insertion
        of substitution templates for common substrings.

        Skip special internal configuration dictionaries -

        ['FILE_FORMAT_EXTENSION_DICTIONARY', 'CONTENT_TYPE_DICTIONARY', 'CONTENT_MILESTONE_LIST', 'CONTENT_TYPE_BASE_DICTIONARY']

        Return: siteSpD dictionary containing site specific config options
                siteCmD dictionary containing common config options
                derList contains the list of keys with symbolic replacements -

        """
        # Extract the default configuration data from the current ConfigInfoData class -
        # Dictionaries to capture options and values for site specific and common sections
        #
        substList = []
        cD = {}
        pD = {}
        rD = {}
        cmD = {}
        spD = {}
        try:
            cI = ConfigInfoData(siteId=siteId, useCache=False)
            cD = cI.getConfigDictionary()
            pD = cI.getConfigParamDictionary()
            rD = cI.getSiteReplacementDictionary()
            #
            # Include reasonable substitutions patterns in the configuration values --
            #
            tokenList = ['PACKAGE_PATH', 'TOOLS_PATH', 'DATA_PATH', 'TOP_SOURCE_PATH', 'REFERENCE_PATH', 'RESOURCE_PATH',
                         'DEPLOY_PATH', 'SESSION_DIR_NAME', 'SITE_PREFIX']
            for token in tokenList:
                if token in pD:
                    subSt = pD[token]
                    for ky in cD:
                        if cD[ky] is not None and subSt in str(cD[ky]):
                            tS = string.replace(str(cD[ky]), subSt, "%%(%s)s" % token.lower(), 1)
                            cD[ky] = tS
                            substList.append(ky)
                    for ky in rD:
                        if rD[ky] is not None and subSt in str(rD[ky]):
                            tS = string.replace(str(rD[ky]), subSt, "%%(%s)s" % token.lower(), 1)
                            rD[ky] = tS
                            if ky not in substList:
                                substList.append(ky)
            #
            # spD <- 1) all of pD,  2) rD if not in substList
            # cmD <- cD if not in rD
            #
            spD = {}
            spD.update(pD)
            spD.update(rD)
            #
            cmD = {}
            for k, v in cD.items():
                if k in rD or k in pD:
                    continue
                cmD[k] = v
        except:
            self.__lfh.write("%s.%s failed assembling configuration data for %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, siteId))
            traceback.print_exc(file=self.__lfh)

        return spD, cmD, substList, pD, rD, cD

    def getCommonOptions(self, siteD):
        """Determine common fallbackup options among sites within each config location.

           Returns a dictionary of configuration options with common values organized by location.


        """
        # These class-level configuration options remain in the ConfigInfoData() class and are not
        #                        migrated to configuration files --
        specialList = ['FILE_FORMAT_EXTENSION_DICTIONARY',
                       'CONTENT_TYPE_DICTIONARY',
                       'CONTENT_MILESTONE_LIST',
                       'CONTENT_TYPE_BASE_DICTIONARY',
                       'SITE_DATASET_ID_ASSIGNMENT_DICTIONARY',
                       'PROJECT_DEPOSIT_SERVICE_DICTIONARY']
        siteLocCmD = {}
        try:
            allSpD = {}
            allCmD = {}
            for siteLoc in siteD:
                siteIdList = siteD[siteLoc]
                locSpD = {}
                locCmD = {}
                for siteId in siteIdList:
                    spD, cmD, subList, pD, rD, cD = self.getFallBackConfig(siteId=siteId)
                    if self.__debug:
                        self.__lfh.write("Location %s site %s length spD %d length cmD %d\n" % (siteLoc, siteId, len(spD), len(cmD)))
                    locSpD[siteId] = spD
                    locCmD[siteId] = cmD
                allSpD[siteLoc] = locSpD
                allCmD[siteLoc] = locCmD

            for siteLoc1 in allCmD:
                keyL = []
                sD = allCmD[siteLoc1]
                for siteId in sD:
                    cD = sD[siteId]
                    keyL.extend(cD.keys())

                keyL = list(set(keyL) - set(specialList))
                if self.__debug:
                    self.__lfh.write("Location %s unique common candidate option keys %d\n" % (siteLoc1, len(keyL)))

                locD = allCmD[siteLoc1]
                mmL = []
                for siteId1 in locD:
                    for siteId2 in locD:
                        if siteId1 >= siteId2:
                            continue
                        cD1 = locD[siteId1]
                        cD2 = locD[siteId2]
                        for ky in keyL:
                            if ky in cD1 and ky in cD2 and cD1[ky] == cD2[ky]:
                                continue
                            elif ky not in cD1:
                                # self.__lfh.write("Option missing for site %s key %s\n" % (siteId1, ky))
                                continue
                            elif ky not in cD2:
                                # self.__lfh.write("Option missing for site %s key %s\n" % (siteId2, ky))
                                continue
                            else:
                                if self.__debug:
                                    self.__lfh.write("Option mismatch site %s site %s key %s %r %r\n" % (siteId1, siteId2, ky, cD1[ky], cD2[ky]))
                                mmL.append(ky)
                cL = list(set(keyL) - set(mmL))
                if self.__debug:
                    self.__lfh.write("\n-------------------------------------------------------------------------\n")
                    self.__lfh.write("Location %s common option list length %d\n" % (siteLoc1, len(cL)))
                siteLocCmD[siteLoc1] = (cL, keyL)
        except:
            self.__lfh.write("%s.%s failing siteD %r\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, siteD))
            traceback.print_exc(file=self.__lfh)

        return siteLocCmD
