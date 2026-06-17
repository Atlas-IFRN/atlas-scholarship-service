from django.urls import path

from .views import ScholarshipListCreateView, ScholarshipDetailView, ApplicationListView, ApplicationCreateView, ApplicationCancelView, TechnologyListView

urlpatterns = [
    path('scholarships/', ScholarshipListCreateView.as_view(), name='scholarship-list-create'),
    path('scholarships/<uuid:pk>/', ScholarshipDetailView.as_view(), name='scholarship-detail'),
    
    path('applications/', ApplicationListView.as_view(), name='application-list'),
    path('scholarships/<uuid:scholarship_id>/apply/', ApplicationCreateView.as_view(), name='application-create'),
    path('scholarships/<uuid:scholarship_id>/cancel/', ApplicationCancelView.as_view(), name='application-cancel'),
    
    path('technologies/', TechnologyListView.as_view(), name='technology-list'),
]
