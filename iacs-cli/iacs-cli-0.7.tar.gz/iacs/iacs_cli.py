import os
from git import Repo
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import shutil
import click

from .default_config import CONFIG


@click.command()
@click.argument('course_name', type=str)
def create(course_name):
    # Today's Date
    now = date.now()

    # Create Root Directory
    if not os.path.exists(course_name):
        os.makedirs(course_name)
    course_dir = os.path.abspath(course_name)
    readings_md = os.path.join(course_dir, 'README.md')
    with open(readings_md, "w") as file:
        file.write("# " + course_name + " Repository")


    # Create Sub-directories
    content_dir = os.path.join(course_dir, 'content')
    docs_dir = os.path.join(course_dir, 'docs')
    os.makedirs(docs_dir)
    os.makedirs(content_dir)
    readings_md = os.path.join(docs_dir, 'README.md')
    with open(readings_md, "w") as file:
        file.write("# Course Website")

    # Create Subdirectories
    lectures_dir = os.path.join(content_dir, 'lectures')
    labs_dir = os.path.join(content_dir, 'labs')
    homeworks_dir = os.path.join(content_dir, 'homeworks')
    pages_dir = os.path.join(content_dir, 'pages')
    os.makedirs(lectures_dir)
    os.makedirs(labs_dir)
    os.makedirs(homeworks_dir)
    os.makedirs(pages_dir)

    # Create sample folder for lecture 0
    lecture0_dir = os.path.join(lectures_dir, 'lecture0')
    os.makedirs(lecture0_dir)
    presentation_dir = os.path.join(lecture0_dir, 'presentation')
    os.makedirs(presentation_dir)
    readings_md = os.path.join(presentation_dir, 'README.md')
    Path(readings_md).touch()
    data_dir = os.path.join(lecture0_dir, 'data')
    os.makedirs(data_dir)
    readings_md = os.path.join(data_dir, 'README.md')
    Path(readings_md).touch()
    fig_dir = os.path.join(lecture0_dir, 'fig')
    os.makedirs(fig_dir)
    readings_md = os.path.join(fig_dir, 'README.md')
    Path(readings_md).touch()
    notes_dir = os.path.join(lecture0_dir, 'notes')
    os.makedirs(notes_dir)
    readings_md = os.path.join(notes_dir, 'README.md')
    Path(readings_md).touch()
    readings_md = os.path.join(lecture0_dir, 'readings.md')
    with open(readings_md, 'w') as file:
        file.write("Title: Lecture 0\n")
        file.write("Date: " + now.strftime('%Y-%m-%d') + "\n")
        file.write("Slug: lecture0\n")
        file.write("Author: \n")
        file.write("\n\n")
        file.write("# Lecture 0\n")



    # Write Pelican configuration file
    config_file = os.path.join(course_dir, 'config.py')
    with open(config_file, 'w') as file:
        for config_pair in CONFIG:
            if len(config_pair) < 2:
                config = config_pair[0]
                config += '\n'
            else:
                key, value = config_pair
                if key == 'SITE_NAME':
                    value = course_name

                if type(value) == str:
                    config = "{} = '{}'"
                else:
                    config = "{} = {}"
                config = config.format(key, value)
                config += "\n\n"
            file.write(config)

    # # TODO: write index.md
    index_file = os.path.join(content_dir, 'index.md')
    with open(index_file, 'w') as file:
        file.write("Title: Home\n")
        file.write("Date: " + now.strftime('%Y-%m-%d') + "\n")
        file.write("save_as: index.html\n")

    # # TODO: write Homework0.ipynb
    # # TODO: write Lecture0.ipynb
    # # TODO: write Lab0.ipynb

    # write .gitignore
    gitignore_file = os.path.join(course_dir, '.gitignore')
    with open(gitignore_file, 'w') as file:
        file.write(" *.pyx\n /dist/\n /*.egg-info\n .DS_Store\n")

    # initialize git
    repo = Repo.init(course_dir)
    repo.index.add(os.listdir(course_dir))
    repo.index.commit("first commit -- " + now.strftime('%Y-%m-%d %X'))



@click.command()
def publish():
    os.system("pelican content -s config.py -t themes/hiacs")



@click.command()
@click.option('--port', default='8000')
def launch(port):
    os.chdir('docs')
    port = int(port)

    with HTTPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        click.echo("Serving at localhost:{}, to quit press <ctrl-c>".format(port))
        httpd.serve_forever()


@click.command()
def upload():

    # Check if github repo address is set in the config.py
    # TODO
    origin_url = 'https://github.com/richardskim111/2200-AM207.git'
        # if not, raise Exception - "Please specify github repository for the course"


    # Check if git remote url exists
    repo = Repo.init(os.getcwd())
    if repo.remotes['origin']:
        # Check if they match?
        origin = repo.remotes['origin']
    else:
        # if not, set to github repo setting in config
        origin = repo.create_remote('origin', origin_url)

    repo.create_head('master', origin.refs.master)
    repo.heads.master.set_tracking_branch(origin.refs.master)

    origin.pull()
    origin.push()





@click.command('copy', short_help="copy existing course project")
@click.argument('original', type=click.Path(exists=True), metavar='<original>', nargs=1)
@click.argument('course_name', type=click.Path(), metavar='<course_name>', nargs=1)
def copy(original, course_name):
    # Today's Date
    now = date.now()

    course_dir = os.path.abspath('./' + course_name)
    if not os.path.exists(course_dir):
        shutil.copytree(original, course_dir)

    # Remove existing git
    git = os.path.join(course_dir, '.git')
    if os.path.exists(git):
        shutil.rmtree(git)

    # initialize git
    repo = Repo.init(course_dir)
    repo.index.add(os.listdir(course_dir))
    repo.index.commit("first commit -- " + now.strftime('%Y-%m-%d %X'))

    # Open config.py and change - SITE_NAME, AUTHOR, SITEURL, GITHUB, NAVBAR_LINKS
    # TODO







@click.group()
def main():
    pass

main.add_command(create)
main.add_command(publish)
main.add_command(launch)
main.add_command(upload)
main.add_command(copy)


if __name__ == '__main__':
    main()
