from django.contrib import admin

from .models import (
    Application,
    AuditLog,
    Scholarship,
    ScholarshipLink,
    ScholarshipPhase,
    ScholarshipRequirement,
    Technology,
)

admin.site.register(Technology)
admin.site.register(Scholarship)
admin.site.register(ScholarshipPhase)
admin.site.register(Application)
admin.site.register(ScholarshipLink)
admin.site.register(ScholarshipRequirement)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_name', 'action', 'record_id', 'user_id', 'created_at')
    list_filter = ('table_name', 'action', 'created_at')
    search_fields = ('record_id', 'user_id')
    readonly_fields = ('id', 'table_name', 'action', 'record_id', 'user_id', 'payload', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
