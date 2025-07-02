from django.urls import path
from . import views

app_name = 'pfa_projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/submit/', views.submit_project, name='submit_project'),
    path('statistics/', views.project_statistics, name='statistics'),
    path('statistics/export/', views.export_statistics, name='export_statistics'),
    path('<int:project_id>/submit-report/', views.submit_report, name='submit_report'),
    path('report/<int:report_id>/review/', views.review_report, name='review_report'),
    path('<int:project_id>/deadlines/', views.manage_deadlines, name='manage_deadlines'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('notifications/', views.notifications, name='notifications'),
    path('<int:project_id>/stats/export/', views.export_project_stats, name='export_stats'),
    path('project/<int:pk>/teams/', views.project_teams, name='project_teams'),
    path('project/<int:pk>/reports/', views.project_reports, name='project_reports'),
    path('report/<int:report_id>/', views.view_report, name='view_report'),
    path('delay-notifications/', views.delay_notifications, name='delay_notifications'),
    path('send-delay-notification/', views.send_delay_notification, name='send_delay_notification'),
    path('manage-delay-notifications/', views.manage_delay_notifications, name='manage_delay_notifications'),
    
    # URLs pour la messagerie
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/compose/', views.compose_message, name='compose_message'),
    path('messages/<int:message_id>/', views.view_message, name='view_message'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('messages/<int:message_id>/mark-read/', views.mark_message_read, name='mark_message_read'),
] 