import docutils.core
import docutils.parsers.rst


'''
Engine
   
| #rst_str            rst-string
| #html_str           html-string
| #xml_str            xml-string
| #tree               docutils.nodes.document-tree
| #r                  rst_str
| #t..................docutils.nodes.document-tree
| #h                  html_str
| #x                  xml_str
| #r2h                rst_str-to-html_str
| #r2t                rst_str-to-docutils.nodes.document_tree
| #t2x                docutils.nodes.document_tree-to-rst_str
| #r2x            rst_str-to-xml_str
'''


def r2h(rst_str):
    '''
    | convet rst_str to html_str,which includes CSS in it.
    
    :param rst_str: string.
        rst-string.
    :return: string.
        html-string.
    
    '''
    html_dict = docutils.core.publish_parts(writer_name='html',source=rst_str)
    return(html_dict['whole'])

def r2t(rst_str,name=''):
    '''
    | convert rst_str to docutils.nodes.document_tree
    
    :param rst_str: string.
        rst_str.
    :param name: string.
        the source attribute of document node of the tree,this is not important,any html escaped string is OK.
        Default is ""
    :return: docutils.nodes.document.
        doc-tree-root-node
    '''
    parser = docutils.parsers.rst.Parser()
    doc = docutils.utils.new_document(name)
    doc.settings.tab_width = 4
    doc.settings.pep_references = 1
    doc.settings.rfc_references = 1
    doc.settings.syntax_highlight = 1
    doc.settings.trim_footnote_reference_space = 1
    parser.parse(rst_str, doc)
    return(doc)

def t2x(tree):
    '''
    | convert docutils.nodes.document_tree  to xml 
    
    :param docutils.nodes.document.
        doc-tree-root-node
    
    :return: string.
        xml_str
    '''
    xdom = tree.asdom()
    xml_str = xdom.toprettyxml()
    xml_str = xml_str.replace("\t","\x20"*4)
    return(xml_str)

def r2x(rst_str,name=''):
    '''
    | convert rst_str to xml_str
    
    :param rst_str: string.
        rst_str.
    :param name: string.
        the source attribute of document node of the tree,this is not important,any html escaped string is OK.
        Default is ""
    :return: string.
        xml_str
    '''
    tree = r2t(rst_str,name)
    xml_str = t2x(tree)
    return(xml_str)


#####
