from django.contrib import admin
from .models import Team, TeamRequest, Message, SubjectChoice, TeamHistory, Report

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'created_at', 'get_members_display')
    list_filter = ('status', 'project', 'created_at')
    search_fields = ('name', 'project__title', 'members__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('members',)

@admin.register(TeamRequest)
class TeamRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'project', 'status', 'created_at', 'message')
    list_display_links = ('id', 'sender', 'receiver')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'message')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        # S'assurer que nous récupérons bien toutes les demandes
        qs = super().get_queryset(request)
        print(f"Nombre total de demandes dans l'admin : {qs.count()}")
        return qs
    
    def save_model(self, request, obj, form, change):
        print(f"Sauvegarde de la demande {obj.id} avec le statut : {obj.status}")
        super().save_model(request, obj, form, change)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'report_type', 'submitted_by', 'submitted_at', 'has_feedback')
    list_filter = ('report_type', 'submitted_at')
    search_fields = ('title', 'team__name', 'submitted_by__username')
    date_hierarchy = 'submitted_at'

    def has_feedback(self, obj):
        return bool(obj.feedback)
    has_feedback.boolean = True
    has_feedback.short_description = "Feedback donné"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'team', 'sent_at', 'read')
    list_filter = ('team', 'sent_at', 'read')
    search_fields = ('content', 'sender__username', 'team__name')
    date_hierarchy = 'sent_at'

@admin.register(SubjectChoice)
class SubjectChoiceAdmin(admin.ModelAdmin):
    list_display = ('team', 'project', 'priority', 'created_at')
    list_filter = ('priority', 'team', 'project')
    search_fields = ('team__name', 'project__title', 'motivation')
    date_hierarchy = 'created_at'

@admin.register(TeamHistory)
class TeamHistoryAdmin(admin.ModelAdmin):
    list_display = ('team', 'action', 'performed_by', 'timestamp')
    list_filter = ('action', 'team', 'performed_by')
    search_fields = ('team__name', 'details', 'performed_by__username')
    date_hierarchy = 'timestamp'
