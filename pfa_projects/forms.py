from django import forms
from .models import Project, ProjectSubmission, Message
from users.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'requirements', 'deadline', 'max_students']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
        }

class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = ['document', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'project', 'subject', 'content', 'attachment', 'message_type']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Tapez votre message ici...'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Sujet du message'}),
            'message_type': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        if sender:
            # Filtrer les destinataires selon le rôle de l'expéditeur
            if sender.role == 'student':
                # Les étudiants peuvent envoyer des messages aux professeurs et à l'admin
                self.fields['recipient'].queryset = User.objects.filter(role__in=['teacher', 'admin'])
                self.fields['message_type'].initial = 'student_to_teacher'
                self.fields['message_type'].choices = [('student_to_teacher', 'Étudiant vers Professeur')]
            elif sender.role == 'teacher':
                # Les professeurs peuvent envoyer des messages aux étudiants et à l'admin
                self.fields['recipient'].queryset = User.objects.filter(role__in=['student', 'admin'])
                self.fields['message_type'].initial = 'teacher_to_student'
                self.fields['message_type'].choices = [('teacher_to_student', 'Professeur vers Étudiant')]
            elif sender.role == 'admin':
                # L'admin peut envoyer des messages à tous
                self.fields['recipient'].queryset = User.objects.all()
                self.fields['message_type'].initial = 'admin_to_all'
                self.fields['message_type'].choices = Message.MESSAGE_TYPES
            
            # Filtrer les projets selon le rôle
            if sender.role == 'student':
                # Les étudiants voient leurs projets assignés via leurs équipes
                user_teams = sender.pfa_teams.all()
                project_ids = user_teams.values_list('project_id', flat=True)
                self.fields['project'].queryset = Project.objects.filter(id__in=project_ids)
            elif sender.role == 'teacher':
                # Les professeurs voient leurs projets supervisés
                self.fields['project'].queryset = Project.objects.filter(supervisor=sender)
            elif sender.role == 'admin':
                # L'admin voit tous les projets
                self.fields['project'].queryset = Project.objects.all()
            
            # S'assurer que la valeur initiale est définie dans les données du formulaire
            if not self.data.get('message_type') and self.fields['message_type'].initial:
                self.data = self.data.copy() if self.data else {}
                self.data['message_type'] = self.fields['message_type'].initial

class ReplyMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tapez votre réponse...'}),
        } 