from django import forms
from django.forms import ModelForm

from .models import Tourist, Nutrition


class UpdateTouristModelForm(ModelForm):

    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    date_of_arrival = forms.DateField(widget=forms.SelectDateWidget)
    date_of_departure = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Tourist
        fields = ['name',
                  'phone',
                  'email',
                  'date_of_arrival',
                  'date_of_departure',
                  'note',
                  'status',
                  'nutrition',
                  'hotel',
                  'group',
                  'excursion',
                  'files']


class CreateTouristModelForm(ModelForm):

    visa = forms.FileField(widget=forms.ClearableFileInput, label='Select a file', required=False)
    contract = forms.FileField(widget=forms.ClearableFileInput, required=False)
    passport = forms.FileField(widget=forms.ClearableFileInput, required=False)
    others = forms.FileField(widget=forms.ClearableFileInput, required=False)

    class Meta:
        model = Tourist
        fields = ['name',
                  'phone',
                  'email',
                  'date_of_arrival',
                  'date_of_departure',
                  'note',
                  'status',
                  'nutrition',
                  'hotel',
                  'group',
                  'excursion',
                  'visa',
                  'contract',
                  'passport',
                  'others']


class UploadFileForm(ModelForm):

    class Meta:
        model = Tourist
        fields = '__all__'

