from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Template, Context
from django.template.loader import get_template
import re

#from mycms.models import Paths, Pages
#from mycms.pageview.base import get_pageview


register = template.Library()
from . import registry

script_str_re_obj =re.compile(r"""(?P<name>src|type)="(?P<value>.*)"|((?P<name2>priority)=(?P<value2>(\d*)))""", re.DOTALL)


@register.inclusion_tag('mycms/templatetags/file_upload.html')
def file_upload():
    #Nothing to add to the context for now.
    return { "none": None }

@register.inclusion_tag('mycms/templatetags/article_editor.html')
def article_editor():
    #Nothing to add to the context for now.
    return { "none": None }




class NullNode(template.Node):
    
    def __init__(self):
        pass
    
    def render(self, context):
        return ""

@register.simple_tag(takes_context=True)
def Script(context, *args, **kwargs):

    #TODO: Currently we only support isLoggedIn=True or False
    isLoggedIn = kwargs.get('isLoggedIn', False)
    src = kwargs.get("src", None);
    
    if kwargs.get("src", None) is not None: 
        #We need at minimum src
        if isLoggedIn: 
            #the isLoggedIn flag is used to know if we need to check whether
            #the user is logged in or not. If he is not logged in , then 
            #there is nothing to do and we just return an empty string. 
            #Needs to check if the user is logged in. 
            view_object = context["view_object"]
            
            if not view_object.request.user.is_authenticated(): 
                #If user is not authenticated then we should not add
                #this script. 
                return ""
        
        registry.register(src=kwargs.get("src","/dummy/path"),
                                  type=kwargs.get("type", "text/javascript"),
                                  priority=kwargs.get("priority", 9999))
                
    else: 
        print("skipped {}".format(token_str))
        return ""
    
   
class ScriptCollectorNode(template.Node):
    def __init__(self):
        
        pass

    def __repr__(self):
        return "<ScriptCollectorNode>"

    def render(self, context):
       
        return registry.html()
    
@register.tag
def ScriptCollector(parser, token_str):
    return ScriptCollectorNode()

    
class NullNode(template.Node):
    
    def __init__(self):
        pass
    
    def render(self, context):
        return ""



@register.tag
def Link(parser, token_str):
    """
    Adds a <link> for our css at the header of the page.   
    """
 
    def parse_tokens(tokens):
        
        tokens = token_str.split_contents()
        tokens = tokens[1:] #the first is always the tag name.        
    
        #each token is expected to be of the format 
        # name=value


    
    
    
    