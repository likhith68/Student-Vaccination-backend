from rest_framework import serializers
from .models import VaccinationDrive
from datetime import date

class VaccinationDriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationDrive
        fields = '__all__'

    def validate_date(self, value):
        if value is None:
            raise serializers.ValidationError("Date is required.")
        if value < date.today():
            raise serializers.ValidationError("Drive date must be today or in the future.")
        return value