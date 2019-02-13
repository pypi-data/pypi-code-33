#!/usr/bin/python3
# coding: utf-8

import os
import tempfile
import safeprint
from .file_filter import FileFilter


class Tree:
    class Node:
        def __init__(self):
            self.comments = []
            self.level = 0
            self.abs_path = ""
            self.is_dir = False
            self.is_end = False

        def get_basename(self) -> str:
            return os.path.basename(self.abs_path)

        def basename_len(self) -> int:
            return len(self.get_basename())

    def __init__(self, path: str = ""):
        self._root_path = os.path.abspath(path)
        self.comment_match_key = "// comment: "
        self._tmp_file = os.path.join(tempfile.gettempdir(),
                                      ".github_dir_tree_tmp")
        self.start_line = "# 目录结构"
        self.end_line = "---"
        self.max_line_len = 120
        self.dir_desc = ".dir_description"
        self.level = 0
        self._file_filter = None

    @property
    def root_path(self):
        return self._root_path

    @root_path.setter
    def root_path(self, path: str):
        if len(path):
            self._root_path = os.path.abspath(path)
        else:
            self._root_path = ""

    @property
    def file_filter(self):
        if self._file_filter is None:
            self.file_filter = []
        return self._file_filter

    @file_filter.setter
    def file_filter(self, filters: list):
        if self._file_filter is None:
            self._file_filter = FileFilter(self._root_path, filters)
            if os.path.isfile(os.path.join(self._root_path, ".gitignore")):
                self._file_filter.load_git_ignore_file(
                    os.path.join(self._root_path, ".gitignore"))

    def list_dir(self, dir_path, level=0) -> []:
        dirs = []
        files = []
        file_list = os.listdir(dir_path)
        if len(file_list) == 0:
            return []

        file_list = [
            file for file in file_list if not self.file_filter.is_match(
                os.path.abspath(os.path.join(dir_path, file)))

        ]
        only_dir = True
        final_file = ""
        for f in file_list:
            tmp = os.path.join(dir_path, f)
            if os.path.isfile(tmp):
                only_dir = False

            if only_dir:
                final_file = tmp
            else:
                if os.path.isfile(tmp):
                    final_file = tmp
        for f in file_list:
            abs_path = os.path.abspath(os.path.join(dir_path, f))

            if os.path.isdir(os.path.join(dir_path, f)):
                node = self.Node()
                node.level = level
                node.abs_path = abs_path
                node.is_dir = True
                dirs.append(node)

                dir_desc_file = os.path.join(
                    os.path.join(dir_path, f), self.dir_desc)
                if os.path.exists(dir_desc_file) and os.path.isfile(
                        dir_desc_file):
                    with open(
                            dir_desc_file.encode("utf-8"),
                            encoding="utf8",
                            errors="ignore") as f_content:
                        for line in f_content:
                            line = line[0:-1] if line[-1] == '\n' else line
                            node.comments.append(line)
                if only_dir and final_file == node.abs_path:
                    node.is_end = True
                dirs += self.list_dir(os.path.join(dir_path, f), level + 1)
            else:

                node = self.Node()
                node.level = level
                node.abs_path = abs_path
                with open(
                        abs_path.encode("utf-8"), encoding="utf8",
                        errors="ignore") as f_content:
                    for num, line in enumerate(f_content, 1):
                        if self.comment_match_key in line:
                            if line[-1] == '\n':
                                line = line[:-1]
                            node.comments.append(
                                line[len(self.comment_match_key):])
                if not only_dir and final_file == node.abs_path:
                    node.is_end = True
                files.append(node)
        return dirs + files

    def print_tree(self):
        fs = open(self._tmp_file, "w+", encoding="utf-8")
        files_list = self.list_dir(self._root_path)
        need_line = []
        for file_node in files_list:
            if int(self.level) != 0 and file_node.level > int(self.level):
                continue
            if not file_node.is_end:
                if file_node.level not in need_line:
                    need_line.append(file_node.level)
            else:
                if file_node.level in need_line:
                    need_line.remove(file_node.level)
            for i in range(0, file_node.level):
                if i in need_line:
                    print(" ", end="", file=fs)
                print('   ', end="", file=fs)
            if file_node.is_end:
                print("* " + self.get_md_file_link(file_node), end="", file=fs)
            else:
                print("* " + self.get_md_file_link(file_node), end="", file=fs)

            max_line_words = 100 - len(need_line) * 5 - file_node.basename_len(
            )
            first_line = True
            if len(file_node.comments):
                comments = file_node.comments.copy()
                while len(comments):
                    if len(comments[0]) > max_line_words:
                        line_content = comments[0][0:max_line_words]
                        comments[0] = comments[0][max_line_words:]
                    else:
                        line_content = comments[0]
                        del comments[0]
                    if first_line:
                        print(
                            "&nbsp;:&nbsp;" + line_content + "<br/>", file=fs)
                        first_line = False
                    else:
                        if file_node.is_end:
                            for i in range(0, file_node.level + 1):
                                if i in need_line:
                                    print(" ", end="", file=fs)
                                print('   ', end="", file=fs)
                            for i in range(0, file_node.basename_len() + 1):
                                print('&nbsp;', end="", file=fs)
                            print("&nbsp;&nbsp;", end="", file=fs)
                            print(line_content)
                        else:
                            for i in range(0, file_node.level + 1):
                                if i in need_line:
                                    print(" ", end="", file=fs)
                                if i != file_node.level:
                                    print('   ', end="", file=fs)
                            for i in range(0, file_node.basename_len() + 3):
                                print("&nbsp;", end="", file=fs)
                            print("&nbsp;&nbsp;", end="", file=fs)
                            print(line_content + "<br/>", file=fs)
            else:
                print("", file=fs)

        fs.close()

        target_update_file = os.path.join(self._root_path, "README.md")
        if not os.path.exists(target_update_file) \
                or os.path.isdir(target_update_file):
            open('README.md', 'a', encoding="utf-8").close()

        with open(self._tmp_file, 'r', encoding="utf-8") as f:
            source_file = f.read()

        with open(target_update_file, 'r', encoding="utf-8") as f:
            target_file = f.read()

        try:
            target_start = target_file.index(self.start_line)
            target_end = target_file.index(self.end_line, target_start)
            target_end += len(self.end_line)
        except Exception as e:
            target_end = target_start = 0

        source_file = "{}\n\n{}\n{}".format(self.start_line, source_file,
                                            self.end_line)

        if target_end == 0 and target_start == 0:
            target_file += '\n' + source_file
        else:
            target_file = target_file.replace(
                target_file[target_start:target_end], source_file)

        safeprint.print(target_file)

        with open(target_update_file, 'w', encoding="utf-8") as f:
            f.write(target_file)

    def get_md_file_link(self, node: Node):
        return "[{}]({})".format(
            os.path.basename(node.abs_path),
            os.path.relpath(node.abs_path, self._root_path).replace("\\", "/"))
