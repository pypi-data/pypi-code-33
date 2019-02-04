'''
pypdf2.py

'''
import io
import re
import requests
import PyPDF2

from PyPDF2 import PdfFileWriter, PdfFileReader
from pprint import pprint
from collections import OrderedDict


def pypdf2():
    '''
    A wrapper function to organize the steps involved to convert a PDF into text:
        1.  Get the PDF file using a URL
        2.  Read the PDF file using PyPDF2

    '''
    #pdfReader = PyPDF2.PdfFileReader(pdfIO_Obj)

    pdf_file_name = './data/Id=MMP15%2F57_5694_5696.pdf'
    infile = PdfFileReader(open(pdf_file_name, 'rb'))
    pdfReader = infile

    print(type(pdfReader))
    print('dir(pdfReader)')
    print(dir(pdfReader))
    fields = pdfReader.getFields()
    print(type(fields))
    print(fields)
    for key, value in fields.items():
        print(key, value)

    return
    #print('dir(pdfReader)')
    #print(dir(pdfReader))
    #print('pdfReader.getFields()')
    #print(pdfReader.getFields())
    #print('pdfReader.documentInfo')
    #print(pdfReader.documentInfo)
    #print('pdfReader.getPage(0)')
    #print(pdfReader.getPage(0))
    #print('pdfReader.getPageLayout()')
    #print(pdfReader.getPageLayout())
    #print(type(pdfReader.getPageLayout()))
    #print('pdfReader.numPages')
    #print(pdfReader.numPages)
    #print('pdfReader.pages')
    #print(pdfReader.pages)
    #print('pdfReader.getOutlines()')
    #print(pdfReader.getOutlines())
    #print(pdfReader.outlines)
    #print('pdfReader.trailer')
    #print(pdfReader.trailer)
    #print('pdfReader.flattenedPages')
    #print(pdfReader.flattenedPages)
    #print('pdfReader.getNamedDestinations()')
    #print(pdfReader.getNamedDestinations())
    #print('pdfReader.getPageMode()')
    #print(pdfReader.getPageMode())

    pageObj = pdfReader.getPage(0)
    print('dir(pageObj)')
    print(dir(pageObj))
    #print('pageObj.items()')
    #print(pageObj.items())
    #print(type(pageObj.items()))
    #print('pageObj.keys()')
    #print(pageObj.keys())
    #print('pageObj.values()')
    #print(pageObj.values())
    #print('pageObj.getObject()')
    #print(pageObj.getObject())
    #print('pageObj.getXmpMetadata')
    #print(pageObj.getXmpMetadata)
    #print(type(pageObj.extractText()))
    #print(pageObj.trimBox)
    for key, val in pageObj.items():
        #print(key, val)
        if 'Contents' in key:
            print(key)
            print(val)
            print(dir(val))


def _getFields(obj, tree=None, retval=None, fileobj=None):
    """
    found here:
    https://stackoverflow.com/a/43680515/6597765

    Extracts field data if this PDF contains interactive form fields.
    The *tree* and *retval* parameters are for recursive use.

    :param fileobj: A file object (usually a text file) to write
        a report to on all interactive form fields found.
    :return: A dictionary where each key is a field name, and each
        value is a :class:`Field<PyPDF2.generic.Field>` object. By
        default, the mapping name is used for keys.
    :rtype: dict, or ``None`` if form data could not be located.
    """

    fieldAttributes = {'/FT': 'Field Type', '/Parent': 'Parent',
            '/T': 'Field Name', '/TU': 'Alternate Field Name',
            '/TM': 'Mapping Name', '/Ff': 'Field Flags', '/V': 'Value',
            '/DV': 'Default Value'}

    if retval is None:
        retval = OrderedDict()
        catalog = obj.trailer["/Root"]
        # get the AcroForm tree
        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
        else:
            return None
    if tree is None:
        return retval

    obj._checkKids(tree, retval, fileobj)
    for attr in fieldAttributes:
        if attr in tree:
            # Tree is a field
            obj._buildField(tree, retval, fileobj, fieldAttributes)
            break

    if "/Fields" in tree:
        fields = tree["/Fields"]
        for f in fields:
            field = f.getObject()
            obj._buildField(field, retval, fileobj, fieldAttributes)

    return retval


def get_form_fields(infile):
    infile = PdfFileReader(open(infile, 'rb'))
    fields = _getFields(infile)
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())



if __name__ == '__main__':
    pypdf2()

    #pdf_file_name = './data/Id=MMP15%2F57_5694_5696.pdf'
    #pprint(get_form_fields(pdf_file_name))



