import cgi

from docify import components as c
from docify.formatters.html import HTML


DOC_TMPL = '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <title>Docify Document</title>
    </head>
    <body>
        <div class="sidebar col-lg-3 col-md-2"></div>
        <div id="container" class="container col-lg-6 col-md-8">
            {}
        </div>
        <div class="sidebar col-lg-3 col-md-2"></div>
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    </body>
</html>
'''


class HTMLBootstrap(HTML):
    '''HTMLBootstrap formatter to format into fancy static web page.'''

    tmpl = DOC_TMPL

    def update_handlers(self):
        '''Overwriting parent's method'''

        super(HTMLBootstrap, self).update_handlers()

        @self.handle(c.Pre)
        def handle_pre(self, obj):
            return self.tag('pre', obj.components, {
                'class': 'bg-light rounded'})

        @self.handle(c.Code)
        def handle_code(self, obj):
            return self.tag('code', obj.components, {
                'class': 'bg-light rounded'})
