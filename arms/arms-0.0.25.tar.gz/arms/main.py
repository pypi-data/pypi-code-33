import os
import lesscli
import hashlib
import requests
import yaml
from jinja2 import Template

from arms.utils import project_to_package, camelize
from arms.ubuntu import build_system

PY2 = (type(b'') == str)
if PY2:
    input = raw_input
    def makedir(real_path):
        os.system("mkdir -p " + real_path)

else:
    def makedir(real_path):
        from pathlib import Path
        Path(real_path).mkdir(parents=True, exist_ok=True)


def print_help():
    text = """

    arms init                   : setup CI/CD
    arms run [stage]            : run scripts of .gitlab-ci.yml
    arms docker prune           : prune docker container/image/volume
    arms paste [format]         : change coped content into another format
    arms yapi [json|controller
        |model|schema] --java=[package]
        [--check] [inpath] --ctxpath=[ctxpath]
        -o [outpath]            : build yapi from markdown
    arms ubuntu
    arms -h                     : show help information
    arms -v                     : show version


    """
    print(text)


def print_version():
    from arms import __version__
    text = """
    arms version: {}

    """.format(__version__)
    print(text)


def grab(project, lang):
    package = project_to_package(project)
    get_port = lambda name: int(hashlib.sha1(name.encode()).hexdigest(), 16) % 22000 + 10000
    port = get_port(package)  # [10000, 32000)
    mysql_port = get_port(package+'_mysql')
    redis_port = get_port(package+'_redis')
    package_upper = camelize(package)
    package_lower = camelize(package, False)
    base = 'http://gitlab.parsec.com.cn/qorzj/chiji-tool/raw/master/templates/' + lang
    index_text = requests.get(base + '/.index.txt').text
    data = {
        'project': project, 'package': package,
        'package_upper': package_upper, 'package_lower': package_lower, 'image': package.lower(),
        'port': port, 'mysql_port': mysql_port, 'redis_port': redis_port,
    }
    for line in index_text.splitlines():
        if not line: continue
        url = base + '/' + line
        real_path = Template(line).render(**data).replace('_PLACEholder_', '')
        print(url + '\t' + real_path)
        if real_path[-1] == '/':
            makedir(real_path)
        else:
            req = requests.get(url)
            if req.status_code == 404:
                print('Template not found!')
                return
            file_text = req.text
            rended_text = Template(file_text).render(**data)
            if real_path == '.gitignore' and os.path.isfile(real_path):  # merge .gitignore
                old_lines = open(real_path).read().splitlines()
                for new_line in rended_text.splitlines():
                    if new_line not in old_lines:
                        old_lines.append(new_line)
                rended_text = '\n'.join(old_lines) + '\n'

            with open(real_path, 'wb') as f:
                f.write(rended_text.encode('utf-8'))
    print('---- Done ----')


def run_init():
    if not os.path.isdir('.git'):
        print('Please change workdir to top!')
        return
    front = input('Please input front or back: [front / back] ')
    lang_front = ['react', 'build']
    lang_back = ['java', 'node', 'python', 'nginx']
    if front == 'front':
        lang_short = input('Please input language: [%s] ' % ' / '.join(lang_front))
        assert lang_short in lang_front
    elif front == 'back':
        lang_short = input('Please input language: [%s] ' % ' / '.join(lang_back))
        assert lang_short in lang_back
    else:
        print('Error, please check!')
        return
    lang = front + '-' + lang_short
    project = os.path.abspath('').rsplit('/')[-1]
    grab(project, lang)


def run_run(stage):
    if not os.path.isfile('.gitlab-ci.yml'):
        print('.gitlab-ci.yml not found!')
        return
    try:
        obj = yaml.load(open('.gitlab-ci.yml').read())
    except:
        print('Cannot load .gitlab-ci.yml')
        return

    def _get_scripts(stage):
        for v in obj.values():
            if isinstance(v, dict) and v.get('stage') == stage:
                return v.get('script', [])

    scripts = _get_scripts(stage)
    if not scripts:
        print('Scripts of stage[{}] is empty'.format(stage))
        return
    for cmd in scripts:
        print('>>', cmd)
        errno = os.system(cmd)
        if errno:
            print('---- Failed! [errno: %d] ----' % errno)
            exit(errno)
    print('---- Done. ----')


def run_docker_prune():
    os.system('docker container prune -f')
    os.system('docker image prune -f')
    os.system('docker volume prune -f')


def run_paste(format):
    pyperclip = None
    try:
        import pyperclip
    except:
        print('---- Failed! Dependence pyperclip not installed ----')
        print('---- Need to run: pip install pyperclip ----')
        exit(1)
    format = format.lower()
    if format not in ['po', 'db', 'acl']:
        print('---- Failed! Only support format [po, db, acl] ----')
        exit(1)
    raw_content = pyperclip.paste()
    if not raw_content:
        print('---- Failed! Please copy content first')
        exit(1)

    # translate format: po
    if format == 'po':
        typedict = {'string': 'String', 'number': 'Integer', '': '____'}
        lines = []
        for raw_line in raw_content.splitlines():
            segs = raw_line.lstrip().split('\t')
            if len(segs) < 3:
                print('---- Failed! Unknown input format ----'); print(segs); print('')
                exit(1)
            varname, explain, vartype = segs[:3]
            javatype = 'Date' if varname.endswith('At') \
                else typedict.get(vartype, vartype)
            lines.append('\tprivate {T} {name};  // {expl}'.format(T=javatype, name=varname, expl=explain))
        out_content = '\n'.join(lines)
    elif format == 'db':
        typedict = {'int': 'Integer', 'smallint': 'Integer',
                    'varchar': 'String', 'text': 'String', 'json': 'String',
                    'datetime': 'Date'}
        lines = []
        for raw_line in raw_content.splitlines():
            if ' COMMENT ' not in raw_line: raw_line += ' COMMENT '
            left, explain = raw_line.split(' COMMENT ', 1)
            segs = left.lstrip().split()
            if len(segs) < 2 or segs[0][0] != '`':
                print('---- Failed! Unknown input format ----'); print(segs); print('')
                exit(1)
            varname, vartype = segs[:2]
            varname = varname.replace('`', '')
            vartype = vartype.split('(', 1)[0] if '(' in vartype else vartype
            javatype = typedict.get(vartype, vartype)
            explain = explain.strip()
            explain = explain[1:-2] if explain.startswith("'") and explain.endswith("',") else explain
            lines.append('\tprivate {T} {name};  // {expl}'.format(T=javatype, name=varname, expl=explain))
        out_content = '\n'.join(lines)
    elif format == 'acl':
        fields = {}
        lines = []
        try:
            for raw_line in raw_content.splitlines():
                key, content = raw_line.strip().split(None, 1)
                fields[key] = content
            url = fields.get('请求Url', '')
            method = fields.get('请求类型', '')
            name = fields.get('接口名称', '')
            desc = fields.get('接口描述', '')
            pathvar = ''
            if url.count(':') == 1:
                pathvar = url.split(':')[-1]
                url = url.replace(':'+pathvar, '{'+pathvar+'}')

            lines.append("// (NULL,'{url}','{method}','',NULL,'{name}'),".format(url=url, method=method, name=name))
            if name: lines.append("// " + name)
            if desc: lines.append("// " + desc)
            lines.append('@{method}Mapping("{url}")'.format(method=method.capitalize(), url=url))
            if pathvar:
                lines.append('public Result ____(@PathVariable("%s") int %s) {' % (pathvar, pathvar))
            else:
                lines.append('public Result ____(____) {')
            lines.append('    return null;')
            lines.append('}')
        except:
            print("""复制文本的样例：
            接口名称 生成查询二维码
            请求类型 get
            请求Url  /wx/makeQRCode/:fileno
            接口描述 直接返回png格式的二维码图片
            """)
            exit(1)
        out_content = '    ' + '\n    '.join(lines) + '\n\n'
    else:
        raise NotImplementedError
    pyperclip.copy(out_content)
    print('\n%s\n' % out_content)
    print('---- Content above is copied ----')


def run_yapi(option, infile, outfile, javaroot, ctxpath, checkonly):
    from arms.yapi.model import Project, YapiProject
    from arms.yapi.java_util import controller_tool, model_tool, schema_tool
    # option in 'json|controller|model|schema'
    if option == 'json':
        assert outfile.endswith('.json'), "outfile[%s] is not a .json file" % outfile
        project = Project.loads(open(infile).read())
        yapijson = YapiProject.yapijson_of(project, ctxpath)
        with open(outfile, 'w') as fout:
            fout.write(yapijson)
    elif option == 'controller':
        controller_tool.process(inpath=infile, outpath=outfile, javaroot=javaroot, checkonly=checkonly)
    elif option == 'model':
        model_tool.process(infile=infile, outpath=outfile, javaroot=javaroot, checkonly=checkonly)
    elif option == 'schema':
        schema_tool.process(infile=infile, outfile=outfile, checkonly=checkonly)
    else:
        raise NotImplementedError
    print('done.')


def run(*a, **b):
    if 'h' in b or 'help' in b:
        print_help()
    elif 'v' in b or 'version' in b:
        print_version()
    elif tuple(a) == ('init',):
        run_init()
    elif len(a) == 2 and a[0] == 'run':
        stage = a[1]
        run_run(stage)
    elif tuple(a) == ('docker', 'prune'):
        run_docker_prune()
    elif len(a) >= 1 and a[0] == 'paste':
        run_paste(a[1] if len(a) > 1 else '')
    elif len(a) == 3 and a[0] == 'yapi':
        run_yapi(option=a[1], infile=a[2], outfile=b['o'], javaroot=b.get('java', ''),
                 ctxpath=b.get('ctxpath', ''), checkonly='check' in b)
    elif len(a) == 1 and a[0] == 'ubuntu':
        build_system()
    else:
        print_help()


def entrypoint():
    lesscli.run(callback=run, single='hv')
