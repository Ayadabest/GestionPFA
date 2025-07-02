from django import forms
from .models import Team, TeamRequest, Message, Report

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class TeamRequestForm(forms.ModelForm):
    class Meta:
        model = TeamRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'file', 'report_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Écrivez votre message ici...'}),
        }
        labels = {
            'content': 'Message',
            'attachment': 'Pièce jointe (optionnel)',
        } 