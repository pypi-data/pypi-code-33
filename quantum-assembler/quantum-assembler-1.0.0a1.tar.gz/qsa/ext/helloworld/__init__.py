from qsa.ext.base import BaseExtension


class Extension(BaseExtension):
    name = 'Hello World v1'
    command_name = 'helloworld'

    def on_project_init(self, quantum, typname, name, language):
        print(f"Initializing the {self.name} extension")
