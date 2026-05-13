from django.contrib import admin

from .models import Application, Scholarship, ScholarshipPhase, Technology

admin.site.register(Technology)
admin.site.register(Scholarship)
admin.site.register(ScholarshipPhase)
admin.site.register(Application)
