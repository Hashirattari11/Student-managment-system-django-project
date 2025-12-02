from django.contrib import admin
from .models import Department, StudentID, Student
from .models import Subject, subject_marks
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department']

@admin.register(StudentID)
class StudentIDAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'student_email', 'student_age', 'student_department', 'student_id']
    search_fields = ['student_name', 'student_email']
    list_filter = ['student_department', 'student_age']

admin.site.register(Subject)
admin.site.register(subject_marks)