import yaml
import gitlab
import base64

from urllib.parse import urljoin


class GitLabFactory:
    def __init__(self, project_id, gitlab_id, config_file):
        self.gl = gitlab.Gitlab.from_config(gitlab_id, [config_file])
        self.gl.auth()
        self.project = self.gl.projects.get(project_id)
        self.tools = {}
        self.workflows = {}
        self.imports_cwls = {}

    def get_repository_tree(self, path, ref):
        return self.project.repository_tree(path=path, ref=ref)

    def get_cwl(self, item_id):
        file_info = self.project.repository_blob(item_id)
        return yaml.load(base64.b64decode(file_info['content']))

    def get_imported_cwl_field(self, field, cwl, cwl_url, items):
        if field in cwl:
            for r in cwl[field]:
                if '$import' in r:
                    file_path = urljoin(cwl_url, r['$import'])
                    for item in items:
                        if item['path'] == file_path:
                            import_info = self.project.repository_blob(item['id'])
                            self.imports_cwls[item['name']] = {
                                'cwl': yaml.load(base64.b64decode(import_info['content'])),
                                'cwl_url': urljoin(cwl_url, item['path'])
                            }

    def get_imported_cwl(self, cwl, cwl_url, items):
        self.imports_cwls.clear()
        self.get_imported_cwl_field('requirements', cwl, cwl_url, items)
        self.get_imported_cwl_field('hints', cwl, cwl_url, items)

    def load_cwl_data(self, ref, path=None):
        items = self.project.repository_tree(path=path, ref=ref)
        for t in items:
            if t['type'] == 'tree':
                self.load_cwl_data(path=t['path'], ref=ref)
            elif t['type'] == 'blob' and t['name'].endswith('.cwl'):
                cwl = self.get_cwl(t['id'])
                label = None if 'label' not in cwl else cwl['label']
                if label:
                    cwl_url = urljoin(self.project.web_url + '/', 'raw/')
                    cwl_url = urljoin(cwl_url, 'master/')
                    cwl_url = urljoin(cwl_url, t['path'])
                    self.get_imported_cwl(cwl, cwl_url, items)
                    if cwl['class'] == 'Workflow':
                        self.workflows[label] = {
                            'cwl': cwl,
                            'cwl_url': cwl_url,
                            'imports': self.imports_cwls
                        }
                    else:
                        self.tools[label] = {
                            'cwl': cwl,
                            'cwl_url': cwl_url,
                            'imports': self.imports_cwls
                        }
