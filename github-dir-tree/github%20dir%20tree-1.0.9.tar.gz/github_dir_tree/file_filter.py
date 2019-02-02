import pathspec
import os


class FileFilter:
    # filters = []
    _filter_files = None
    _project_root = None

    def __init__(self, project_root, git_wild_match=None):
        self._project_root = project_root
        if git_wild_match:
            if isinstance(git_wild_match, str):
                git_wild_match = git_wild_match.splitlines()
            if not isinstance(git_wild_match, list):
                raise "the git_wild_match arguments must be string or list"
            self.git_wild_match = git_wild_match
        else:
            self.git_wild_match = []

    def load_git_ignore_file(self, path):
        with open(path, 'r', encoding='utf8') as f:
            lines = f.read().splitlines()
        self.git_wild_match = self.git_wild_match + lines

    def get_filter_files(self) -> list:
        if self._project_root is None:
            raise "you must use set_project_root_dir() to set project path"
        if self._filter_files is None:
            print(self.git_wild_match)
            spec = pathspec.PathSpec.from_lines('gitwildmatch',
                                                self.git_wild_match)
            matches = spec.match_tree(self._project_root)
            self._filter_files = []
            for file in matches:
                self._filter_files.append(
                    os.path.join(self._project_root, file))
        return self._filter_files

    def is_match(self, abs_path):
        if not self.is_in_project(abs_path):
            return False
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, self.git_wild_match)
        rel_path = os.path.relpath(abs_path, self._project_root)
        return spec.match_file(rel_path)

    def is_in_project(self, abs_path):
        return os.path.commonprefix([abs_path,
                                     self._project_root]) == self._project_root

# filter = FileFilter([])
# filter.set_project_root_dir(r'C:\Users\jefun\Desktop\py_repos\github_dir_tree')
# filter.load_git_ignore_file(r'C:\Users\jefun\Desktop\py_repos\github_dir_tree\.gitignore')
# print(len(filter.filter_files()))
# spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, [".git", "tests"])
# print(spec.match_file('.git\\logs23'))
# print(spec.match_file('C:\\Users\\jefun\\Desktop\\py_repos\\github_dir_tree\\tests\\dir_tree'))
