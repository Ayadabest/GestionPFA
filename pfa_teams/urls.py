from django.urls import path
from . import views

app_name = 'pfa_teams'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.team_create, name='team_create'),
    path('send-request/', views.send_team_request, name='send_request'),
    path('send-request/project/<int:project_id>/', views.send_team_request, name='send_request_project'),
    path('handle-request/<int:request_id>/', views.handle_team_request, name='handle_request'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:team_id>/submit-choices/', views.submit_subject_choices, name='submit_choices'),
    path('<int:team_id>/approve-subject/', views.approve_subject_choice, name='approve_subject_choice'),
    path('<int:team_id>/approve/', views.approve_team, name='approve_team'),
    path('<int:team_id>/submit-report/', views.submit_report, name='submit_report'),
    path('<int:team_id>/reports/', views.team_reports, name='team_reports'),
    path('<int:team_id>/messages/', views.team_messages, name='team_messages'),
    path('<int:team_id>/send-message/', views.send_message, name='send_message'),
] 