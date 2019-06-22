from django import forms
from django.forms import ModelForm

from .models import Tourist, Nutrition


class TouristModelForm(ModelForm):

    date_of_arrival = forms.DateField(widget=forms.SelectDateWidget)
    date_of_departure = forms.DateField(widget=forms.SelectDateWidget)
    # Загрузка сразу нескольких файлов (пока не работает)
    # others = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    NUTRITION_CHOICES = list(enumerate(Nutrition.objects.values_list("name", flat=True)))
    nutrition = forms.ChoiceField(choices=NUTRITION_CHOICES)

    class Meta:
        model = Tourist
        fields = ['name', 'phone', 'email', 'date_of_arrival', 'date_of_departure',
                  'note', 'status', 'nutrition', 'visa', 'contract', 'passport', 'others']


