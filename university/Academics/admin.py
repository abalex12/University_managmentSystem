from django.contrib import admin
from .models import (
    AcademicPeriod,
    Course,
    Department,
    CourseDepartment,
    CourseOffering,
    Section,
    SectionCourseOffering,
    AcademicStatus,
    TeacherAssignment,
    StudentAcademicRecord,
    Enrollment
)

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('academic_period_id', 'academic_year', 'semester', 'start_date', 'end_date')
    list_filter = ('academic_year', 'semester')
    search_fields = ('academic_year', 'semester')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_code', 'course_name', 'credit_hours')
    list_filter = ('credit_hours',)
    search_fields = ('course_code', 'course_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_id', 'department_name', 'head_of_department')
    search_fields = ('department_name',)

@admin.register(CourseDepartment)
class CourseDepartmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'department')
    list_filter = ('department',)
    search_fields = ('course__course_name', 'department__department_name')

@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('offering_id', 'course_department', 'academic_period', 'semester_number')
    list_filter = ('academic_period', 'semester_number')
    search_fields = ('course_department__course__course_name', 'academic_period__academic_year')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'section_name', 'max_students')
    search_fields = ('section_name',)

@admin.register(SectionCourseOffering)
class SectionCourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('section', 'course_offering')
    list_filter = ('course_offering__academic_period','course_offering__semester_number','course_offering__course_department__department')
    search_fields = ('section__section_name', 'course_offering__course_department__course__course_name')

@admin.register(AcademicStatus)
class AcademicStatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'status_name')
    search_fields = ('status_name',)

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'teacher', 'section_course_offering')
    list_filter = ('section_course_offering__course_offering__academic_period',)
    search_fields = ('teacher__username', 'section_course_offering__section__section_name')

@admin.register(StudentAcademicRecord)
class StudentAcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('record_id', 'student', 'department', 'academic_period', 'academic_status', 'semester_number', 'year', 'is_current')
    list_filter = ('academic_period', 'academic_status', 'is_current','department','semester_number')
    search_fields = ('student__username', 'department__department_name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'student_record', 'section_course_offering', 'registration_date', 'is_retake')
    list_filter = ('registration_date', 'is_retake','section_course_offering__section',
                   'section_course_offering__course_offering__semester_number','section_course_offering__course_offering__academic_period',
                   'section_course_offering__course_offering__course_department__department','student_record')
    search_fields = ('student_record__student__username', 'section_course_offering__section__section_name')