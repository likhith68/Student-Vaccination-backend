from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from vaccinations.models import VaccinationRecord
from drives.models import VaccinationDrive
from students.models import Student
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import pandas as pd
import xlsxwriter
import csv
import io
from datetime import date
from django.db.models import Prefetch
from django.db.models import Count, Q
from django.core.cache import cache

class DashboardReportView(APIView):
    def get(self, request):
        total_students = Student.objects.count()
        total_drives = VaccinationDrive.objects.count()
        total_vaccinations = VaccinationRecord.objects.count()

        return Response({
            "total_students": total_students,
            "total_drives": total_drives,
            "total_vaccinations": total_vaccinations,
        })

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = 'dashboard_metrics'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        total_students = Student.objects.count()
        students_vaccinated = Student.objects.filter(vaccination_status=True).count()
        upcoming_drives = VaccinationDrive.objects.filter(date__gte=date.today()).count()
        
        grades = Student.objects.values_list('grade', flat=True).distinct()
        vaccination_trend = {}
        vaccinated_by_grade = {}
        
        for grade in grades:
            vaccinated = Student.objects.filter(grade=grade, vaccination_status=True).count()
            not_vaccinated = Student.objects.filter(grade=grade, vaccination_status=False).count()
            
            vaccination_trend[str(grade)] = {
                "vaccinated": vaccinated,
                "not_vaccinated": not_vaccinated
            }
            vaccinated_by_grade[str(grade)] = vaccinated
        
        upcoming_drives_list = VaccinationDrive.objects.filter(date__gte=date.today()).values(
            'name', 'date'
        ).order_by('date')[:10] 
        
        data = {
            "total_students": total_students,
            "students_vaccinated": students_vaccinated,
            "upcoming_drives": upcoming_drives,
            "vaccinated_by_grade": vaccinated_by_grade,
            "vaccination_trend": vaccination_trend,
            "upcoming_drives_list": list(upcoming_drives_list),
        }
        
        return Response(data)

class BaseDriveReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_drive_data(self, drive_id):
        try:
            drive = VaccinationDrive.objects.get(pk=drive_id)
            records = VaccinationRecord.objects.filter(drive=drive).select_related('student')
            return drive, records
        except VaccinationDrive.DoesNotExist:
            return None, None

    def prepare_data(self, drive, records):
        if not records.exists():
            return [{
                "Drive Name": drive.name,
                "Date": drive.date.strftime('%Y-%m-%d'),
                "Message": "No students vaccinated in this drive"
            }]
        
        data = []
        for record in records:
            data.append({
                "Name": record.student.name,
                "Grade": record.student.grade,
                "Roll Number": record.student.roll_number,
                "Date Vaccinated": record.vaccination_date.strftime('%Y-%m-%d')
            })
        return data

class DriveReportCSVView(BaseDriveReportView):
    def get(self, request, drive_id):
        drive, records = self.get_drive_data(drive_id)
        if not drive:
            return Response({"error": "Drive not found"}, status=404)
        
        data = self.prepare_data(drive, records)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="drive_{drive_id}_report.csv"'
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return response

class DriveReportPDFView(BaseDriveReportView):
    def get(self, request, drive_id):
        drive, records = self.get_drive_data(drive_id)
        if not drive:
            return Response({"error": "Drive not found"}, status=404)
        
        data = self.prepare_data(drive, records)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        y = 800
        p.setFont("Helvetica", 12)
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Drive: {drive.name}")
        y -= 20
        p.drawString(50, y, f"Date: {drive.date.strftime('%Y-%m-%d')}")
        y -= 30
        p.setFont("Helvetica", 12)
        
        if not records.exists():
            p.drawString(50, y, "No students vaccinated in this drive")
            y -= 20
        else:
            for row in data:
                if y < 50:
                    p.showPage()
                    y = 800
                line = f"{row['Name']} (Grade {row['Grade']}, Roll {row['Roll Number']}) - Vaccinated on {row['Date Vaccinated']}"
                p.drawString(50, y, line)
                y -= 20
        
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="drive_{drive_id}_report.pdf"'
        return response

class DriveReportExcelView(BaseDriveReportView):
    def get(self, request, drive_id):
        drive, records = self.get_drive_data(drive_id)
        if not drive:
            return Response({"error": "Drive not found"}, status=404)
        
        data = self.prepare_data(drive, records)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(data).to_excel(writer, index=False)
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="drive_{drive_id}_report.xlsx"'
        return response

class AllDrivesBaseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_drives_data(self):
        return VaccinationDrive.objects.all().prefetch_related(
            Prefetch('vaccinationrecord_set', 
                   queryset=VaccinationRecord.objects.select_related('student'))
        )
    
    def prepare_data(self):
        drives = self.get_drives_data()
        all_data = []
        
        for drive in drives:
            drive_header = {
                "Drive Name": drive.name,
                "Date": drive.date.strftime('%Y-%m-%d')
            }
            all_data.append(drive_header)
            
            records = drive.vaccinationrecord_set.all()
            if records.exists():
                for record in records:
                    all_data.append({
                        "Name": record.student.name,
                        "Grade": record.student.grade,
                        "Roll Number": record.student.roll_number,
                        "Date Vaccinated": record.vaccination_date.strftime('%Y-%m-%d')
                    })
            else:
                all_data.append({
                    "Message": "No students vaccinated in this drive"
                })
            
            all_data.append({})
            
        return all_data

class AllDrivesCSVView(AllDrivesBaseView):
    def get(self, request):
        data = self.prepare_data()
        
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(fieldnames)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_drives_report.csv"'
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            if row: 
                writer.writerow(row)
            else:
                writer.writerow({})  
        
        return response

class AllDrivesExcelView(AllDrivesBaseView):
    def get(self, request):
        data = self.prepare_data()
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(fieldnames)
        
        for col_num, header in enumerate(fieldnames):
            worksheet.write(0, col_num, header)
        
        row_num = 1
        for data_row in data:
            if not data_row:  
                row_num += 1
                continue
                
            for col_num, header in enumerate(fieldnames):
                worksheet.write(row_num, col_num, data_row.get(header, ""))
            row_num += 1
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="all_drives_report.xlsx"'
        return response

class AllDrivesPDFView(AllDrivesBaseView):
    def get(self, request):
        data = self.prepare_data()
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        y = 800
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, "All Vaccination Drives Report")
        y -= 40
        
        p.setFont("Helvetica", 12)
        for row in data:
            if not row:  
                y -= 20
                continue
                
            if "Drive Name" in row:  
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, f"Drive: {row['Drive Name']}")
                y -= 20
                p.drawString(50, y, f"Date: {row['Date']}")
                y -= 20
                p.setFont("Helvetica", 12)
            elif "Message" in row:  
                p.drawString(50, y, row['Message'])
                y -= 20
            else:  
                line = f"{row['Name']} (Grade {row['Grade']}, Roll {row['Roll Number']}) - Vaccinated on {row['Date Vaccinated']}"
                p.drawString(50, y, line)
                y -= 20
            
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 12)
        
        p.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="all_drives_report.pdf"'
        return response