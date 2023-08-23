from .models import *
from django import forms

class BotConfigurationForm(forms.ModelForm):
    creation_message = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    welcome_message = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    ticket_title = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    ticket_description = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    class Meta:
        model = BotServer
        fields = ['creation_message', 'welcome_message', 'ticket_title', 'ticket_description']



class BotServerForm(forms.ModelForm):
    creation_message = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    welcome_message = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    ticket_title = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    ticket_description = forms.CharField(widget=forms.Textarea (attrs={'class': 'form-control ', 'placeholder': 'Description'}))
    class Meta:
        model = BotServer
        fields = ['creation_message', 'welcome_message', 'ticket_title', 'ticket_description']


    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.templates = {
            'creation_message': self.cleaned_data['creation_message'],
            'welcome_message': self.cleaned_data['welcome_message'],
            'ticket_title': self.cleaned_data['ticket_title'],
            'ticket_description': self.cleaned_data['ticket_description'],
        }
        if commit:
            instance.save()
        return instance