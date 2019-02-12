""" 
Main Generator methods 
"""
import os
import shutil
import datetime
from subprocess import call
import platform
try:   
    import urllib2 #python2
except:
    import urllib.request as urllib2 #python3
import ssl
import inflection
import click
from jinja2 import Environment, PackageLoader, select_autoescape


today = datetime.date.today()

env = Environment(
    loader=PackageLoader('espada', 'templates'),
    autoescape=select_autoescape(['cpp', 'h', 'txt'])
)


@click.group()
def cli():
    """Entry point for click"""
    #print(os.getcwd())
    pass

@cli.command('build')
def build():
    """Compile a C++ Project """
    if os.path.isfile("CMakeLists.txt"):
        dir_name = "build"
        # Create Build Directory
        if(os.path.isdir(dir_name)):
            shutil.rmtree(dir_name)
        os.mkdir(dir_name)
        os.chdir(dir_name)
        # run CMake for platform
        generator = "Unix Makefiles"
        if platform.system() == 'Windows': #'Linux' or 'Windows'/'Darwin'
            generator = "Visual Studio 15 2017"
        call(["cmake", "-G", generator, ".."] )
        # run Cmake --build .
        call(["cmake", "--build", "."] )
        os.chdir('..')

@cli.command('new')
@click.argument('project_name') # , help="Name of Project"
@click.option('--type', '-t', 'template', type=click.Choice(['app', 'lib', 'ws']), prompt="Select what you wish to create:[app, lib, ws]")
def project(project_name, template):
    """Generate a C++ Project"""
    print('Generating project')
    if(template == 'ws'):
        generate_project_folder(project_name)
    elif template == 'lib':
        generate_single_lib_project(project_name)
    else:
        generate_single_project(project_name)


@cli.command('class')
@click.option('--class', '-c', 'class_name', prompt='Name of the class',
              help="Name of Class to generate ")
@click.option('--test', is_flag=True, help="Generate test case for class")
def class_gen(class_name, test):
    """Generate C++ Class file with given name"""
    dir_name = os.path.basename(os.getcwd())
    if 'lib' in dir_name:
        proj_name = dir_name[3:]
    elif 'tests' in dir_name:
        proj_name = dir_name[5:]
    else:
        proj_name = dir_name
    print("Creating code for Project: {0}".format(proj_name))
    if os.path.isdir("include"):
        generate_class_header(class_name)
        generate_class_body(class_name)
        if(test):
            if os.path.isdir("../tests{0}".format(proj_name)):
                generate_class_test(class_name, proj_name)
    else:
        print "Please make sure you are in a project directory"


@cli.command('test')
@click.option('--class', '-c', 'class_name', prompt='Name of the class to test',
              help="Name of Class to generate a test case for")
def test_gen(class_name):
    """Generate Unit test based on given class name"""
    dir_name = os.path.basename(os.getcwd())
    if 'lib' in dir_name:
        proj_name = dir_name[3:]
    elif 'tests' in dir_name:
        proj_name = dir_name[5:]
    else:
        proj_name = dir_name
    
    if os.path.isdir("include"):
        generate_class_test(class_name, proj_name)
    else:
        print "Please make sure you are in a tests project directory"


@cli.command('header')
@click.option('--proj', '-p', 'project', type=click.STRING, prompt="Project to Create Header")
@click.option('--file', '-f', 'name', prompt='Name of the file', help="Name of header file to create")
def header_gen(project, name):
    """Generate a empty Header File"""
    if os.path.isdir(project):
        if os.path.isdir("{0}/include".format(project)):
            generate_empty_file(name, project, "h", "include")
        else:
            os.mkdir("{0}/include".format(project))
            generate_empty_file(name, project, "h", "include")
            print "Please remember to remove the # sign from the include_directories command at " \
                "the top of the CMakeLists file in the {0} directory".format(project)
    else:
        print "Please make sure you are in the main project directory"


@cli.command('source')
# @click.option('--proj', '-p', 'project', type=click.Choice(['lib', 'app']), prompt="Project to create source")
@click.option('--proj', '-p', 'project', type=click.STRING, prompt="Project to create source")
@click.option('--file', '-f', 'name', prompt='Name of the file', help="Name of source file to create")
def source_gen(project, name):
    """Generate a empty source File"""
    if os.path.isdir(project):
        generate_empty_file(name, project, "cpp", "src")
    else:
        print "Please make sure you are in the main project directory"



#############################################################################################################
# Private Helpers


def generate_single_project(name):
    proj_name = inflection.camelize(name)
    os.mkdir(proj_name)
    os.chdir(proj_name)
    args = {
        'project_name': proj_name,
        'exe_name': inflection.underscore(proj_name)
    }
    generate_file_from_template('single_app_cmake.txt', 'CMakeLists.txt', **args)
    os.mkdir('include')
    generate_file_from_template('gitkeep.txt', 'include/.gitkeep', **args)
    os.mkdir('src')
    generate_file_from_template('app_main.cpp', 'src/main.cpp', **args)
    os.chdir('..')

def fetch_file(url, file):
    #ssl._create_default_https_context = ssl._create_unverified_context
    # gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    response = urllib2.urlopen(url)
    # req = urllib2.Request(url)
    # gcontext = ssl.SSLContext(ssl.CERT_NONE)  # Only for gangstars
    # response = urllib2.urlopen(req, context=gcontext)
    #open the file for writing
    fh = open(file, "w")

    # read from request while writing to file
    fh.write(response.read())
    fh.close()
    print("Fetching file {0}".format(file))


def generate_single_lib_project(name):
    proj_name = inflection.camelize(name)
    dirName = "lib{0}".format(proj_name)
    os.mkdir(dirName)
    os.chdir(dirName)
    args = {
        'project_name': proj_name,
        'exe_name': inflection.underscore(proj_name)
    }
    generate_file_from_template('single_lib_cmake.txt', 'CMakeLists.txt', **args)
    os.mkdir('include')
    generate_file_from_template('gitkeep.txt', 'include/.gitkeep', **args)
    os.mkdir('src')
    generate_file_from_template('gitkeep.txt', 'src/.gitkeep', **args)
    os.chdir('..')


def generate_project_folder(name):
    proj_name = inflection.camelize(name)
    os.mkdir(proj_name)
    os.chdir(proj_name)
    args = {
        'project_name': proj_name,
        'exe_name': inflection.underscore(proj_name)
    }
    generate_file_from_template('project_cmake.txt', 'CMakeLists.txt', **args)
    generate_lib_project(**args)
    generate_test_project(**args)
    generate_main_project(**args)


def generate_lib_project(**kwargs):
    dirName = "lib{0}".format(kwargs['project_name'])
    print("Creating Library Project: {0}".format(dirName))
    os.mkdir(dirName)
    os.chdir(dirName)
    generate_file_from_template('lib_cmake.txt', 'CMakeLists.txt', **kwargs)
    os.mkdir('include')
    generate_file_from_template('gitkeep.txt', 'include/.gitkeep', **kwargs)
    os.mkdir('src')
    generate_file_from_template('gitkeep.txt', 'src/.gitkeep', **kwargs)
    os.chdir('..')


def generate_test_project(**kwargs):
    dirName = "tests{0}".format(kwargs['project_name'])
    print("Creating Test Project: {0}".format(dirName))
    os.mkdir(dirName)
    os.chdir(dirName)
    generate_file_from_template('tests_cmake.txt', 'CMakeLists.txt', **kwargs)
    os.mkdir('include')
    # testfile = urllib.URLopener()
    # testfile.retrieve("https://raw.githubusercontent.com/catchorg/Catch2/master/single_include/catch2/catch.hpp",
    #                   "include/catch.hpp")
    fetch_file("https://raw.githubusercontent.com/catchorg/Catch2/master/single_include/catch2/catch.hpp", "include/catch.hpp")
    # testfile.retrieve("https://raw.githubusercontent.com/eranpeer/FakeIt/master/single_header/catch/fakeit.hpp",
    #                   "include/fakeit.hpp")
    fetch_file("https://raw.githubusercontent.com/eranpeer/FakeIt/master/single_header/catch/fakeit.hpp", "include/fakeit.hpp")
    os.mkdir('src')
    generate_file_from_template('test_main.cpp', 'src/main.cpp', **kwargs)
    os.chdir('..')


def generate_main_project(**kwargs):
    dirName = "{0}".format(kwargs['project_name'])
    os.mkdir(dirName)
    os.chdir(dirName)
    print("Creating Application Project: {0}".format(dirName))
    generate_file_from_template('app_cmake.txt', 'CMakeLists.txt', **kwargs)
    os.mkdir('include')
    generate_file_from_template('gitkeep.txt', 'include/.gitkeep', **kwargs)
    os.mkdir('src')
    generate_file_from_template('app_main.cpp', 'src/main.cpp', **kwargs)
    os.chdir('..')


def generate_class_header(name):
    args = generate_args(name)
    generate_file_from_template('class_header.h', "include/{0}.h".format(args['f_name']), **args)


def generate_class_body(name):
    args = generate_args(name)
    generate_file_from_template('class_body.cpp', "src/{0}.cpp".format(args['f_name']), **args)


def generate_class_test(name, project_name):
    args = generate_args(name)
    generate_file_from_template('test_case.cpp', "../tests{1}/src/{0}_tests.cpp".format(args['f_name'], project_name), **args)


def generate_args(name, ext='cpp'):
    return {
        'class_name': inflection.camelize(name),
        'f_name': inflection.underscore(name),
        'user_name': os.environ.get('USER', ''),
        'ext': ext,
        'date_time': "{:%d, %b %Y }".format(today)
    }


def generate_empty_file(name, proj, ext, dest):
    args = generate_args(name, ext)
    generate_file_from_template('empty_src.cpp', "{0}/{1}/{2}.{3}".format(proj, dest, args['f_name'], ext), **args)


def generate_file_from_template(template_name, file_name, **kwargs):
    template = env.get_template(template_name)
    target = open(file_name, 'w')
    target.write(template.render(**kwargs))
    print "Generated {0}".format(file_name)



# Creating Espada file
# # Writing JSON data
# with open('data.json', 'w') as f:
#      json.dump(data, f)

# # Reading data back
# with open('data.json', 'r') as f:
#      data = json.load(f)