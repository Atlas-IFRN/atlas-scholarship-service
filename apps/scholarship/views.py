from rest_framework import viewsets

from .models import Application, Scholarship, Technology
from .serializers import ApplicationSerializer, ScholarshipSerializer, TechnologySerializer


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    lookup_field = 'id'


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = 'id'


class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    lookup_field = 'id'
