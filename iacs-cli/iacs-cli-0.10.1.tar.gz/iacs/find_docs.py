import os, re


def find_docs(root):
    document_dir = dict()
    for dirname, subdirList, files in os.walk(root):
        for file in files:
            doc = os.path.join(dirname, file)
            if re.search(".md", file):
                with open(doc, 'r') as file:
                    row = file.readline()
                    title = row[6:].strip()
                    idx = re.match("^([^:]*)", title)
                    if idx:
                        document_dir[idx.group(0)] = doc

    return document_dir
