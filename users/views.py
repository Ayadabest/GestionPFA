from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from .models import User, StudentProfile
from .forms import StudentRegistrationForm, StudentProfileForm, UserProfileForm, TeacherRegistrationForm
from pfa_teams.models import Team, TeamRequest
from pfa_projects.models import Project, ProjectSubmission, Message
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    context = {}
    logger.debug(f"User role: {request.user.role}")
    logger.debug(f"User is_superuser: {request.user.is_superuser}")
    logger.debug(f"User is_staff: {request.user.is_staff}")
    
    if request.user.role == 'student':
        # Vérifier et créer un profil étudiant si nécessaire
        try:
            student_profile = request.user.studentprofile
        except StudentProfile.DoesNotExist:
            student_profile = StudentProfile.objects.create(
                user=request.user,
                student_id=f"STU{request.user.id:03d}",
                department='Informatique',
                level='Master 2'
            )
            messages.info(request, 'Un profil étudiant a été créé pour vous. Veuillez le mettre à jour dans la section profil.')

        # Vue étudiant
        user_teams = Team.objects.filter(members=request.user)
        context['teams'] = user_teams
        context['available_projects'] = Project.objects.filter(status='available')

        # Récupérer les étudiants disponibles (sans équipe et dans le même département)
        students_with_teams = Team.objects.values_list('members', flat=True)
        available_students = User.objects.filter(
            role='student',
            studentprofile__department=student_profile.department
        ).exclude(
            id__in=students_with_teams
        ).exclude(
            id=request.user.id
        ).select_related('studentprofile')
        context['available_students'] = available_students

        # Récupérer les demandes de binôme reçues
        context['received_requests'] = TeamRequest.objects.filter(
            receiver=request.user,
            status='pending'
        ).select_related('sender')

        # Données de messagerie
        recent_messages = request.user.received_project_messages.all().order_by('-sent_at')[:5]
        context['recent_messages'] = recent_messages
        context['unread_messages_count'] = request.user.received_project_messages.filter(is_read=False).count()

    elif request.user.role == 'teacher':
        # Vue enseignant
        supervised_projects = Project.objects.filter(supervisor=request.user)
        context['supervised_projects'] = supervised_projects
        
        # Équipes en attente d'approbation pour les projets supervisés
        pending_teams = Team.objects.filter(
            project__in=supervised_projects,
            status='pending'
        ).select_related('project')
        context['pending_teams'] = pending_teams
        
        # Rapports récents
        context['recent_reports'] = ProjectSubmission.objects.filter(
            project__in=supervised_projects
        ).order_by('-submission_date')[:5]
        
        # Données de messagerie
        recent_messages = request.user.received_project_messages.all().order_by('-sent_at')[:5]
        context['recent_messages'] = recent_messages
        context['unread_messages_count'] = request.user.received_project_messages.filter(is_read=False).count()
        
        # Statistiques
        context['stats'] = {
            'total_projects': supervised_projects.count(),
            'pending_teams_count': pending_teams.count(),
            'active_teams': Team.objects.filter(
                project__in=supervised_projects,
                status='approved'
            ).count(),
        }

    elif request.user.role == 'admin' or request.user.is_superuser:
        # Vue administrateur
        projects = Project.objects.all()
        teams = Team.objects.all()
        context['projects'] = projects
        context['teams'] = teams
        
        # Récupérer toutes les demandes d'équipe en attente
        pending_team_requests = TeamRequest.objects.filter(status='pending').select_related('sender', 'receiver', 'project')
        context['pending_team_requests'] = pending_team_requests
        
        # Statistiques des étudiants
        total_students = User.objects.filter(role='student').count()
        logger.debug(f"Total students: {total_students}")
        
        # Étudiants avec demandes acceptées (dans une équipe)
        students_in_teams = Team.objects.filter(status='approved').values_list('members', flat=True).distinct()
        students_accepted = User.objects.filter(id__in=students_in_teams).count()
        logger.debug(f"Students with accepted requests: {students_accepted}")
        
        # Étudiants avec demandes en attente
        students_with_pending_requests = User.objects.filter(
            Q(sent_requests__status='pending') | 
            Q(received_requests__status='pending')
        ).distinct()
        students_pending = students_with_pending_requests.count()
        logger.debug(f"Students with pending requests: {students_pending}")
        
        # Étudiants sans aucune demande
        students_without_requests = User.objects.filter(
            role='student'
        ).exclude(
            id__in=students_in_teams
        ).exclude(
            id__in=students_with_pending_requests
        ).select_related('studentprofile')
        
        students_without_requests_count = students_without_requests.count()
        logger.debug(f"Students without requests: {students_without_requests_count}")
        
        # Ajouter la liste des étudiants sans demande au contexte
        context['students_without_requests'] = students_without_requests
        
        # Données de messagerie
        recent_messages = request.user.received_project_messages.all().order_by('-sent_at')[:5]
        context['recent_messages'] = recent_messages
        context['unread_messages_count'] = request.user.received_project_messages.filter(is_read=False).count()
        
        # Statistiques globales
        stats = {
            'total_students': total_students,
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_teams': teams.count(),
            'total_projects': projects.count(),
            'pending_requests': pending_team_requests.count(),
            'students_accepted': students_accepted,
            'students_pending': students_pending,
            'students_without_requests': students_without_requests_count
        }
        context['stats'] = stats
        
        # Log des statistiques finales
        logger.debug(f"Final stats for chart: {stats}")
    else:
        logger.warning(f"User {request.user.username} with role {request.user.role} tried to access admin dashboard")
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('users:dashboard')
    
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('users:dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {
        'user': request.user,
        'form': form
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.get_full_name()}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {
        'form': form,
        'title': 'Connexion'
    })

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('users:login')
    
    return render(request, 'users/logout.html', {
        'title': 'Déconnexion'
    })

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Compte créé avec succès! Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Compte professeur créé avec succès! Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'users/register_teacher.html', {'form': form})

@login_required
def approve_team(request, team_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Vous n\'avez pas la permission d\'effectuer cette action.')
        return redirect('users:dashboard')
    
    team = get_object_or_404(Team, id=team_id)
    
    # Vérifier que l'enseignant est bien le superviseur du projet
    if team.project.supervisor != request.user:
        messages.error(request, 'Vous n\'êtes pas le superviseur de ce projet.')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            team.status = 'approved'
            messages.success(request, f'L\'équipe {team.name} a été approuvée.')
        elif action == 'reject':
            team.status = 'rejected'
            messages.success(request, f'L\'équipe {team.name} a été refusée.')
        team.save()
    
    return redirect('users:dashboard')

@require_POST
def send_notification(request):
    logger.debug(f"Notification request from user: {request.user.username} (role: {request.user.role})")
    
    if not request.user.role == 'admin':
        logger.warning(f"Permission denied for user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        data = json.loads(request.body)
        notification_type = data.get('type')
        logger.debug(f"Notification data: {data}")
        
        if notification_type == 'team':
            student = User.objects.get(id=data.get('student_id'))
            subject = 'Rappel : Formation des binômes PFA'
            message = f"""
            Bonjour {student.get_full_name()},
            
            Nous vous rappelons que vous n'avez pas encore formé votre binôme pour le projet PFA.
            Veuillez vous connecter à la plateforme pour choisir votre partenaire dès que possible.
            
            Cordialement,
            L'équipe administrative
            """
            recipient = student.email
            
        elif notification_type == 'project':
            team = Team.objects.get(id=data.get('team_id'))
            subject = 'Rappel : Choix du projet PFA'
            message = f"""
            Bonjour {', '.join(member.get_full_name() for member in team.members.all())},
            
            Nous vous rappelons que votre binôme n'a pas encore choisi de projet PFA.
            Veuillez vous connecter à la plateforme pour faire votre choix dès que possible.
            
            Cordialement,
            L'équipe administrative
            """
            recipient = [member.email for member in team.members.all()]
        else:
            logger.error(f"Invalid notification type: {notification_type}")
            return JsonResponse({'success': False, 'error': 'Type de notification invalide'})
        
        if not recipient:
            logger.error("No recipients found")
            return JsonResponse({'success': False, 'error': 'Aucun destinataire trouvé'})
        
        logger.debug(f"Sending email to: {recipient}")
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient if isinstance(recipient, list) else [recipient],
            fail_silently=False,
        )
        
        logger.debug("Email sent successfully")
        return JsonResponse({'success': True})
        
    except User.DoesNotExist:
        logger.error(f"User not found: {data.get('student_id')}")
        return JsonResponse({'success': False, 'error': 'Utilisateur non trouvé'})
    except Team.DoesNotExist:
        logger.error(f"Team not found: {data.get('team_id')}")
        return JsonResponse({'success': False, 'error': 'Équipe non trouvée'})
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
