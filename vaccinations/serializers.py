from rest_framework import serializers
from .models import VaccinationRecord
from students.models import Student
from drives.models import VaccinationDrive

class VaccinationRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    drive_name = serializers.CharField(source='drive.name', read_only=True)

    class Meta:
        model = VaccinationRecord
        fields = ['id', 'student', 'drive', 'vaccination_date', 'student_name', 'drive_name']