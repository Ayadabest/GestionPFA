from django.db import models
from django.utils import timezone
from users.models import User
from pfa_projects.models import Project

class Team(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    )
    
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='pfa_teams')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assigned_team')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject_choices = models.ManyToManyField(Project, through='SubjectChoice', related_name='interested_teams')
    
    def __str__(self):
        return f"{self.name} - {self.project.title}"

    def get_members_display(self):
        return ", ".join([user.get_full_name() for user in self.members.all()])

    def get_unread_messages_count(self, user):
        """Retourne le nombre de messages non lus pour un utilisateur donné."""
        if user == self.project.supervisor:
            return self.messages.filter(read=False).exclude(sender=user).count()
        else:
            return self.messages.filter(read=False, sender=self.project.supervisor).count()

class TeamRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Rejeté'),
    )
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    project = models.ForeignKey('pfa_projects.Project', on_delete=models.CASCADE, related_name='team_requests', null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Demande de {self.sender.get_full_name()} à {self.receiver.get_full_name()}"

    class Meta:
        unique_together = ('sender', 'receiver')

class SubjectChoice(models.Model):
    PRIORITY_CHOICES = (
        (1, '1er choix'),
        (2, '2ème choix'),
        (3, '3ème choix'),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    motivation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'priority')
        ordering = ['priority']

    def __str__(self):
        return f"{self.team.name} - {self.project.title} (Choix {self.priority})"

class TeamHistory(models.Model):
    ACTION_CHOICES = (
        ('created', 'Création'),
        ('approved', 'Approbation'),
        ('rejected', 'Rejet'),
        ('subject_choice', 'Choix du sujet'),
        ('subject_approved', 'Sujet approuvé'),
        ('subject_rejected', 'Sujet rejeté'),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.team.name} - {self.get_action_display()} par {self.performed_by.get_full_name()}"

class Report(models.Model):
    REPORT_TYPES = [
        ('progress', 'Rapport d\'avancement'),
        ('final', 'Rapport final'),
        ('presentation', 'Présentation'),
        ('other', 'Autre document'),
    ]

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='reports/')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)
    feedback_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.team.name}"

class Message(models.Model):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='messages/', blank=True, null=True)

    def __str__(self):
        return f"Message de {self.sender.username} à {self.team.name}"

    class Meta:
        ordering = ['-sent_at']
