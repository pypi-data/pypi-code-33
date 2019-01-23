"""
This is a git commit-hook which can be used to check if huge files
 where accidentally added to the staging area and are about to be
 committed.
If there is a file which is bigger then the given "max_file_size"-
 variable, the script will exit non-zero and abort the commit.
This script is meant to be added as a "pre-commit"-hook. See this
 page for further information:
    http://progit.org/book/ch7-3.html#installing_a_hook
In order to make the script work probably, you'll need to set the
 above path to the python interpreter (first line of the file)
 according to your system (under *NIX do "which python" to find out).
Also, the "git_binary_path"-variable should contain the absolute
 path to your "git"-executable (you can use "which" here, too).
See the included README-file for further information.
The script was developed and has been confirmed to work under
 python 3.2.2 and git 1.7.7.1 (might also work with earlier versions!)
"""
import subprocess, sys, os
import collections, operator

# The maximum file-size for a file to be committed:
max_file_size = 50 * 1024  # in KiB (= 1024 byte), 50 MB
max_repo_size = 500 * 1024  # in KiB, 200 MB
units = 1024.0  # To move up and down between magnitudes of size


def check_for_large_files():
    # Now, do the checking:
    try:
        too_large_files = []
        files_committed = []
        num_files_to_show = 5
        # In Bytes
        total_size_of_commit = 0
        LargeFile = collections.namedtuple('LargeFile', ['filename', 'size_bytes'])
        # Check all files in the staging-area:
        text = subprocess.check_output(
            ['git', "status", "--porcelain", "-uno"],
            stderr=subprocess.STDOUT).decode("utf-8")
        file_list = text.splitlines()

        # Check all files:
        for file_s in file_list:
            file_git_status = file_s[:3]
            if "D" in file_git_status:
                continue
            # Renamed files need a bit more special handling
            if "R" in file_git_status:
                arrow_text = '->'
                arrow_end = file_s.find(arrow_text)
                if arrow_end > -1:
                    # Sample rename output from git
                    # 'R  file2.txt -> file3.txt'
                    position_adjustment = arrow_end + len(arrow_text) + 1
                    file_name = file_s[position_adjustment:]
            else:
                file_name = file_s[3:]
            # If filenames with spaces continues to be an issue, consider git status with -z argument.
            if file_name.startswith('"') and file_name.endswith('"'):
                file_name = file_name.strip('"')
            file_path = os.path.abspath(file_name)
            stat = os.stat(file_path)
            total_size_of_commit += stat.st_size
            files_committed.append(LargeFile(file_name, stat.st_size))
            if stat.st_size >= (max_file_size * units):
                # File is too big, store it for later analysis
                too_large_files.append(LargeFile(file_name, stat.st_size))

        # Are they trying to commit large files?
        if len(too_large_files) > 0:
            print("You have one more files that are larger than {file_max_size}.".format(file_max_size=sizeof_fmt(max_file_size * units)))
            print("Use Onepanel datasets to store datasets or any files larger than {file_max_size}.".format(file_max_size=sizeof_fmt(max_file_size * units)))
            print("Use \"git reset HEAD <file>\" to unstage large files and try your commit again.")
            print_top_x_large_files(num_files_to_show, too_large_files)
            sys.exit(1)

        # Everything seems to be okay with file sizes
        print_top_x_large_files(num_files_to_show, files_committed)
        sys.exit(0)

    except subprocess.CalledProcessError:
        # There was a problem calling "git status".
        print("Error executing git status")
        sys.exit(12)


def sizeof_fmt(num):
    """
	This function will return a human-readable filesize-string
	 like "3.5 MB" for it's given 'num'-parameter.
	From http://stackoverflow.com/questions/1094841
	"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < units:
            return "%3.1f %s" % (num, x)
        num /= units


def print_top_x_large_files(how_many=5, list_of_files=None):
    if list_of_files is None:
        list_of_files = []
    else:
        print("Top {how_many} largest files:".format(how_many=how_many))
    # Sort the list of files by size
    sorted_files = sorted(list_of_files, key=operator.attrgetter('size_bytes'), reverse=True)
    for index, file in enumerate(sorted_files):
        if index == how_many:
            break
        print(
            "{file_name} - ({size_of_file})".format(file_name=file.filename, size_of_file=sizeof_fmt(file.size_bytes)))


def check_repo_sizet(total_size_of_commit=0):
    # Check if the repository size is too big
    git_repo_info = subprocess.check_output(
        ['git', "count-objects", "-v"],
        stderr=subprocess.STDOUT).decode("utf-8")
    repo_info_output = git_repo_info.splitlines()
    for git_output in repo_info_output:
        if "size" in git_output:
            size_line = git_output
            kib_info = size_line.split(":")
            kib_val = int(kib_info[1].strip())
            if (kib_val * units + total_size_of_commit) >= max_repo_size * units:
                print("The total size of your repository is greater than {repo_max_size}.".format(
                    repo_max_size=sizeof_fmt(max_repo_size * units)))
                print("Use Onepanel datasets to store datasets or any files larger than {file_max_size}.".format(
                    file_max_size=sizeof_fmt(max_file_size * units)))
                print("Use \"git reset HEAD <file>\" to unstage large files and try your commit again.")
                sys.exit(1)