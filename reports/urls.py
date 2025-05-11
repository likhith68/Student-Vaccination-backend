from django.urls import path
from .views import (
    DriveReportCSVView,
    DriveReportPDFView,
    DriveReportExcelView,
    AllDrivesCSVView,
    AllDrivesPDFView,
    AllDrivesExcelView,
    DashboardReportView,
    DashboardMetricsView,)

app_name = 'reports'

urlpatterns = [
    path('dashboard/', DashboardReportView.as_view(), name='dashboard'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    
    path('drives/<int:drive_id>/csv/', DriveReportCSVView.as_view(), name='drive-csv'),
    path('drives/<int:drive_id>/pdf/', DriveReportPDFView.as_view(), name='drive-pdf'),
    path('drives/<int:drive_id>/excel/', DriveReportExcelView.as_view(), name='drive-excel'),
    
    path('drives/all/csv/', AllDrivesCSVView.as_view(), name='all-drives-csv'),
    path('drives/all/pdf/', AllDrivesPDFView.as_view(), name='all-drives-pdf'),
    path('drives/all/excel/', AllDrivesExcelView.as_view(), name='all-drives-excel'),
]