try:
    import dnf
    MODULE = "dnf"
except ImportError:
    import yum
    MODULE = "yum"


class RpmBackend:
    def __init__(self):
        self.installed_packages = []
        self.enabled_repos = []
        self.releasever = None
        self.basearch = None
        if MODULE == "dnf":
            self.get_from_dnf()
        elif MODULE == "yum":
            self.get_from_yum()

    def get_from_dnf(self):
        base = dnf.dnf.Base()
        base.fill_sack(load_system_repo=True, load_available_repos=False)
        self.installed_packages = ["%s-%s:%s-%s.%s" % (pkg.name, pkg.epoch, pkg.version, pkg.release, pkg.arch)
                                   for pkg in base.sack.query().installed()]
        base.read_all_repos()
        self.enabled_repos = [repo for repo in base.repos if base.repos[repo].enabled]
        self.releasever = base.conf.substitutions["releasever"]
        self.basearch = base.conf.substitutions["basearch"]


    def get_from_yum(self):
        base = yum.YumBase()
        base.doConfigSetup(init_plugins=False)
        self.installed_packages = ["%s-%s:%s-%s.%s" % (pkg.name, pkg.epoch, pkg.version, pkg.release, pkg.arch)
                                   for pkg in base.rpmdb.returnPackages()]
        self.enabled_repos = [repo.id for repo in base.repos.listEnabled()]
        self.releasever = base.conf.yumvar["releasever"]
        self.basearch = base.conf.yumvar["basearch"]
