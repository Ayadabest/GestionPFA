from django.db import models
from users.models import User
from django.utils import timezone
from datetime import datetime

class Project(models.Model):
    STATUS_CHOICES = (
        ('available', 'Disponible'),
        ('assigned', 'Attribué'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervised_projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(default=datetime(timezone.now().year, 6, 30).date())
    requirements = models.TextField()
    max_students = models.IntegerField(default=2)
    
    def __str__(self):
        return self.title

class ProjectSubmission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey('pfa_teams.Team', on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to='submissions/')
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return f"Submission for {self.project.title} by {self.submitted_by}"

class Deadline(models.Model):
    TYPE_CHOICES = (
        ('report', 'Rapport'),
        ('presentation', 'Présentation'),
        ('demo', 'Démonstration'),
        ('other', 'Autre'),
    )
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='deadlines')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    deadline_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class DelayNotification(models.Model):
    """Modèle pour les notifications de retard de projets"""
    DELAY_TYPES = (
        ('deadline_missed', 'Échéance dépassée'),
        ('project_delay', 'Retard de projet'),
        ('report_delay', 'Retard de rapport'),
        ('presentation_delay', 'Retard de présentation'),
        ('warning', 'Avertissement'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='delay_notifications')
    team = models.ForeignKey('pfa_teams.Team', on_delete=models.CASCADE, related_name='delay_notifications')
    delay_type = models.CharField(max_length=20, choices=DELAY_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    deadline_date = models.DateTimeField()
    days_late = models.IntegerField(default=0)
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_delay_notifications')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Retard {self.delay_type} - {self.team.name} - {self.project.title}"
    
    def get_priority_color(self):
        """Retourne la couleur CSS selon la priorité"""
        colors = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'danger'
        }
        return colors.get(self.priority, 'warning')
    
    def get_delay_type_display_icon(self):
        """Retourne l'icône selon le type de retard"""
        icons = {
            'deadline_missed': 'fas fa-calendar-times',
            'project_delay': 'fas fa-clock',
            'report_delay': 'fas fa-file-alt',
            'presentation_delay': 'fas fa-presentation',
            'warning': 'fas fa-exclamation-triangle'
        }
        return icons.get(self.delay_type, 'fas fa-exclamation')

class Message(models.Model):
    """Modèle pour la messagerie entre professeurs et étudiants"""
    MESSAGE_TYPES = (
        ('student_to_teacher', 'Étudiant vers Professeur'),
        ('teacher_to_student', 'Professeur vers Étudiant'),
        ('admin_to_all', 'Admin vers Tous'),
    )
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_project_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_project_messages')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_messages', null=True, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='student_to_teacher')
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    auto_classified_as_report = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Message de {self.sender.username} à {self.recipient.username} - {self.subject}"
    
    def mark_as_read(self):
        """Marquer le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def is_pdf_attachment(self):
        """Vérifie si le message contient une pièce jointe PDF"""
        if self.attachment:
            return self.attachment.name.lower().endswith('.pdf')
        return False
    
    def auto_classify_as_report(self):
        """Classe automatiquement le message comme un rapport si c'est un PDF d'étudiant"""
        if (self.message_type == 'student_to_teacher' and 
            self.is_pdf_attachment() and 
            self.project and 
            not self.auto_classified_as_report):
            
            # Trouver l'équipe de l'étudiant pour ce projet
            from pfa_teams.models import Team
            try:
                team = Team.objects.get(members=self.sender, project=self.project)
                
                # Créer un rapport automatiquement
                report = Report.objects.create(
                    project=self.project,
                    team=team,
                    title=f"Rapport automatique: {self.subject}",
                    document=self.attachment,
                    status='pending',
                    feedback=f"Rapport automatiquement classé depuis un message de {self.sender.get_full_name()}"
                )
                
                # Marquer le message comme classé
                self.auto_classified_as_report = True
                self.save()
                
                # Créer une notification pour le professeur
                Notification.objects.create(
                    user=self.recipient,
                    title=f"Nouveau rapport reçu - {self.project.title}",
                    message=f"Un nouveau rapport a été automatiquement classé depuis un message de {self.sender.get_full_name()}. Titre: {self.subject}",
                    link=f"/projects/reports/{report.id}/"
                )
                
                return report
            except Team.DoesNotExist:
                # L'étudiant n'a pas d'équipe pour ce projet
                pass
        
        return None
    
    def get_unread_count_for_user(user):
        """Retourne le nombre de messages non lus pour un utilisateur"""
        return Message.objects.filter(recipient=user, is_read=False).count()

class ProjectStatistics(models.Model):
    project = models.OneToOneField('Project', on_delete=models.CASCADE, related_name='statistics')
    total_reports = models.IntegerField(default=0)
    approved_reports = models.IntegerField(default=0)
    rejected_reports = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    team_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Statistics for {self.project.title}"

    def calculate_completion_rate(self):
        if self.total_reports > 0:
            return (self.approved_reports / self.total_reports) * 100
        return 0

class Report(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('reviewed', 'Revu'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    )
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='reports')
    team = models.ForeignKey('pfa_teams.Team', on_delete=models.CASCADE, related_name='submitted_reports')
    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='reports/')
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    deadline = models.ForeignKey(Deadline, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Rapport {self.title} - {self.team}"

    def save(self, *args, **kwargs):
        # Mettre à jour les statistiques
        stats, created = ProjectStatistics.objects.get_or_create(project=self.project)
        if self.pk is None:  # Nouveau rapport
            stats.total_reports += 1
        else:  # Mise à jour d'un rapport existant
            old_status = Report.objects.get(pk=self.pk).status
            if old_status != self.status:
                if self.status == 'approved':
                    stats.approved_reports += 1
                elif self.status == 'rejected':
                    stats.rejected_reports += 1
        stats.save()
        super().save(*args, **kwargs)

class ProjectReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='student_reports')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.get_full_name()}"
