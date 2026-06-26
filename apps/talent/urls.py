from django.urls import path

from .views import (
    NoteDetailView,
    NoteListCreateView,
    TalentActivateView,
    TalentDeactivateView,
    TalentListCreateView,
)


urlpatterns = [
    path('talent-bank/', TalentListCreateView.as_view(), name='talentbank-list'),
    path('talent-bank/activate/', TalentActivateView.as_view(), name='talentbank-activate'),
    path('talent-bank/deactivate/', TalentDeactivateView.as_view(), name='talentbank-deactivate'),
    
    path('notes/', NoteListCreateView.as_view(), name='notes-list'),
    path('notes/<uuid:pk>/', NoteDetailView.as_view(), name='notes-detail'),
]
