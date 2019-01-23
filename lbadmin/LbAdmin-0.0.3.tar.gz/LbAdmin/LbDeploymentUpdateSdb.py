#!/usr/bin/env python
#
# Helper script to update the content of the Software Database during the
# deployment of a project.
#


import os, sys, re
from LbCommon.Script import Script


# @class Check Released configs
# Main script class for to release RPMs to the repository.
class CheckReleasedConfig(Script):

    def __init__(self):
        Script.__init__(self, usage="\n\t%prog [options] releasedir",
                        description="Script update the SDB with the platforms effectively built")

    def defineOpts(self):
        """ User options """
        self.parser.add_option("-i", "--interactive", action="store_true", default=False,
                               help="Prompt before adding the platform")
        self.parser.add_option("--platform-regex", action="store", default=None,
                               help="Regexp for the platform to update")
        self.parser.add_option("--name-regex", action="store", default=None,
                               help="Regexp for the projects to update")
        self.parser.add_option("-u", "--update", action="store_true", default=False,
                               help="Really update the platforms, in dry-run mode otherwise")

    def getBuildConfig(self, builddir):
        """ Get the list of platforms built from slot-config.json """
        configfile = os.path.join(builddir, "slot-config.json")
        if not os.path.exists(configfile):
            raise Exception("%s does not exist!. Cannot load list of platforms" % configfile)

        self.log.info("Logging configurations from %s" % configfile)
        import json
        config = None
        with open(configfile) as f:
            data = json.load(f)
            config = data
        return config

    def updateSdb(self, builddir, updatemode, platformre, namere):
        """ Update the platform in the SDB """

        # Cheking that our files are there...
        builddir = os.path.abspath(builddir)
        self.log.warning("Build dir: %s" % builddir)

        if not os.path.exists(builddir):
            raise Exception("The build directory %s does not exist" % builddir)

        # Loading the build config
        config = self.getBuildConfig(builddir)

        # Now looking for binary projects...
        projname = lambda p: (p["name"].upper(), p["version"])
        projlist = []
        indepprojlist = []
        for p in config.get("projects", []):
            if p.get("platform_independent", False) and p["platform_independent"]:
                self.log.info("%s %s is platform independent" % projname(p))
                indepprojlist.append(projname(p))
            else:
                projlist.append(projname(p))

        # And finding the platforms and therefore listing the RPMs we should find...
        sanitize = lambda s: s.replace("-", "_")
        platforms = config["platforms"]

        # Dealing with binary dependent projects
        for p, v in projlist:

            if namere and not re.match(namere, p):
                self.log.warning("Ignoring %s %s due to regex" % (p, v))
                continue

            platform_found = []
            platform_missing = []
            for platform in platforms:
                prefix = "_".join([p, v, sanitize(platform)])
                # foundrpm = [ r for r in os.listdir(builddir) if r.startswith(prefix) ]
                foundrpm = [f for _, _, files in os.walk(builddir) for f in files if f.startswith(prefix)]
                if len(foundrpm) == 0:
                    platform_missing.append(platform)
                elif len(foundrpm) >= 1:
                    platform_found.append(platform)

            if len(platform_found) > 0:
                self.log.warning("%s %s: found   builds for %s" % (p, v, ", ".join(platform_found)))
            else:
                self.log.error("No platform builds found")

            if len(platform_missing) > 0:
                self.log.error("%s %s: missing builds for %s" % (p, v, ", ".join(platform_missing)))
            else:
                self.log.info("No platforms missing")

            # Now updating the sdb, calling the scripts not the python module to make sure we have the credentials
            if updatemode:
                import subprocess
                for c in platform_found:
                    if platformre and not re.match(platformre, c):
                        self.log.warning("Ignoring platform %s due to regex" % c)
                        continue
                    self.log.warning("Adding platform to DB: %s %s %s" % (p, v, c))
                    subprocess.check_call(["lb-sdb-add-platform", p, v, c])

                self.log.warning("Marking %s %s as released" % (p, v))
                subprocess.check_call(["lb-sdb-release", "-r", p, v])
            else:
                for c in platform_found:
                    if platformre and not re.match(platformre, c):
                        self.log.warning("Ignoring platform %s due to regex" % c)
                        continue
                    self.log.warning("Will add to SDB: %s %s %s" % (p, v, c))
                self.log.warning("Will release %s %s" % (p, v))

        # Releasing platform independent projects
        for p, v in indepprojlist:

            if namere and not re.match(namere, p):
                self.log.warning("Ignoring %s %s due to regex" % (p, v))
                continue

            if updatemode:
                import subprocess
                self.log.warning("Marking %s %s as released" % (p, v))
                subprocess.check_call(["lb-sdb-release", "-r", p, v])
            else:
                self.log.warning("Will release %s %s" % (p, v))

    def main(self):
        """ Main method for the script """
        if len(self.args) != 1:
            self.parser.error('Please specify the directory with the release')

        if not self.options.update:
            self.log.warning("In dry-run mode. use --update to update the SDB")
        else:
            self.log.warning("Updating the SDB")

        # Now performing the update
        rc = 0
        try:
            updated = self.updateSdb(self.args[0],
                                     self.options.update,
                                     self.options.platform_regex,
                                     self.options.name_regex)
        except Exception, e:
            self.log.error(e)
            rc = 1
        return rc


def main():
    s = CheckReleasedConfig()
    sys.exit(s.run())


if __name__ == '__main__':
    main()
