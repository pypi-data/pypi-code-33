import os
import subprocess

def convert_menu(menu_pdf):
    with open(os.devnull, 'w') as devnull:
        path_to_menu_pdf = os.path.dirname(os.path.abspath(menu_pdf))
        flattened_pdf = path_to_menu_pdf + "/menu_flattened.pdf"
        subprocess.run(["gs", "-o", flattened_pdf, "-sDEVICE=pdfwrite", menu_pdf], stdout=devnull, stderr=devnull)
        menu_txt = path_to_menu_pdf + "/menu.txt"
        subprocess.run(["pdftotext", flattened_pdf, menu_txt], stdout=devnull, stderr=devnull)
        return menu_txt
