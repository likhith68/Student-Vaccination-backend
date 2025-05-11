from rest_framework import viewsets
from .models import VaccinationRecord
from .serializers import VaccinationRecordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from students.models import Student

class VaccinationRecordViewSet(viewsets.ModelViewSet):
    queryset = VaccinationRecord.objects.all()
    serializer_class = VaccinationRecordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        student = serializer.validated_data['student']
        student.vaccination_status = True
        student.save()
        serializer.save()