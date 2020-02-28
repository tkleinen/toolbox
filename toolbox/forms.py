from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorDict
from django.forms.forms import NON_FIELD_ERRORS

from toolbox.models import Problem, Location, Case, Parameter, Contact
from django.forms.widgets import TextInput, HiddenInput, Select
from django.utils.translation import ugettext as _
from django.contrib.localflavor.nl.forms import NLPhoneNumberField
from django.contrib.auth.models import User
from olwidget.widgets import EditableMap

class ProblemForm(ModelForm):
    class Meta:
        model = Problem
        
class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ('name','description','address','location')
        widgets = {'location': EditableMap(),}

class ParamForm(ModelForm):
    class Meta:
        model = Parameter
        fields = ('value',)
        widgets= {'value':TextInput(),}

class CaseForm(ModelForm):
    class Meta:
        model = Case
        exclude = ('user','problem','location')

class EditForm(forms.Form):
    value = forms.CharField(label=_('value'), required=False)

from registration.forms import RegistrationForm

class RegistrationFormEx(RegistrationForm):
    first_name = forms.CharField(label=_('First name'))
    last_name = forms.CharField(label=_('Last name'))

class ContactForm(ModelForm):
    class Meta:
        model = Contact
#        widgets = {'phone': NLPhoneNumberField}

class LocationSelectForm(ModelForm):
    class Meta:
        model = Case
        fields = ('location',)

    def __init__(self, user, *args, **kwargs):
        super(LocationSelectForm, self).__init__(*args, **kwargs)
        self.fields['location'].widget.attrs['onchange'] = 'locationChanged(this);'
        if user:
            self.fields['location'].queryset = Location.objects.filter(user=user)

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login')
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['date_joined'].widget.attrs['disabled'] = True
            self.fields['last_login'].widget.attrs['disabled'] = True


# custom validation of editforms        
from django.forms.formsets import BaseFormSet

class BaseEditFormSet(BaseFormSet):

    input_variables = []

    def clean(self):
        # check r and (B+L)
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        
        # Do we have to check for r, B and L??
        va = [v.symbol for v in self.input_variables]
        if 'r' in va and ('B' in va or 'L' in va):
            d = {}
            for i in range(0, self.total_form_count()):
                v = va[i]
                if v in ['r','L','B']:
                    form = self.forms[i]
                    val = form.cleaned_data['value']
                    if(len(val)>0):
                        d[v] = val
            if 'r' in d:
                if 'L' in d or 'B' in d:
                    raise forms.ValidationError('Lengte en Breedte van de bouwput opgeven of de Afstand tot de bemaling, niet allebei')
            elif not ('L' in d and 'B' in d):
                    raise forms.ValidationError('Afstand tot de bemaling opgeven of de Lengte en Breedte van de bouwput')
                
