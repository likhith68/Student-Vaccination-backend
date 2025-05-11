from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=20)
    roll_number = models.IntegerField()
    vaccination_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - Grade {self.grade}"