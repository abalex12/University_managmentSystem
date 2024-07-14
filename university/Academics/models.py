from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AcademicPeriod(BaseModel):
    SEMESTER_CHOICES = [
        ('Fall', 'Fall'),
        ('Winter', 'Winter')
    ]
    academic_period_id = ShortUUIDField(unique=True, length=5, max_length=10, prefix="AcPe", alphabet="1234567890", primary_key=True)
    academic_year = models.CharField(max_length=20, db_index=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, db_index=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_('Start date must be before end date.'))

    def __str__(self):
        return f"{self.semester} {self.academic_year}"

    class Meta:
        unique_together = ('academic_year', 'semester')
        ordering = ['academic_year', 'semester']
        indexes = [
            models.Index(fields=['academic_year', 'semester']),
        ]

class Course(BaseModel):
    course_id = ShortUUIDField(unique=True, length=5, max_length=10, prefix="Cour", alphabet="1234567890", primary_key=True)
    course_name = models.CharField(max_length=100, db_index=True)
    course_code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    credit_hours = models.PositiveIntegerField()

    def __str__(self):
        return self.course_name

class Department(BaseModel):
    department_id = ShortUUIDField(unique=True, length=5, max_length=10, prefix="Dep", alphabet="1234567890", primary_key=True)
    department_name = models.CharField(max_length=100, db_index=True)
    head_of_department = models.ForeignKey('Users.Teacher', on_delete=models.SET_NULL, null=True, related_name='headed_departments')
    description = models.CharField(max_length=255, null=True, blank=True)
    office_location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.department_name

class CourseDepartment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')

    class Meta:
        unique_together = ('course', 'department')
        indexes = [
            models.Index(fields=['course', 'department']),
        ]

    def __str__(self):
        return f'{self.course} - {self.department}'

class CourseOffering(BaseModel):
    offering_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="CoOf", alphabet="1234567890", primary_key=True)
    course_department = models.ForeignKey(CourseDepartment, on_delete=models.CASCADE, related_name='course_offerings')
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name='course_offerings')

    class Meta:
        unique_together = ('course_department', 'academic_period')
        indexes = [
            models.Index(fields=['course_department', 'academic_period']),
        ]

    def __str__(self):
        return f"{self.course_department} - {self.academic_period}"

class Section(BaseModel):
    section_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="Sec", alphabet="1234567890", primary_key=True)
    section_name = models.CharField(max_length=20)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f"{self.section_name} - {self.course_offering}"

    class Meta:
        unique_together = ('section_name', 'course_offering')
        indexes = [
            models.Index(fields=['section_name', 'course_offering']),
        ]

class AcademicStatus(BaseModel):
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('probation', 'Probation'),
        ('dismissed', 'Dismissed'),
        ('graduated', 'Graduated'),
    ]
    status_id = ShortUUIDField(unique=True, length=5, max_length=10, prefix="AcSt", alphabet="1234567890", primary_key=True)
    status_name = models.CharField(max_length=50, unique=True, choices=STATUS_CHOICES)

    def __str__(self):
        return self.get_status_name_display()

class TeacherAssignment(BaseModel):
    assignment_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="TeAs", alphabet="1234567890", primary_key=True)
    teacher = models.ForeignKey('Users.Teacher', on_delete=models.CASCADE, related_name='assignments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='teacher_assignments')

    class Meta:
        unique_together = ('teacher', 'section')
        indexes = [
            models.Index(fields=['teacher', 'section']),
        ]

class StudentAcademicRecord(BaseModel):
    record_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="StAc", alphabet="1234567890", primary_key=True)
    student = models.ForeignKey('Users.Student', on_delete=models.CASCADE, related_name='academic_records')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='student_records')
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name='student_records')
    academic_status = models.ForeignKey(AcademicStatus, on_delete=models.CASCADE, related_name='student_records')
    semester_number = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    is_current = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = ('student', 'department', 'academic_period')
        indexes = [
            models.Index(fields=['student', 'academic_period']),
            models.Index(fields=['department', 'academic_period']),
        ]

    def __str__(self):
        return f"{self.student} - {self.department} - {self.academic_period}"

class Enrollment(BaseModel):
    enrollment_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="Enro", alphabet="1234567890", primary_key=True)
    student_record = models.ForeignKey(StudentAcademicRecord, on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    registration_date = models.DateTimeField(auto_now_add=True)
    is_retake = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student_record', 'section')
        indexes = [
            models.Index(fields=['student_record', 'section']),
            models.Index(fields=['registration_date']),
        ]

    def __str__(self):
        return f"{self.student_record.student} enrolled in {self.section}"