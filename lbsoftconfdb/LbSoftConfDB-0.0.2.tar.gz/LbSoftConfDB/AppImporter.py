#!/usr/bin/env python
"""
A script to add a project to the Software Configuration DB

"""
import logging
import os
import re
import sys
import urllib2
import json

from LbCommon.Processes import callCommand
from LbSoftConfDB.SoftConfDB import SoftConfDB
from LbCommon.CMake import getHeptoolsVersion, getGaudiUse
from LbEnv import fixProjectCase

def importerTranslateProject(p, v):
    ''' Function needed to prevent LCGCMT to be passed to translateProject
    as that does not work '''
    if p.lower() == "lcgcmt" or p.lower() == "lcg":
        return (p.upper(), v)
    else:
        return (fixProjectCase(p), v)

class GitlabProject:
    """ Helper class to manager projects hosted in gitlab """

    def __init__(self, project, version, sourceuri):

        ## SourceURI like: gitlab-cern:LHCb-SVN-mirrors/Brunel#v50r1

        self.log = logging.getLogger()
        self.project = project.upper()
        self.version = version

        # Hack alert: This should NOT be here, we need to find a correct location
        # for all the  location for the constants for CERN gitlab...
        self.gitlabHTTPSURL =  "https://gitlab.cern.ch"
        self.gitlabSSHURL = "ssh://git@gitlab.cern.ch:7999"
        self.gitlabViewURL = "https://gitlab.cern.ch"

        from urlparse import  urlsplit
        self.sourceuri = sourceuri
        url = urlsplit(sourceuri)
        self.scheme = url.scheme
        self.path = url.path

        tmp = self.path.split("/")
        if len(tmp) == 2:
            self.gitlabGroup = tmp[0]
            self.gitlabName = tmp[1]
        elif len(tmp) == 1:
            self.log.warning("Path without Group/Name: %s, using lhcb group by default" % self.path)
            self.gitlabGroup = "lhcb"
            self.gitlabName = tmp[0]
 

    def getURL(self, file=None):
        """ Returns the URL at which files can be found in gitlab
        e.g. https://gitlab.cern.ch/gaudi/Gaudi/raw/v27r0/CMakeLists.txt
        """
        prefix =  self.gitlabViewURL + "/" \
                 + self.gitlabGroup + "/" + self.gitlabName + "/raw/" \
                 + self.version
        if file != None:
            return prefix + "/" + file
        else:
            return prefix

    def getToolchain(self):
        self.toolchainurl = self.getURL("toolchain.cmake")
        self.log.warning("Reading toolchain.cmake from: %s" %self.toolchainurl)
        response = urllib2.urlopen(self.toolchainurl)
        data = response.read()
        self.log.debug("Got: %s" % self.toolchainurl)
        return data

    def getCMakeLists(self):
        self.cmakelistsurl = self.getURL("CMakeLists.txt")
        self.log.debug("Getting: %s" % self.cmakelistsurl)
        try:
            response = urllib2.urlopen(self.cmakelistsurl)
            data = response.read()
            self.log.debug("Got: %s" % self.cmakelistsurl)
        except:
            self.log.warning("Could not find CMakeLists at: %s" %  self.cmakelistsurl)
            raise
        return data

    def getProjectCMT(self):
        self.projectcmturl = self.getURL("cmt/project.cmt")
        self.log.debug("Getting: %s" % self.projectcmturl)
        try:
            response = urllib2.urlopen(self.projectcmturl)
            data = response.read()
            self.log.debug("Got: %s" % self.projectcmturl)
        except:
            self.log.warning("Could not find Project.cmt at: %s" %  self.projectcmturl)
            raise            
        return data


    def getProjectConfig(self):
        """ URL folows pattern:
        https://gitlab.cern.ch/lhcb-dirac/LHCbDIRAC/raw/v8r6p3/dist-tools/projectConfig.json
        """
        self.projconfigurl = self.getURL("dist-tools/projectConfig.json")
        self.log.debug("Getting: %s" % self.projconfigurl)
        try:
            response = urllib2.urlopen(self.projconfigurl)
            data = response.read()
            self.log.debug("Got: %s" % self.projconfigurl)
        except:
            self.log.warning("Could not find projectConfig.json at: %s" %  self.projconfigurl)
            raise
        return data

    def getDepsFromProjectConfig(self, data):
        pc = json.loads(data)
        used_projects = pc["used_projects"]
        deps = []
        for l in used_projects["project"]:
            deps.append((l[0], l[1]))
        return deps

    def getDepsFromProjectCMT(self, data):
        deps = []
        for l in data.splitlines():
            m = re.match("\s*use\s+(\w+)\s+([\w\*]+)", l)
            if m != None:
                dp = m.group(1)
                dv = m.group(2)
                # removing the project name from the version if there
                dv = dv.replace(dp + "_", "")
                deps.append((dp, dv))
        return deps

    def getDependencies(self):
        """ Returns the list of project dependencies """
        pupper = self.project.upper()
        if pupper in [ "GAUDI", "GEANT4"]:
            # For GAUDI we take the dependency in the toolchain file
            try:
                data = self.getToolchain()
                htv = getHeptoolsVersion(data)
                deplist = [ ("LCG", htv) ]
                return deplist
            except:
                # In this case Gaudi is probably still using CMT
                self.log.warning("Looking for legacy CMT project.cmt")
                data = self.getProjectCMT()
                deplist = self.getDepsFromProjectCMT(data)
                return deplist
                
        if pupper in [ "DIRAC", "LHCBGRID" ]:
            return []
        else:
            # For all other projects use the gaudi_project macro
            # First we try to find teh CMakeLists
            # Second we try the projectConfig.json
            # Third we try the project.cmt for legacy projects
            try:
                self.log.warning("Looking for CMakeLists.txt")
                data = self.getCMakeLists()
                deplist = getGaudiUse(data)
                return deplist
            except:
                try:
                    self.log.warning("Looking for projectConfig.json")
                    data = self.getProjectConfig()
                    deplist = self.getDepsFromProjectConfig(data)
                    return deplist
                except:
                    try:
                        self.log.warning("Looking for legacy CMT project.cmt")
                        data = self.getProjectCMT()
                        deplist = self.getDepsFromProjectCMT(data)
                        return deplist
                    except:
                        self.log.error("Could not find project dependency metadata")
                        raise Exception("Could not find project metadata")
        return []


class AppImporter:
    """ Tool to add new project/version to the Software configuration
    DB from the version control systems """

    def __init__(self, autorelease = True, platforms = None):
        # Creating the SoftConfDB Object
        self.mConfDB = SoftConfDB()
        self.log = logging.getLogger()
        self.installArea = None
        self.mAutorelease = autorelease
        self.mPlatforms  = platforms
        if self.mPlatforms is not None:
            known_platforms =  set(self.mConfDB.listAllPlatforms())
            unknown = set(self.mPlatforms) - known_platforms
            if len(unknown) > 0:
                raise Exception("Unknown platforms: %s" % ", ".join(list(unknown)))


    def _setRequestedPlatforms(self, project, version):
        if self.mPlatforms:
            for p in self.mPlatforms:
                self.mConfDB.addPVPlatform(project, version, p, "REQUESTED_PLATFORM")

    def inGitlab(self, project, alturi=None):
        """ Check whether the project is handled in GIT or SVN """
        if not project:
            raise Exception("inGitlab method called with None project")

        if project.upper() in ["LCG", "LCGCMT"]:
            return False

        sourceuri = None
        if alturi == None:
            props = self.mConfDB.getProjectProperties(project.upper())
            if props != None and "sourceuri" in props.keys():
                sourceuri = props["sourceuri"]
        else:
            sourceuri = alturi

        from urlparse import urlsplit
        if sourceuri != None:
            if urlsplit(sourceuri).scheme == "svn":
                return False

        return True

    def gitlabProcessProjectVersion(self, p, v, alreadyDone = [], recreate=False,
                                    alturi=None, saveURIinPV=False):
        """ Get the dependencies for a single project """
        # Cleanup the project name and version
        (proj,ver)=(fixProjectCase(p),v)

        # Getting the project properties and locating the CMakeLists
        props = self.mConfDB.getProjectProperties(proj.upper())
        gp = GitlabProject(proj, ver, alturi)
        deps =  gp.getDependencies()

        # Formatting the project name/version
        corver = ver
        if proj in ver:
            corver = ver.replace(proj + "_", "")
        proj = proj.upper()

        # Looking for the project version in the DB
        tmp = self.mConfDB.findVersion(proj, ver)
        createNode = False
        node_parent = None

        # First checking if the node is there with the correct revision
        if len(tmp) != 0:
            node = tmp[0][0]
            node_parent = node
            # Need to add commit to the DB
        #If the node does not exist just create it...
        else:
            createNode = True

        if createNode:
            self.log.warning("Creating project %s %s" % (proj, ver))
            node_parent = self.mConfDB.getOrCreatePV(proj, corver)
            if saveURIinPV:
                self.log.warning("Setting sourceuri=%s for %s %s" % (gp.sourceuri, proj, ver))
                self.mConfDB.setPVProperty(proj, corver, "sourceuri", gp.sourceuri)
            # If releasing is needed!
            if self.mAutorelease and proj.upper() not in [ "LCG", "LCGCMT"]:
                self.log.warning("Requesting release of %s %s" % (proj, corver))
                self.mConfDB.setReleaseFlag(proj, corver)
                self._setRequestedPlatforms(proj, corver)

        if len(deps) == 0:
            self.log.warning("No dependencies found for %s %s" % (p, v))
            return node_parent

        # Now creating the dependencies
        for (dp, dv) in deps:
            if dp in dv:
                dv = dv.replace(dp + "_", "")
            dp = dp.upper()
            self.log.warning("Find project %s %s" % (dp, dv))
            node_child = self.processProjectVersion(dp, dv, alreadyDone, recreate)

            # Now checking if the links exist
            if self.mConfDB.nodesHaveRelationship(node_parent, node_child, "REQUIRES"):
                self.log.warning("Pre-existing dependency (%s, %s)-[:REQUIRES]->(%s, %s)" % (proj, ver, dp, dv))
            else:
                self.log.warning("Adding dependency (%s, %s)-[:REQUIRES]->(%s, %s)" % (proj, ver, dp, dv))
                self.mConfDB.addRequires(node_parent, node_child)

        return node_parent


    ##
    # Main entry point for the importer
    #
    def processProjectVersion(self, p, v, alreadyDone = [], recreate=False, sourceuri=None):
        """ Get the dependencies for a single project """
        # Cleanup the project name and version and get the SVN URL
        (proj,ver)=importerTranslateProject(p,v)
        tagpath = ""

        # If not forced check in the DB what the source URI should be
        forcedSourceURI = False
        if sourceuri == None:
            sourceuri = self.mConfDB.getSourceURI(p, v)
        else:
            forcedSourceURI = True
            # Only in this case do we need to save it in the project/version node

        self.log.warning("%s/%s - Using import URI: %s" % (p, v, sourceuri))
        
        # Now checking whether we should get the info from SVN of GIT
        gitlab = self.inGitlab(proj, alturi=sourceuri)
        if gitlab:
            # In this case use the new code
            # This should be cleanup up but in the transition period
            # we'll use this hack
            self.log.warning("Project %s is in Gitlab URI:%s" % (proj, sourceuri))
            return self.gitlabProcessProjectVersion(p, v, alturi=sourceuri, saveURIinPV=forcedSourceURI)


        # Only LCG/LCGCMT should not be in gitlab
        if proj not in [ "LCG", "LCGCMT"]:
            raise Exception("Error: project %s should be in gitlab" % proj)

        # Set deps to empty for LCG
        deps = []

        # Formatting the project name/version
        corver = ver
        if proj in ver:
            corver = ver.replace(proj + "_", "")
        proj = proj.upper()

        # Looking for the project version in the DB
        tmp = self.mConfDB.findVersion(proj, ver)
    
        createNode = False
        node_parent = None

        # First checking if the node is there with the correct revision
        if len(tmp) != 0:
            node = tmp[0][0]
            node_parent = node
        #If the node does not exist just create it...
        else:
            createNode = True

        # Rename LCGCMT to LCG
        if createNode and proj == "LCGCMT":
            proj = "LCG"

        # For LCG we check we don't have a LCGCMT node already...
        if createNode and proj == "LCG":
            tmplcgcmt = self.mConfDB.findVersion("LCGCMT", corver)
            if len(tmplcgcmt) > 0:
                self.log.warning("Found LCGCMT version %s instead of LCG" % corver)
                node_parent = tmplcgcmt[0][0]
            else:
                self.log.warning("Creating project %s %s" % (proj, corver))
                node_parent = self.mConfDB.getOrCreatePV(proj, corver)


        return node_parent

