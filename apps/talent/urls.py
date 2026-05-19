from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NoteViewSet, TalentViewSet

router = DefaultRouter()
router.register(r'talent-bank', TalentViewSet, basename='talentbank')
router.register(r'notes', NoteViewSet, basename='notes')

urlpatterns = [
    path('', include(router.urls)),
]
