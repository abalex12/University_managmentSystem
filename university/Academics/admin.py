from django.contrib import admin
from .models import (
    AcademicPeriod, Course, Department, CourseDepartment,
    CourseOffering, Section, AcademicStatus, TeacherAssignment,
    StudentAcademicRecord, Enrollment
)

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('academic_period_id', 'academic_year', 'semester', 'start_date', 'end_date')
    list_filter = ('academic_year', 'semester')
    search_fields = ('academic_year', 'semester')
    ordering = ('-academic_year', 'semester')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'course_code', 'credit_hours')
    search_fields = ('course_name', 'course_code')
    list_filter = ('credit_hours',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_id', 'department_name', 'head_of_department', 'office_location')
    search_fields = ('department_name', 'head_of_department__name')  # Assuming Teacher model has a 'name' field
    list_filter = ('office_location',)

@admin.register(CourseDepartment)
class CourseDepartmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'department')
    list_filter = ('department',)
    search_fields = ('course__course_name', 'department__department_name')

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('offering_id', 'course_department', 'academic_period')
    list_filter = ('academic_period',)
    search_fields = ('course_department__course__course_name', 'academic_period__academic_year')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'section_name', 'course_offering')
    list_filter = ('course_offering__academic_period',)
    search_fields = ('section_name', 'course_offering__course_department__course__course_name')

@admin.register(AcademicStatus)
class AcademicStatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'status_name')
    search_fields = ('status_name',)

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'teacher', 'section')
    list_filter = ('section__course_offering__academic_period',)
    search_fields = ('teacher__name', 'section__section_name')  # Assuming Teacher model has a 'name' field

@admin.register(StudentAcademicRecord)
class StudentAcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('record_id', 'student', 'department', 'academic_period', 'academic_status', 'is_current')
    list_filter = ('academic_period', 'academic_status', 'is_current', 'department')
    search_fields = ('student__name', 'department__department_name')  # Assuming Student model has a 'name' field
    fieldsets = (
        (None, {
            'fields': ('student', 'department', 'academic_period', 'academic_status')
        }),
        ('Academic Details', {
            'fields': ('semester_number', 'year', 'is_current')
        }),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'student_record', 'section', 'registration_date', 'is_retake')
    list_filter = ('is_retake', 'registration_date', 'section__course_offering__academic_period')
    search_fields = ('student_record__student__name', 'section__section_name')  # Assuming Student model has a 'name' field
    date_hierarchy = 'registration_date'