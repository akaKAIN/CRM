from django import forms
from django.forms import ModelForm

from .models import Tourist


class EditTouristModelForm(ModelForm):

    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Tourist
        fields = ['name',
                  'phone',
                  'email',
                  'date_of_arrival',
                  'date_of_departure',
                  'note',
                  'status',
                  'hotel',
                  'group',
                  ]
