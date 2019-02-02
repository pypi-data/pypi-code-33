import os
import json
import pickle
from yo_core._common import Obj

def find_root_folder(root_file_name):
    root_path = './'
    for i in range(10):
        if os.path.isfile(root_path+root_file_name):
            return root_path
        root_path+='../'
    raise ValueError("Cound't find the root {1}. The current directory is {0}".format(os.path.abspath('.'), root_file_name))


def load_json(filename, as_obj=False):
    result = None
    with open(filename) as file:
        result = json.load(file)
    if as_obj:
        result = Obj.create(result)
    return result

def save_json(filename, obj):
    with open(filename,'w') as file:
        json.dump(obj,file,indent=1)

def load_pkl(filename):
    with open(filename,'rb') as file:
        return pickle.load(file)


def save_pkl(filename, obj):
    with open(filename,'wb') as file:
        pickle.dump(obj,file)


from IPython.display import HTML

def notebook_printable_version(finalize):
    if finalize:
        return HTML('''<script>
        code_show=true; 
        function code_toggle() {
         if (code_show){
         $('div.input').hide();
         $("div[class='prompt output_prompt']").css('visibility','hidden');

         } else {
         $('div.input').show();
         $("div[class='prompt output_prompt']").css('visibility','visible');
         }
         code_show = !code_show
        } 
        $( document ).ready(code_toggle);
        </script>
        <a href="javascript:code_toggle()">Automatically generated report</a>.''')
    else:
        return None