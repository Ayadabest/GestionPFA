from django.contrib import admin
from .models import Project, ProjectSubmission, Deadline, Notification, ProjectStatistics, Report, ProjectReport, DelayNotification, Message

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'supervisor', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'supervisor', 'created_at')
    search_fields = ('title', 'description', 'supervisor__username')
    date_hierarchy = 'created_at'

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ('project', 'submitted_by', 'submission_date')
    list_filter = ('submission_date', 'project__supervisor')
    search_fields = ('project__title', 'submitted_by__name')

@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'deadline_type', 'due_date', 'created_by')
    list_filter = ('deadline_type', 'due_date', 'project__supervisor')
    search_fields = ('title', 'project__title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'user__role')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(DelayNotification)
class DelayNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'team', 'delay_type', 'priority', 'days_late', 'sent_by', 'is_read', 'is_resolved', 'sent_at')
    list_filter = ('delay_type', 'priority', 'is_read', 'is_resolved', 'sent_at', 'project__supervisor')
    search_fields = ('title', 'message', 'project__title', 'team__name', 'sent_by__username')
    date_hierarchy = 'sent_at'
    readonly_fields = ('days_late', 'sent_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('project', 'team', 'delay_type', 'priority')
        }),
        ('Contenu', {
            'fields': ('title', 'message', 'deadline_date')
        }),
        ('Statut', {
            'fields': ('is_read', 'is_resolved', 'resolved_at')
        }),
        ('Métadonnées', {
            'fields': ('sent_by', 'sent_at', 'days_late'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'message_type', 'is_read', 'sent_at')
    list_filter = ('message_type', 'is_read', 'sent_at', 'sender__role', 'recipient__role')
    search_fields = ('subject', 'content', 'sender__username', 'recipient__username')
    date_hierarchy = 'sent_at'
    readonly_fields = ('sent_at', 'read_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('sender', 'recipient', 'project', 'message_type')
        }),
        ('Contenu', {
            'fields': ('subject', 'content', 'attachment')
        }),
        ('Statut', {
            'fields': ('is_read', 'read_at')
        }),
        ('Métadonnées', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProjectStatistics)
class ProjectStatisticsAdmin(admin.ModelAdmin):
    list_display = ('project', 'total_reports', 'approved_reports', 'rejected_reports', 'team_count', 'last_activity')
    list_filter = ('last_activity',)
    search_fields = ('project__title',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'team', 'status', 'submission_date')
    list_filter = ('status', 'submission_date', 'project__supervisor')
    search_fields = ('title', 'project__title', 'team__name')

@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'student', 'is_approved', 'is_rejected', 'created_at')
    list_filter = ('is_approved', 'is_rejected', 'created_at', 'project__supervisor')
    search_fields = ('title', 'project__title', 'student__username')
