from __future__ import print_function
from future.builtins import dict
import yaml, sys, itertools, logging

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

def generate_inputs(template, input_category, input):
    result = []

    for key, values in input.items():
        result.append([(input_category, key, value) for value in values])

    return result

def input_matrix(template, inputs):
    result = []

    for input in inputs:
        if input in template:
            result += generate_inputs(template, input, template[input])

    result = list(itertools.product(*result))
    return result

def format_flag(packages, flag_tuple):
    category, name, value = flag_tuple

    if category == "settings":
        return " ".join("-s {}:{}={}".format(package, name, value) for package in packages)
    elif category == "options":
        return " ".join("-o {}:{}={}".format(package, name, value) for package in packages)


def format_flags(packages, flags_tuple):
    return ' '.join(format_flag(packages, e) for e in flags_tuple)

def pretty_format_flag(flag_tuple):
    _, name, value = flag_tuple
    return "{}={}".format(name, value)

def pretty_format_flags(flags_tuple):
    return '+'.join(pretty_format_flag(e) for e in flags_tuple)

def filter_package_args(package_args, expected_category):
    filtered = []
    others = []

    for arg in package_args:
        category, name, value = arg

        if category == expected_category:
            filtered.append((name, value))
        else:
            others.append(arg)

    return (filtered, tuple(others))

def job_tag(packages, compiler, version, package_args):
    return "{}_{}_{}_{}".format('+'.join(packages), version, compiler, pretty_format_flags(package_args))

def build_job_tag(packages, compiler, version, package_args):
    return "build_" + job_tag(packages, compiler, version, package_args)

def test_job_tag(packages, compiler, version, package_args):
    return "test_" + job_tag(packages, compiler, version, package_args)

def deploy_job_tag(packages, compiler, version, package_args):
    return "deploy_" + job_tag(packages, compiler, version, package_args)

def build_job_dependencies(packages, package):
    packages_names = list(packages.keys())
    return packages_names[:packages_names.index(package)]

def generate_gitlab_package(gitlab_ci, remote, package, dependencies, compiler, version, user, channel, package_args):
    job = job_tag([package], compiler, version, package_args)
    build_job = build_job_tag([package], compiler, version, package_args)

    settings, others = filter_package_args(package_args, "settings")

    print("gitlab ci job " + job)

    gitlab_ci[build_job] = {
        "tags": ["linux", "docker"],
        "image": "conanio/" + compiler,
        "stage": package,
        "script": ["conan profile update settings.{}={} default".format(name, value) for name, value in settings] + [
            "CONAN_VERSION_OVERRIDE={version} conan create --profile=default {flags} {package} {package}/{version}@{user}/{channel} --build=missing --build={package}" \
                .format(version=version, package=package, user=user, channel=channel, flags=format_flags(dependencies + [package], others)),
            "conan remove -b -s -f \"*\"",
            "conan upload {package}/{version}@{user}/{channel} -r {remote} --all --force --retry 3" \
                .format(package=package, version=version, user=user, channel=channel, remote=remote)
        ]
    }

def generate_gitlab_recipe_scripts_package(gitlab_ci, remote, package, user, channel):
    job = "build_{}@{}/{}".format(package, user, channel)
    package_id = package.split("/")
    package_name = package_id[0]
    package_version = package_id[1]

    print("gitlab ci job {}".format(job))

    gitlab_ci[job] = {
        "tags": ["linux", "docker"],
        "image": "lasote/conangcc5",
        "stage": "common-recipe-scripts",
        "script": [
            "export RECIPE_DIR=`manu343726-conan-tools generate_python_package {} {} {} {} --with-test --url \"https://gitlab.com/Manu343726/clang-conan-packages\"`"
                .format(package_name, package_version, user, channel),
            "cat -n $RECIPE_DIR/conanfile.py",
            "cat -n $RECIPE_DIR/test_package/conanfile.py",
            "conan create $RECIPE_DIR {}/{}".format(user, channel),
            "conan upload {}@{}/{} --all --force --retry 3 -r {}".format(package, user, channel, remote)
        ]
    }


def generate_gitlab(template):
    total_package_variants = 0
    total_packages = 0
    gitlab_ci = {}

    gitlab_ci['before_script'] = [
        "export PATH=$PATH:$HOME/.local/bin/",
        "pip install --user manu343726-conan-tools",
        "pip install --user --upgrade conan",
        "conan --version",
        "conan remote add {} {}".format(template["remote"]["name"], template["remote"]["url"]),
        "conan remote add bincrafters  https://api.bintray.com/conan/bincrafters/public-conan",
        "conan profile new --detect default",
        "if [[ ! -z \"${0}\" ]]; then echo remote password variable \"{0}\" not empty, ok; else echo remote password variable \"{0}\" empty, error && exit 1; fi".format(template["remote"]["password"]),
        "conan user {} -p ${} -r {}".format(template["remote"]["user"], template["remote"]["password"], template["remote"]["name"])
    ]

    if "remotes" in template:
        for remote, url in template["remotes"].items():
            gitlab_ci["before_script"].append("conan remote add {} {}".format(remote, url))

    gitlab_ci["stages"] = list(template["packages"]) if "packages" in template else []

    if "explicit-jobs" in template:
        for name, job in template["explicit-jobs"].items():
            gitlab_ci[name] = job

            if "stage" in job and not job["stage"] in gitlab_ci["stages"]:
                gitlab_ci["stages"].insert(0, job["stage"])

    if "common-recipe-scripts" in template:
        gitlab_ci["stages"].insert(0, "common-recipe-scripts")

        for scripts_package in template["common-recipe-scripts"]:
            total_packages += 1
            generate_gitlab_recipe_scripts_package(gitlab_ci, template["remote"]["name"], scripts_package, template["channel"]["user"], template["channel"]["channel"])


    package_matrix = input_matrix(template, ["settings", "options"])

    logging.debug("package matrix: {}".format(package_matrix))

    if "compilers" in template and \
       "packages" in template:
        for compiler in template["compilers"]:
            for package_args in package_matrix:
                total_package_variants += 1

                packages = template["packages"]
                logging.debug("packages before processing: {}".format(template["packages"]))

                if isinstance(packages, dict):
                    for package, properties in packages.items():
                        logging.debug("{}.properties: {}".format(package, properties))
                        total_packages += 1

                        if properties is None:
                            template["packages"][package] = {}

                        if not "versions" in template["packages"][package]:
                            if not "versions" in template:
                                logging.error("\"versions\" global config field required for packages with no explicit versions")
                                sys.exit(1)

                            template["packages"][package]["versions"] = template["versions"]
                else:
                    packages = template["packages"]
                    template["packages"] = {}

                    for package in packages:
                        total_packages += 1
                        template["packages"][package] = {
                            "versions": template["versions"]
                        }

                logging.debug("packages after processing: {}".format(template["packages"]))

                for package, properties in template["packages"].items():
                    for version in properties["versions"]:
                        generate_gitlab_package(gitlab_ci, template["remote"]["name"], package, build_job_dependencies(template["packages"], package), compiler, version, template["channel"]["user"], template["channel"]["channel"], package_args)

    print("\n\n Done. {} package variants in {} packages/stages. Total: {} different compiled packages/jobs."
        .format(total_package_variants, len(gitlab_ci["stages"]), total_packages))

    yaml.dump(gitlab_ci, open('.gitlab-ci.yml', 'w'), default_flow_style = False)


def run(args):
    with open(args.config_file) as template_file:
        try:
            template_yaml = yaml.load_all(template_file)
            template = list(template_yaml)[0]

            {
                'gitlab': generate_gitlab
            }[args.service](template)
        except yaml.YAMLError as err:
            eprint("Error loading CI config file: {}", err)

def setup_argparser(subparsers):
    parser = subparsers.add_parser('generate_ci', description='Generates CI configuration files to test, package, and upload conan packages')
    parser.add_argument('-s', '--service', default='gitlab', choices=['gitlab'], help='Name of the CI service the output file should implement (travis, gitlab, appveyor, etc)')
    parser.add_argument('-c', '--config-file', default='config.yml', help='YAML file with the packaging configuration')
    parser.set_defaults(func=run)
