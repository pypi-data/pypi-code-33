'''
PDFMiner.py

'''
import pickle

#from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.converter import PDFPageAggregator
#from pdfminer.layout import LAParams
#from pdfminer.pdfpage import PDFPage
#from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.pdftypes import PDFObjRef

from pprint import pprint
from argparse import ArgumentParser


def load_form(filename=None):
    """Load pdf form contents into a nested list of name/value tuples"""
    filename = './data/Id=MMP15%2F57_5694_5696.pdf'
    with open(filename, 'rb') as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)
        #print(dir(doc))
        #print()
        parser.set_document(doc)
        #print(dir(parser.set_document(doc)))
        #doc.set_parser(parser)
        doc.initialize()
        return [load_fields(resolve1(f)) for f in
                resolve1(doc.catalog['AcroForm'])['Fields']]


def load_fields(field):
    """Recursively load form fields"""
    form = field.get('Kids', None)
    if form:
        return [load_fields(resolve1(f)) for f in form]
    else:
        # Some field types, like signatures, need extra resolving
        return (field.get('T').decode('utf-8'), resolve1(field.get('V')))


def parse_cli():
    """Load command line arguments"""
    parser = ArgumentParser(description='Dump the form contents of a PDF.')
    parser.add_argument('file', metavar='pdf_form',
                        help='PDF Form to dump the contents of')
    parser.add_argument('-o', '--out', help='Write output to file',
                        default=None, metavar='FILE')
    parser.add_argument('-p', '--pickle', action='store_true', default=False,
                        help='Format output for python consumption')
    return parser.parse_args()


def main():
    #args = parse_cli()
    form = load_form()
    if args.out:
        with open(args.out, 'w') as outfile:
            if args.pickle:
                pickle.dump(form, outfile)
            else:
                pp = pprint.PrettyPrinter(indent=2)
                file.write(pp.pformat(form))
    else:
        if args.pickle:
            print(pickle.dumps(form))
        else:
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(form)

if __name__ == '__main__':
    main()
