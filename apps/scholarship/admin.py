from django.contrib import admin

from .models import Application, Scholarship, ScholarshipLink, ScholarshipPhase, ScholarshipRequirement, Technology

admin.site.register(Technology)
admin.site.register(Scholarship)
admin.site.register(ScholarshipPhase)
admin.site.register(Application)
admin.site.register(ScholarshipLink)
admin.site.register(ScholarshipRequirement)
