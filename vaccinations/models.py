from django.db import models
from students.models import Student
from drives.models import VaccinationDrive

class VaccinationRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    drive = models.ForeignKey(VaccinationDrive, on_delete=models.CASCADE)
    vaccination_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'drive')

    def __str__(self):
        return f"{self.student.name} - {self.drive.name}"