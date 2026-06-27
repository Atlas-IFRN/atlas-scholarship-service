from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet, ScholarshipViewSet, TechnologyViewSet

router = DefaultRouter()
router.register(r'scholarships', ScholarshipViewSet, basename='scholarship')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'technologies', TechnologyViewSet, basename='technology')

urlpatterns = [
    path('', include(router.urls)),
]
