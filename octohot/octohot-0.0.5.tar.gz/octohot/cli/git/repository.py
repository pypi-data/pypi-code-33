import os
from octohot.sh import sh


def path(exists=True, raise_error=True):
    """
        Decorator: Execution depends if folder exists or not
    :param exists: Boolean. Check if exists or not.
    :param raise_error: Boolean. Check if there will be an error if exists check
    :return:
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            self = args[0]
            if os.path.isdir(self.folder) == exists:
                return fn(*args, **kwargs)
            else:
                if raise_error:
                    if exists:
                        FileNotFoundError(self.folder)
                    else:
                        FileExistsError(self.folder)
        return wrapper
    return decorator


class Repository():

    def __init__(self, url):
        self.url = url
        self.name = url.split('/')[-1].replace('.git', '')
        self.folder = '%s/%s' % (os.getcwd(), self.name)

        self.owner = self.url.split('/')[-2]
        if ':' in self.owner:
            self.owner = self.owner.split(':')[-1]

    def pprint(self, msg):
        cmd = '\n>>>>>> %s: %s\n' % (self.name, msg)
        return cmd

    def clone(self):
        cmd = 'git clone --single-branch %s %s'
        return sh(cmd % (self.url, self.folder))

    def pull(self):
        cmd = 'git -C %s pull'  # TODO: --merge
        return sh(cmd % self.folder)

    def reset(self):
        """
            Reseta a branch atual, baseada na respectiva branch remota.
        """
        # 'git -C %s clean -fd ' % self.folder
        # 'git -C %s checkout -- .' % self.folder
        cmd = 'git -C %s reset --hard origin/$(git -C %s rev-parse ' \
              '--abbrev-ref HEAD)'
        return sh(cmd % (self.folder, self.folder))

    def diff(self):
        cmd = 'git -C %s --no-pager diff'
        return sh(cmd % self.folder)

    def branch(self, branch_name):
        cmd = 'git -C %s checkout %s 2>/dev/null || ' \
              'git -C %s checkout master; git -C %s checkout -b %s'
        cmd = cmd % (self.folder, branch_name, self.folder, self.folder,
                     branch_name)
        sh(cmd)

    def add(self):
        sh('git -C %s add .' % self.folder)

    def commit(self, commit_name, commit_description):
        commit_name = commit_name.replace('"', '\\"')
        commit_description = commit_description.replace('"', '\\"')
        sh('git -C %s commit -m "%s" -m "%s"'
           % (self.folder, commit_name, commit_description))

    def push(self, branch_name):
        sh('git -C %s push origin %s' % (self.folder, branch_name))

    def default_branch(self):
        cmd = """git -C %s symbolic-ref refs/remotes/origin/HEAD | \
            sed 's@^refs/remotes/origin/@@'"""
        return sh(cmd % self.folder)[0]

    def all_branches(self):
        cmd = """git -C %s branch | cut -c 3-"""
        return sh(cmd % self.folder)

    def delete_branch(self, branch_name):
        cmd = """git -C %s branch -D %s"""
        return sh(cmd % (self.folder, branch_name))

    def delete_unpushed_branches(self):
        branches_to_remove = [branch for branch in self.all_branches()
                              if not branch == self.default_branch()]
        return [self.delete_branch(branch) for branch in branches_to_remove]

    def tainted(self):
        """
        Lista arquivos que foram incluídos, modificados ou preparados (staged)
        :return:
        """
        files = sh(
            'git -C %s status -uall -s' % self.folder
        )
        return bool(len(files))

    def is_current_branch(self, branch):
        current_branch = sh(
            """git -C %s branch | grep \\* | cut -d' ' -f2""" % self.folder
        )[0]
        return current_branch == branch

    def is_github(self):
        return 'github.com' in self.url

    def branch_has_diff_from_master(self, branch_name):
        diff = sh("git -C %s --no-pager diff master..%s" % (self.folder, branch_name))

        # branch not exists
        if 'unknown revision or path' in '\n'.join(diff):
            return False

        return bool(len(diff))

    def files(self, pattern=".*"):
        cmd = "find %s -type f -not -path '*/.git/*' -exec grep -Iq . {} \\; -and -print"
        files = sh(cmd % self.folder)

        import re
        regex = re.compile(pattern)
        files = [file for file in files if regex.match(file)]

        return files

