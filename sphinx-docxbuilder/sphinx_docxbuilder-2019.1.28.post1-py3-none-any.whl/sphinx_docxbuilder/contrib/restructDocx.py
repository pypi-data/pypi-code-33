#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
from ..docx import DocxDocument

if __name__ == '__main__':
    if len(sys.argv) > 2:
        doc = DocxDocument()
        doc.restruct_docx(sys.argv[1], sys.argv[2])
    else:
        print(sys.argv[0], " <docx dir> <docx filename>")
