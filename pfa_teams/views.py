from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Team, TeamRequest, Message, SubjectChoice, TeamHistory, Report
from .forms import TeamForm, TeamRequestForm, MessageForm, ReportForm
from users.models import User
from pfa_projects.models import Project
from django.http import HttpResponseForbidden
from django.urls import reverse

def is_admin(user):
    return user.role == 'admin'

@login_required
def team_list(request):
    project_id = request.GET.get('project_id')
    if request.user.role == 'student':
        teams = Team.objects.filter(members=request.user)
    elif request.user.role == 'admin':
        teams = Team.objects.all()
    elif request.user.role == 'teacher' and project_id:
        teams = Team.objects.filter(project__supervisor=request.user, project_id=project_id)
    else:  # teacher
        teams = Team.objects.filter(project__supervisor=request.user)
    context = {
        'teams': teams,
        'is_admin': request.user.role == 'admin'
    }
    return render(request, 'pfa_teams/team_list.html', context)

@login_required
def team_create(request):
    if request.user.role != 'student':
        raise PermissionDenied
    
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            team.members.add(request.user)
            
            project_id = request.POST.get('project')
            if project_id:
                project = get_object_or_404(Project, pk=project_id)
                team.project = project
                team.save()
            
            messages.success(request, 'Équipe créée avec succès.')
            return redirect('pfa_teams:team_detail', pk=team.pk)
    else:
        form = TeamForm()
    
    available_projects = Project.objects.filter(status='available')
    return render(request, 'pfa_teams/team_form.html', {
        'form': form,
        'projects': available_projects
    })

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Vérifier les permissions
    if request.user.role == 'student' and request.user not in team.members.all():
        raise PermissionDenied
    
    history = team.history.all()
    subject_choices = team.subjectchoice_set.all().order_by('priority')
    
    return render(request, 'pfa_teams/team_detail.html', {
        'team': team,
        'history': history,
        'subject_choices': subject_choices
    })

@login_required
def send_team_request(request, project_id=None):
    if request.user.role != 'student':
        messages.error(request, 'Seuls les étudiants peuvent envoyer des demandes de binôme.')
        raise PermissionDenied
    
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        message = request.POST.get('message')
        
        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)
            
            # Debug logs détaillés
            print("=== Détails de la demande ===")
            print(f"Sender: {request.user.username} (ID: {request.user.id})")
            print(f"Receiver: {receiver.username} (ID: {receiver.id})")
            print(f"Message: {message}")
            print(f"Project: {project.title if project else 'Aucun'}")
            
            # Vérifier si une demande existe déjà
            existing_request = TeamRequest.objects.filter(
                Q(sender=request.user, receiver=receiver) |
                Q(sender=receiver, receiver=request.user)
            ).first()
            
            if existing_request:
                print(f"Demande existante trouvée : ID={existing_request.id}, Status={existing_request.status}")
                messages.error(request, 'Une demande existe déjà avec cet étudiant.')
            else:
                try:
                    # Créer la nouvelle demande
                    new_request = TeamRequest.objects.create(
                        sender=request.user,
                        receiver=receiver,
                        message=message or '',
                        project=project,
                        status='pending'  # Explicitement définir le statut
                    )
                    print(f"Nouvelle demande créée avec succès : ID={new_request.id}, Status={new_request.status}")
                    
                    # Vérifier que la demande est bien dans la base de données
                    verification = TeamRequest.objects.get(id=new_request.id)
                    print(f"Vérification - Demande en base : ID={verification.id}, Status={verification.status}")
                    
                    messages.success(request, 'Demande de binôme envoyée avec succès.')
                except Exception as e:
                    print(f"Erreur lors de la création de la demande : {str(e)}")
                    messages.error(request, 'Erreur lors de l\'envoi de la demande.')
            
            return redirect('pfa_teams:team_list')
    
    # Récupérer tous les étudiants sauf l'utilisateur actuel
    available_students = User.objects.filter(role='student').exclude(id=request.user.id)
    
    print("=== Étudiants disponibles ===")
    for student in available_students:
        print(f"- {student.username} (ID: {student.id})")
    
    return render(request, 'pfa_teams/send_request.html', {
        'available_students': available_students,
        'project': project
    })

@login_required
def handle_team_request(request, request_id):
    print("\n=== Debug handle_team_request ===")
    print(f"User: {request.user.username} (Role: {request.user.role})")
    
    # Permettre à l'admin ou au destinataire de gérer la demande
    if request.user.role == 'admin':
        team_request = get_object_or_404(TeamRequest, id=request_id)
        print("Accès en tant qu'admin")
    else:
        team_request = get_object_or_404(TeamRequest, id=request_id, receiver=request.user)
        print("Accès en tant que destinataire")
    
    # Forcer la récupération de tous les projets disponibles
    available_projects = list(Project.objects.filter(status='available').select_related('supervisor'))
    
    print(f"\nProjets disponibles ({len(available_projects)}):")
    for project in available_projects:
        print(f"- {project.title} (ID: {project.id}, Superviseur: {project.supervisor.get_full_name()})")
    
    if request.method == 'POST':
        action = request.POST.get('action')
        project_id = request.POST.get('project')
        print(f"\nAction demandée : {action}")
        print(f"Projet sélectionné : {project_id}")
        
        if action == 'accept':
            # Vérifier si l'un des étudiants a déjà une équipe
            sender_has_team = Team.objects.filter(members=team_request.sender).exists()
            receiver_has_team = Team.objects.filter(members=team_request.receiver).exists()
            
            if sender_has_team or receiver_has_team:
                messages.error(request, 'Un des étudiants fait déjà partie d\'une équipe.')
                return redirect('users:dashboard')
            
            # Vérifier si un projet a été sélectionné
            if not project_id and not team_request.project:
                messages.error(request, 'Veuillez sélectionner un projet pour l\'équipe.')
                return render(request, 'pfa_teams/handle_request.html', {
                    'team_request': team_request,
                    'available_projects': available_projects
                })
            
            try:
                # Récupérer le projet sélectionné ou utiliser celui de la demande
                project = None
                if project_id:
                    project = get_object_or_404(Project, id=project_id)
                else:
                    project = team_request.project
                
                # Créer une nouvelle équipe
                team = Team.objects.create(
                    name=f"Équipe {team_request.sender.get_full_name()} et {team_request.receiver.get_full_name()}",
                    project=project
                )
                team.members.add(team_request.sender, team_request.receiver)
                
                # Créer l'historique
                TeamHistory.objects.create(
                    team=team,
                    action='created',
                    details='Équipe créée suite à une demande de binôme',
                    performed_by=request.user
                )
                
                # Mettre à jour le statut du projet
                project.status = 'assigned'
                project.save()
                
                team_request.status = 'accepted'
                team_request.save()
                
                messages.success(request, 'Demande de binôme acceptée et équipe créée.')
                
                if request.user.role == 'admin':
                    return redirect('users:dashboard')
                return redirect('pfa_teams:team_list')
                
            except Exception as e:
                print(f"Erreur lors de la création de l'équipe : {str(e)}")
                messages.error(request, f'Erreur lors de la création de l\'équipe : {str(e)}')
        
        elif action == 'reject':
            team_request.status = 'rejected'
            team_request.save()
            messages.success(request, 'Demande de binôme refusée.')
            
            if request.user.role == 'admin':
                return redirect('users:dashboard')
            return redirect('pfa_teams:team_list')
    
    # Forcer l'évaluation du queryset avant de le passer au template
    context = {
        'team_request': team_request,
        'available_projects': list(available_projects),  # Forcer l'évaluation du queryset
    }
    
    print("\nContext passé au template:")
    print(f"- team_request: {team_request}")
    print(f"- available_projects: {[p.title for p in available_projects]}")
    
    response = render(request, 'pfa_teams/handle_request.html', context)
    print("\nRéponse générée avec succès")
    return response

@login_required
def submit_subject_choices(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Vérifier que l'utilisateur est membre de l'équipe
    if request.user not in team.members.all():
        raise PermissionDenied
    
    if request.method == 'POST':
        # Supprimer les anciens choix
        team.subjectchoice_set.all().delete()
        
        # Enregistrer les nouveaux choix
        for i in range(1, 4):  # 3 choix maximum
            project_id = request.POST.get(f'choice_{i}')
            motivation = request.POST.get(f'motivation_{i}')
            
            if project_id:
                project = get_object_or_404(Project, id=project_id)
                SubjectChoice.objects.create(
                    team=team,
                    project=project,
                    priority=i,
                    motivation=motivation
                )
        
        # Créer l'historique
        TeamHistory.objects.create(
            team=team,
            action='subject_choice',
            details='Soumission des choix de sujets',
            performed_by=request.user
        )
        
        messages.success(request, 'Vos choix de sujets ont été enregistrés.')
        return redirect('pfa_teams:team_detail', team_id=team.id)
    
    # Récupérer les projets disponibles
    available_projects = Project.objects.filter(status='available')
    current_choices = team.subjectchoice_set.all().order_by('priority')
    
    return render(request, 'pfa_teams/submit_choices.html', {
        'team': team,
        'available_projects': available_projects,
        'current_choices': current_choices
    })

@login_required
def approve_subject_choice(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Vérifier que l'utilisateur est administrateur
    if request.user.role != 'admin':
        raise PermissionDenied
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        action = request.POST.get('action')
        
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            
            if action == 'approve':
                # Assigner le projet à l'équipe
                team.project = project
                team.status = 'approved'
                team.save()
                
                # Mettre à jour le statut du projet
                project.status = 'assigned'
                project.save()
                
                # Créer l'historique
                TeamHistory.objects.create(
                    team=team,
                    action='subject_approved',
                    details=f'Sujet "{project.title}" approuvé',
                    performed_by=request.user
                )
                
                messages.success(request, 'Sujet approuvé et assigné à l\'équipe.')
            
            elif action == 'reject':
                TeamHistory.objects.create(
                    team=team,
                    action='subject_rejected',
                    details=f'Sujet "{project.title}" rejeté',
                    performed_by=request.user
                )
                messages.success(request, 'Sujet rejeté.')
        
        return redirect('pfa_teams:team_detail', team_id=team.id)
    
    return render(request, 'pfa_teams/approve_subject.html', {
        'team': team,
        'choices': team.subjectchoice_set.all().order_by('priority')
    })

@login_required
def send_message(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all() and request.user != team.supervisor:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à envoyer des messages.")

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.team = team
            message.sender = request.user
            message.save()
            messages.success(request, 'Message envoyé!')
            return redirect('team_messages', team_id=team.id)
    else:
        form = MessageForm()

    return render(request, 'pfa_teams/send_message.html', {
        'form': form,
        'team': team
    })

@login_required
def team_messages(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all() and request.user != team.supervisor:
        return HttpResponseForbidden("Accès non autorisé.")

    messages_list = team.messages.all()
    
    # Marquer les messages comme lus
    if request.user != team.supervisor:
        unread_messages = messages_list.filter(read=False, sender=team.supervisor)
    else:
        unread_messages = messages_list.filter(read=False).exclude(sender=request.user)
    
    unread_messages.update(read=True)

    return render(request, 'pfa_teams/team_messages.html', {
        'team': team,
        'messages': messages_list,
        'message_form': MessageForm()
    })

@login_required
@user_passes_test(is_admin)
def approve_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Si l'équipe a déjà un projet assigné
            if team.project:
                team.status = 'approved'
                team.project.status = 'assigned'
                team.project.save()
                team.save()
                messages.success(request, f'L\'équipe {team.name} a été approuvée.')
            else:
                messages.error(request, 'Veuillez d\'abord assigner un projet à l\'équipe.')
                return redirect('pfa_teams:team_detail', team_id=team_id)
                
        elif action == 'reject':
            team.status = 'rejected'
            if team.project:
                team.project.status = 'available'
                team.project.save()
            team.save()
            messages.warning(request, f'L\'équipe {team.name} a été rejetée.')
        
        return redirect('pfa_teams:team_list')
    
    # Pour l'affichage du formulaire
    context = {
        'team': team,
        'available_projects': Project.objects.filter(status='available')
    }
    return render(request, 'pfa_teams/team_detail.html', context)

@login_required
def submit_report(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all():
        return HttpResponseForbidden("Vous n'êtes pas membre de cette équipe.")

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.team = team
            report.submitted_by = request.user
            report.save()
            messages.success(request, 'Rapport soumis avec succès!')
            return redirect('team_detail', team_id=team.id)
    else:
        form = ReportForm()

    return render(request, 'pfa_teams/submit_report.html', {
        'form': form,
        'team': team
    })

@login_required
def team_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all() and not request.user.is_staff:
        return HttpResponseForbidden("Accès non autorisé.")

    reports = team.reports.all().order_by('-submitted_at')
    return render(request, 'pfa_teams/team_reports.html', {
        'team': team,
        'reports': reports
    })
