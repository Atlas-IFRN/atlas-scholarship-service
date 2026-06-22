from django.urls import path

from .views import (
    ApplicationCancelView,
    ApplicationCreateView,
    ApplicationListView,
    ScholarshipDetailView,
    ScholarshipListCreateView,
    ApplicationReproveView,
    ApplicationAproveView,
    TechnologyListCreateView,
)

urlpatterns = [
    path('scholarships/', ScholarshipListCreateView.as_view(), name='scholarship-list-create'),
    path('scholarships/<uuid:pk>/', ScholarshipDetailView.as_view(), name='scholarship-detail'),
    
    path('applications/', ApplicationListView.as_view(), name='application-list'),
    path('scholarships/<uuid:scholarship_id>/apply/', ApplicationCreateView.as_view(), name='application-create'),
    path('scholarships/<uuid:scholarship_id>/cancel/', ApplicationCancelView.as_view(), name='application-cancel'),
    path('applications/<uuid:pk>/reprove/', ApplicationReproveView.as_view(), name='application-reprove'),
    path('applications/<uuid:pk>/approve/', ApplicationAproveView.as_view(), name='application-approve'),   
    
    path('technologies/', TechnologyListCreateView.as_view(), name='technology-list'),
]
