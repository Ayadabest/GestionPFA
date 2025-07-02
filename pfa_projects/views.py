from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from .models import Project, ProjectSubmission, Report, Deadline, Notification, ProjectStatistics, ProjectReport, DelayNotification, Message
from .forms import ProjectForm, ProjectSubmissionForm, MessageForm, ReplyMessageForm
from pfa_teams.models import Team, SubjectChoice
from django.utils import timezone
import xlsxwriter
from io import BytesIO
import json
from datetime import datetime, timedelta
from django.db.models import Count, Q
from users.models import User
import io
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

@login_required
def project_list(request):
    if request.user.role == 'teacher':
        # Les enseignants ne peuvent que voir leurs projets
        projects = Project.objects.filter(supervisor=request.user)
    elif request.user.role == 'admin':
        # L'administrateur peut tout voir et tout gérer
        projects = Project.objects.all()
    else:
        # Les étudiants voient tous les projets disponibles
        projects = Project.objects.filter(status='available')
    
    return render(request, 'pfa_projects/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Projet créé avec succès.')
            return redirect('pfa_projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'pfa_projects/project_form.html', {'form': form})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'student':
        # Les étudiants ne peuvent voir que les projets disponibles ou leurs projets assignés
        if project.status == 'available' or project.assigned_team.filter(members=request.user).exists():
            pass
        else:
            raise PermissionDenied
    elif request.user.role == 'teacher':
        # Les enseignants ne peuvent voir que leurs projets
        if project.supervisor != request.user:
            raise PermissionDenied
    
    context = {
        'project': project,
        'deadlines': project.deadlines.all().order_by('due_date'),
        'submissions': project.submissions.all().order_by('-submission_date'),
        'reports': project.reports.all().order_by('-submission_date'),
    }
    
    # Ajouter les équipes assignées si l'utilisateur a les permissions
    if request.user.role in ['teacher', 'admin'] or project.assigned_team.filter(members=request.user).exists():
        context['assigned_teams'] = project.assigned_team.all()
    
    return render(request, 'pfa_projects/project_detail.html', context)

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user.role != 'admin':
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projet mis à jour avec succès.')
            return redirect('pfa_projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'pfa_projects/project_form.html', {'form': form, 'project': project})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user.role != 'admin':
        raise PermissionDenied
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Projet supprimé avec succès.')
        return redirect('pfa_projects:project_list')
    
    return render(request, 'pfa_projects/project_confirm_delete.html', {'project': project})

@login_required
def submit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user.role != 'student':
        raise PermissionDenied
    
    # Vérifier si l'étudiant est membre d'une équipe assignée à ce projet
    team = None
    for assigned_team in project.assigned_team.all():
        if request.user in assigned_team.members.all():
            team = assigned_team
            break
    
    if not team:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.project = project
            submission.submitted_by = team
            submission.save()
            messages.success(request, 'Projet soumis avec succès.')
            return redirect('pfa_projects:project_detail', pk=pk)
    else:
        form = ProjectSubmissionForm()
    
    return render(request, 'pfa_projects/submit_project.html', {
        'form': form,
        'project': project,
        'team': team
    })

@login_required
def submit_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    team = request.user.teams.filter(project=project).first()
    
    if not team:
        messages.error(request, "Vous n'êtes pas membre d'une équipe pour ce projet.")
        return redirect('pfa_projects:project_detail', pk=project_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        document = request.FILES.get('document')
        
        if title and document:
            Report.objects.create(
                project=project,
                team=team,
                title=title,
                document=document
            )
            messages.success(request, 'Votre rapport a été soumis avec succès.')
            return redirect('pfa_projects:project_detail', pk=project_id)
        else:
            messages.error(request, 'Veuillez remplir tous les champs requis.')
    
    return render(request, 'pfa_projects/submit_report.html', {
        'project': project,
        'team': team
    })

@login_required
def review_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    if request.user.role not in ['teacher', 'admin']:
        raise PermissionDenied
    
    if request.user.role == 'teacher' and report.project.supervisor != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        status = request.POST.get('status')
        feedback = request.POST.get('feedback', '')
        
        if status in ['pending', 'reviewed', 'approved', 'rejected']:
            report.status = status
            report.feedback = feedback
            report.save()
            messages.success(request, 'Rapport mis à jour avec succès.')
            return redirect('pfa_projects:project_reports', pk=report.project.id)
    
    return render(request, 'pfa_projects/review_report.html', {'report': report})

@login_required
def manage_deadlines(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user != project.supervisor and request.user.role != 'admin':
        raise PermissionDenied
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        deadline_type = request.POST.get('deadline_type')
        
        deadline = Deadline.objects.create(
            project=project,
            title=title,
            description=description,
            due_date=datetime.strptime(due_date, '%Y-%m-%dT%H:%M'),
            deadline_type=deadline_type,
            created_by=request.user
        )
        
        # Notifier les étudiants
        teams = project.assigned_team.all()
        for team in teams:
            for student in team.members.all():
                Notification.objects.create(
                    user=student,
                    title=f"Nouvelle échéance : {title}",
                    message=f"Une nouvelle échéance a été ajoutée pour le projet {project.title}",
                    link=f"/projects/{project.id}/"
                )
        
        messages.success(request, 'Échéance ajoutée avec succès.')
        return redirect('pfa_projects:project_detail', pk=project_id)
    
    return render(request, 'pfa_projects/manage_deadlines.html', {
        'project': project,
        'deadlines': project.deadlines.all().order_by('due_date')
    })

@login_required
def calendar_view(request):
    if request.user.role == 'student':
        teams = request.user.teams.all()
        projects = Project.objects.filter(assigned_team__in=teams)
    elif request.user.role == 'teacher':
        projects = Project.objects.filter(supervisor=request.user)
    else:
        projects = Project.objects.all()
    
    deadlines = Deadline.objects.filter(project__in=projects).order_by('due_date')
    
    # Format pour le calendrier
    events = []
    for deadline in deadlines:
        events.append({
            'title': f"{deadline.title} - {deadline.project.title}",
            'start': deadline.due_date.isoformat(),
            'url': f"/projects/{deadline.project.id}/",
            'className': f"deadline-{deadline.deadline_type}"
        })
    
    return render(request, 'pfa_projects/calendar.html', {
        'events_json': json.dumps(events)
    })

@login_required
def notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
    
    return render(request, 'pfa_projects/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def export_project_stats(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user != project.supervisor and request.user.role != 'admin':
        raise PermissionDenied
    
    # Créer un fichier Excel en mémoire
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Styles
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4CAF50',
        'color': 'white',
        'align': 'center'
    })
    
    # En-têtes
    headers = ['Métrique', 'Valeur']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Données
    stats = project.statistics
    data = [
        ['Nombre total de rapports', stats.total_reports],
        ['Rapports approuvés', stats.approved_reports],
        ['Rapports rejetés', stats.rejected_reports],
        ['Taux de complétion', f"{stats.calculate_completion_rate():.2f}%"],
        ['Nombre d\'équipes', stats.team_count],
        ['Dernière activité', stats.last_activity.strftime('%d/%m/%Y %H:%M')]
    ]
    
    for row, (metric, value) in enumerate(data, start=1):
        worksheet.write(row, 0, metric)
        worksheet.write(row, 1, value)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=stats_{project.title}_{timezone.now().strftime("%Y%m%d")}.xlsx'
    
    return response

@login_required
def project_statistics(request):
    # Statistiques générales
    stats = {
        'total_projects': Project.objects.count(),
        'available_projects': Project.objects.filter(status='available').count(),
        'assigned_projects': Project.objects.filter(status='assigned').count(),
        'completed_projects': Project.objects.filter(status='completed').count(),
        'total_teams': Team.objects.count(),
        'pending_teams': Team.objects.filter(status='pending').count(),
        'approved_teams': Team.objects.filter(status='approved').count(),
    }
    
    # Statistiques par département
    department_stats = User.objects.filter(role='student').values('department').annotate(
        total_students=Count('id'),
        with_team=Count('teams'),
        without_team=Count('id', filter=Q(teams=None))
    )
    
    # Statistiques des soumissions
    submission_stats = ProjectSubmission.objects.values('status').annotate(
        count=Count('id')
    )
    
    return render(request, 'pfa_projects/statistics.html', {
        'stats': stats,
        'department_stats': department_stats,
        'submission_stats': submission_stats
    })

@login_required
def export_statistics(request):
    # Créer un buffer en mémoire pour le fichier Excel
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1
    })
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Feuille des statistiques générales
    ws_general = workbook.add_worksheet('Statistiques Générales')
    general_data = [
        ['Projets total', Project.objects.count()],
        ['Projets disponibles', Project.objects.filter(status='available').count()],
        ['Projets assignés', Project.objects.filter(status='assigned').count()],
        ['Projets terminés', Project.objects.filter(status='completed').count()],
        ['Équipes total', Team.objects.count()],
        ['Équipes en attente', Team.objects.filter(status='pending').count()],
        ['Équipes approuvées', Team.objects.filter(status='approved').count()],
    ]
    
    ws_general.write_row(0, 0, ['Métrique', 'Valeur'], header_format)
    for i, row in enumerate(general_data, 1):
        ws_general.write_row(i, 0, row, cell_format)
    
    # Feuille des statistiques par département
    ws_dept = workbook.add_worksheet('Par Département')
    dept_headers = ['Département', 'Total Étudiants', 'Avec Équipe', 'Sans Équipe']
    ws_dept.write_row(0, 0, dept_headers, header_format)
    
    dept_stats = User.objects.filter(role='student').values('department').annotate(
        total=Count('id'),
        with_team=Count('teams'),
        without_team=Count('id', filter=Q(teams=None))
    )
    
    for i, dept in enumerate(dept_stats, 1):
        row = [
            dept['department'],
            dept['total'],
            dept['with_team'],
            dept['without_team']
        ]
        ws_dept.write_row(i, 0, row, cell_format)
    
    # Feuille des projets
    ws_projects = workbook.add_worksheet('Projets')
    project_headers = ['Titre', 'Superviseur', 'Status', 'Équipe', 'Date de création']
    ws_projects.write_row(0, 0, project_headers, header_format)
    
    projects = Project.objects.select_related('supervisor').prefetch_related('assigned_team')
    for i, project in enumerate(projects, 1):
        team = project.assigned_team.first()
        row = [
            project.title,
            project.supervisor.get_full_name(),
            project.get_status_display(),
            team.name if team else 'Non assigné',
            project.created_at.strftime('%d/%m/%Y')
        ]
        ws_projects.write_row(i, 0, row, cell_format)
    
    # Feuille des soumissions
    ws_submissions = workbook.add_worksheet('Soumissions')
    submission_headers = ['Projet', 'Équipe', 'Type', 'Status', 'Date']
    ws_submissions.write_row(0, 0, submission_headers, header_format)
    
    submissions = ProjectSubmission.objects.select_related('project', 'team')
    for i, submission in enumerate(submissions, 1):
        row = [
            submission.project.title,
            submission.team.name,
            submission.get_submission_type_display(),
            submission.get_status_display(),
            submission.submission_date.strftime('%d/%m/%Y')
        ]
        ws_submissions.write_row(i, 0, row, cell_format)
    
    # Ajuster la largeur des colonnes
    for ws in [ws_general, ws_dept, ws_projects, ws_submissions]:
        ws.autofit()
    
    # Fermer le workbook et préparer le fichier pour le téléchargement
    workbook.close()
    output.seek(0)
    
    # Créer la réponse HTTP avec le fichier Excel
    filename = f'statistiques_pfa_{timezone.now().strftime("%Y%m%d")}.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@login_required
def project_teams(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user.role not in ['teacher', 'admin']:
        raise PermissionDenied
    
    if request.user.role == 'teacher' and project.supervisor != request.user:
        raise PermissionDenied
    
    teams = project.assigned_team.all()
    
    return render(request, 'pfa_projects/project_teams.html', {
        'project': project,
        'teams': teams
    })

@login_required
def project_reports(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user.role == 'student':
        # Vérifier si l'étudiant est membre d'une équipe assignée
        if not project.assigned_team.filter(members=request.user).exists():
            raise PermissionDenied
    elif request.user.role == 'teacher':
        # Vérifier si l'enseignant supervise ce projet
        if project.supervisor != request.user:
            raise PermissionDenied
    
    reports = project.reports.all().order_by('-submission_date')
    
    # Ajouter des informations sur les rapports automatiquement classés
    for report in reports:
        # Vérifier si ce rapport provient d'un message automatiquement classé
        auto_message = Message.objects.filter(
            auto_classified_as_report=True,
            attachment=report.document
        ).first()
        
        if auto_message:
            report.is_auto_classified = True
            report.original_message = auto_message
        else:
            report.is_auto_classified = False
    
    return render(request, 'pfa_projects/project_reports.html', {
        'project': project,
        'reports': reports
    })

@login_required
def view_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Vérifier les permissions
    if request.user.role == 'student':
        if request.user not in report.team.members.all():
            raise PermissionDenied
    elif request.user.role == 'teacher':
        if report.project.supervisor != request.user:
            raise PermissionDenied
    
    return render(request, 'pfa_projects/view_report.html', {'report': report})

@login_required
def delay_notifications(request):
    """Vue pour afficher les notifications de retard pour les étudiants"""
    if request.user.role != 'student':
        raise PermissionDenied
    
    # Récupérer les notifications de retard pour les équipes de l'étudiant
    user_teams = request.user.pfa_teams.all()
    delay_notifications = DelayNotification.objects.filter(
        team__in=user_teams
    ).order_by('-sent_at')
    
    unread_count = delay_notifications.filter(is_read=False).count()
    
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        action = request.POST.get('action')
        
        if notification_id:
            notification = get_object_or_404(DelayNotification, id=notification_id, team__in=user_teams)
            
            if action == 'mark_read':
                notification.is_read = True
                notification.save()
            elif action == 'mark_resolved':
                notification.is_read = True
                notification.is_resolved = True
                notification.resolved_at = timezone.now()
                notification.save()
            
            return JsonResponse({'status': 'success'})
    
    return render(request, 'pfa_projects/delay_notifications.html', {
        'delay_notifications': delay_notifications,
        'unread_count': unread_count
    })

@login_required
def send_delay_notification(request):
    """Vue pour que l'admin puisse envoyer des notifications de retard"""
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            team_id = data.get('team_id')
            delay_type = data.get('delay_type')
            priority = data.get('priority', 'medium')
            title = data.get('title')
            message = data.get('message')
            deadline_date = data.get('deadline_date')
            days_late = data.get('days_late', 0)
            
            team = get_object_or_404(Team, id=team_id)
            
            # Créer la notification de retard
            delay_notification = DelayNotification.objects.create(
                project=team.project,
                team=team,
                delay_type=delay_type,
                priority=priority,
                title=title,
                message=message,
                deadline_date=datetime.fromisoformat(deadline_date.replace('Z', '+00:00')),
                days_late=days_late,
                sent_by=request.user
            )
            
            # Envoyer un email aux membres de l'équipe
            for member in team.members.all():
                subject = f"Notification de retard - {title}"
                email_message = f"""
                Bonjour {member.get_full_name()},
                
                {message}
                
                Projet : {team.project.title}
                Équipe : {team.name}
                Date limite : {deadline_date}
                Jours de retard : {days_late}
                
                Veuillez prendre les mesures nécessaires pour respecter les échéances.
                
                Cordialement,
                L'équipe administrative
                """
                
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [member.email],
                    fail_silently=False,
                )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
def manage_delay_notifications(request):
    """Vue pour que l'admin puisse gérer les notifications de retard"""
    if request.user.role != 'admin':
        raise PermissionDenied
    
    # Récupérer toutes les équipes avec leurs projets
    teams = Team.objects.filter(status='approved').select_related('project')
    
    # Calculer les retards potentiels
    today = timezone.now()
    teams_with_delays = []
    
    for team in teams:
        project = team.project
        deadlines = project.deadlines.all()
        
        for deadline in deadlines:
            if deadline.due_date < today:
                days_late = (today - deadline.due_date).days
                teams_with_delays.append({
                    'team': team,
                    'deadline': deadline,
                    'days_late': days_late,
                    'has_notification': DelayNotification.objects.filter(
                        team=team,
                        deadline_date=deadline.due_date
                    ).exists()
                })
    
    return render(request, 'pfa_projects/manage_delay_notifications.html', {
        'teams_with_delays': teams_with_delays
    })

# Vues pour la messagerie
@login_required
def inbox(request):
    """Vue pour afficher la boîte de réception"""
    received_messages = request.user.received_project_messages.all().order_by('-sent_at')
    unread_count = received_messages.filter(is_read=False).count()
    
    return render(request, 'pfa_projects/inbox.html', {
        'messages': received_messages,
        'unread_count': unread_count
    })

@login_required
def sent_messages(request):
    """Vue pour afficher les messages envoyés"""
    sent_messages = request.user.sent_project_messages.all().order_by('-sent_at')
    
    return render(request, 'pfa_projects/sent_messages.html', {
        'messages': sent_messages
    })

@login_required
def compose_message(request):
    """Vue pour composer un nouveau message"""
    if request.method == 'POST':
        print("=== DÉBOGAGE COMPOSE MESSAGE ===")
        print(f"Données POST: {request.POST}")
        print(f"Fichiers: {request.FILES}")
        
        form = MessageForm(request.POST, request.FILES, sender=request.user)
        print(f"Formulaire valide: {form.is_valid()}")
        
        if form.is_valid():
            print("✅ Formulaire valide - Sauvegarde du message...")
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            print(f"✅ Message sauvegardé avec ID: {message.id}")
            
            # Classification automatique des rapports PDF
            try:
                auto_report = message.auto_classify_as_report()
                if auto_report:
                    print(f"✅ Rapport automatiquement classé: {auto_report.title}")
                    messages.success(request, f'Message envoyé et rapport automatiquement classé: {auto_report.title}')
                else:
                    messages.success(request, 'Message envoyé avec succès.')
            except Exception as e:
                print(f"⚠️ Erreur classification automatique: {e}")
                messages.success(request, 'Message envoyé avec succès.')
            
            # Envoyer un email de notification
            try:
                subject = f"Nouveau message : {message.subject}"
                email_content = f"""
                Bonjour {message.recipient.get_full_name()},
                
                Vous avez reçu un nouveau message de {message.sender.get_full_name()}.
                
                Sujet : {message.subject}
                Contenu : {message.content}
                
                Connectez-vous à la plateforme pour répondre.
                
                Cordialement,
                L'équipe PFA
                """
                
                send_mail(
                    subject,
                    email_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [message.recipient.email],
                    fail_silently=True,
                )
                print("✅ Email de notification envoyé")
            except Exception as e:
                print(f"⚠️ Erreur email: {e}")
                # En cas d'erreur d'envoi d'email, on continue
                pass
            
            print("✅ Redirection vers inbox...")
            return redirect('pfa_projects:inbox')
        else:
            print("❌ Formulaire invalide")
            print(f"Erreurs: {form.errors}")
            # Afficher les erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    error_msg = f"Erreur dans {field}: {error}"
                    print(f"❌ {error_msg}")
                    messages.error(request, error_msg)
    else:
        form = MessageForm(sender=request.user)
    
    return render(request, 'pfa_projects/compose_message.html', {
        'form': form
    })

@login_required
def view_message(request, message_id):
    """Vue pour afficher un message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur est le destinataire ou l'expéditeur
    if message.recipient != request.user and message.sender != request.user:
        raise PermissionDenied
    
    # Marquer comme lu si l'utilisateur est le destinataire
    if message.recipient == request.user and not message.is_read:
        message.mark_as_read()
    
    # Formulaire de réponse
    if request.method == 'POST':
        reply_form = ReplyMessageForm(request.POST, request.FILES)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.sender = request.user
            reply.recipient = message.sender
            reply.subject = f"Re: {message.subject}"
            reply.project = message.project
            
            # Déterminer le type de message
            if request.user.role == 'student':
                reply.message_type = 'student_to_teacher'
            elif request.user.role == 'teacher':
                reply.message_type = 'teacher_to_student'
            else:
                reply.message_type = 'admin_to_all'
            
            reply.save()
            
            messages.success(request, 'Réponse envoyée avec succès.')
            return redirect('pfa_projects:view_message', message_id=message_id)
    else:
        reply_form = ReplyMessageForm()
    
    return render(request, 'pfa_projects/view_message.html', {
        'message': message,
        'reply_form': reply_form
    })

@login_required
def delete_message(request, message_id):
    """Vue pour supprimer un message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Vérifier que l'utilisateur est le destinataire ou l'expéditeur
    if message.recipient != request.user and message.sender != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message supprimé avec succès.')
        return redirect('pfa_projects:inbox')
    
    return render(request, 'pfa_projects/delete_message.html', {
        'message': message
    })

@login_required
def mark_message_read(request, message_id):
    """Vue pour marquer un message comme lu"""
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    
    if request.method == 'POST':
        message.mark_as_read()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})
