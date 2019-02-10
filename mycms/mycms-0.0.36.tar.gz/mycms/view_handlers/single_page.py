
class SinglePage(object):

    def __init__(self, page_object, request=None):
        
        self.request = request


    def on_create(self):
        pass


    @property
    def html_content(self):
        """The html content of the page. This formats the page
        using the CreoleFormatter"""

        logger.debug("html_content entered")

        #TODO: Fix me: This loads only the first content entry.
        #      This should be updated to load by date.

        try:
            content_obj = self.page_object.content.all()[0]
        except IndexError as e:

            if settings.DEBUG:
                msg = """We did not find a content_obj so returning a fake content since DEBUG is swithed on."""
                logger.debug(msg)
                return CreoleFormatter().html(fake_content=True)
            else:
                return "Error: There is no content for this page."

        #TODO: Fix me: right now hardcoded to creole.

        #We pass the view into our custom CreoleFormatter so that the
        #custom creole markup can have access.
        _html_content =  CreoleFormatter(content_obj.content,view=self).html()

        logger.debug("Call to YACMSObject.html_content returns: \n {}".format(_html_content))
        
        
        return _html_content
    
     