from rest_framework import viewsets, status
from .models import Student
from .serializers import StudentSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import csv

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        deleted_data = serializer.data  # Store data before deletion
        self.perform_destroy(instance)
        return Response({
            "message": "Student deleted successfully",
            "deleted_student": deleted_data
        }, status=status.HTTP_200_OK)

class StudentCSVUploadView(APIView):
    parser_classes = [MultiPartParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0
        errors = []

        for row_number, row in enumerate(reader, start=2):
            try:
                Student.objects.create(
                    name=row['name'],
                    grade=row['grade'],
                    roll_number=int(row['roll_number']),
                    vaccination_status=row['vaccination_status'].lower() in ('yes', 'true', '1'),
                )
                created_count += 1
            except Exception as e:
                errors.append(f"Row {row_number}: {str(e)}")

        if errors:
            return Response(
                {
                    "status": f"Completed with {len(errors)} errors",
                    "created": created_count,
                    "errors": errors
                },
                status=207
            )

        return Response({
            "status": "Upload successful",
            "created": created_count
        })