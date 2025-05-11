from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, filters
from .models import VaccinationDrive
from .serializers import VaccinationDriveSerializer
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from rest_framework.exceptions import ValidationError

class VaccinationDriveViewSet(viewsets.ModelViewSet):
    queryset = VaccinationDrive.objects.all()
    serializer_class = VaccinationDriveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


    def get_queryset(self):
        queryset = super().get_queryset()
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            today = date.today()
            thirty_days_later = today + timedelta(days=30)
            queryset = queryset.filter(date__gte=today, date__lte=thirty_days_later)
        return queryset

    def perform_create(self, serializer):
        drive_date = serializer.validated_data.get('date')

        if drive_date is None:
            raise ValidationError({"date": "Drive date is required."})

        if drive_date < date.today():
            raise ValidationError({"date": "Drive date must be today or a future date."})

        serializer.save()

    def perform_update(self, serializer):
        drive_date = serializer.validated_data.get('date')

        if drive_date is not None: 
            if drive_date < date.today():
                raise ValidationError({"date": "Drive date must be today or a future date."})

        serializer.save()