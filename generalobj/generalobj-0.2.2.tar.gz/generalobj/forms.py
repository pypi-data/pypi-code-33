from django import forms
from django.contrib.auth.models import User

class GeneralObjForm(forms.ModelForm):
    """
    This is a general class for forms used almost everywhere.
    
    It sets the autofocus if needed
    
    It handles live_search parameters
    
    It takes care about help_texts
    
    It handles User selections and DatePickers
    
    It makes automatic changes to Labels.
    """
    
    def __init__(self, *args, **kwargs):
        """The init method"""
        self.request = kwargs.pop('request', None)
        super(GeneralObjForm, self).__init__(*args, **kwargs)
        #slow solution, needs to be replaced!
        focus_to = [field for field in self.fields][0]
        self.fields[focus_to].widget.attrs.update({'autofocus': 'autofocus'})
        for field in self.fields:
            sfield = self.fields[field]

            #live_search
            self.fields[field].live_search = False
            if hasattr(sfield, 'choices'):
                if sfield.choices.queryset.count() > 10:
                    sfield.live_search = True

            #Help text
            help_text = self.fields[field].help_text
#            self.fields[field].help_text = None
##            if help_text != '':
##                self.fields[field].widget.attrs.update(\
##                        {'class':'has-popover',
##                         'data-content':help_text,
##                         'data-placement':'right',
##                         'data-container':'body'
##                        })

            #User selections
            if hasattr(sfield, 'choices'):
                if sfield.choices.queryset.count():
                    if type(sfield.choices.queryset[0]) == User:
                        sfield.label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
                        sfield.queryset = sfield.queryset.filter(is_active = True).order_by('first_name')

            #DateField
            sfield.date_field = False
            if hasattr(sfield, 'strptime'):
                sfield.date_field = True
                sfield.input_formats = ['%d/%m/%Y']
                inst = eval('self.instance.%s' % field)
                pass
                if inst:
                    self.initial[field] = inst.strftime('%d/%m/%Y')
                elif sfield.initial:
                    sfield.initial = sfield.initial.strftime('%d/%m/%Y')
            
            #User -> Creator
            if field == 'user':
                sfield.label = 'Creator'
    
    
            #Checkbox
            sfield.checkbox_field = False
            if sfield.__class__.__name__ == 'BooleanField':
                sfield.checkbox_field = True
