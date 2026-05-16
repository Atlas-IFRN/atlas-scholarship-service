from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InterviewRecordViewSet, TalentBankRegistrationViewSet

router = DefaultRouter()
router.register(r'talent-bank', TalentBankRegistrationViewSet, basename='talentbank')
router.register(r'interviews', InterviewRecordViewSet, basename='interview')

urlpatterns = [
    path('', include(router.urls)),
]
