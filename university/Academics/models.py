from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, Count

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
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(_('Start date must be before end date.'))

    def __str__(self):
        return f"{self.semester} {self.academic_year}"

    def get_course_offerings(self):
        return self.course_offerings.all()

    def get_student_records(self):
        return self.student_records.all()

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
    credit_hours = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subsequent_courses')

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

    def get_departments(self):
        return Department.objects.filter(courses__course=self)

class Department(BaseModel):
    department_id = ShortUUIDField(unique=True, length=5, max_length=10, prefix="Dep", alphabet="1234567890", primary_key=True)
    department_name = models.CharField(max_length=100, db_index=True)
    head_of_department = models.ForeignKey('Users.Teacher', on_delete=models.SET_NULL, null=True, related_name='headed_departments')
    description = models.CharField(max_length=255, null=True, blank=True)
    office_location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.department_name

    def get_courses(self):
        return Course.objects.filter(departments__department=self)

    def get_head_of_department(self):
        return self.head_of_department

    def get_student_records(self):
        return self.student_records.all()

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

    def get_course_offerings(self):
        return self.course_offerings.all()

class CourseOffering(BaseModel):
    offering_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="CoOf", alphabet="1234567890", primary_key=True)
    course_department = models.ForeignKey(CourseDepartment, on_delete=models.CASCADE, related_name='course_offerings')
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name='course_offerings')
    semester_number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])

    class Meta:
        unique_together = ('course_department', 'academic_period', 'semester_number')
        indexes = [
            models.Index(fields=['course_department', 'academic_period']),
        ]

    def __str__(self):
        return f"{self.course_department} - {self.academic_period} - Semester {self.semester_number}"

    def get_course_department(self):
        return self.course_department

    def get_academic_period(self):
        return self.academic_period

    def get_sections(self):
        return self.sections.all()

class Section(BaseModel):
    section_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="Sec", alphabet="1234567890", primary_key=True)
    section_name = models.CharField(max_length=20)
    max_students = models.PositiveIntegerField(validators=[MaxValueValidator(30)])
    course_offerings = models.ManyToManyField(CourseOffering, through='SectionCourseOffering', related_name='sections')

    def __str__(self):
        return f"{self.section_name}"

    def get_course_offerings(self):
        return self.course_offerings.all()

    def get_teacher_assignments(self):
        return TeacherAssignment.objects.filter(section_course_offering__section=self)

    def get_enrollments(self):
        return Enrollment.objects.filter(section_course_offering__section=self)

    def get_unique_student_count(self):
        return self.get_enrollments().values('student_record').distinct().count()

    def get_semester_year_info(self):
        course_offering = self.section_course_offerings.first().course_offering
        return f"{course_offering.academic_period.semester} {course_offering.academic_period.academic_year}"

    @classmethod
    def create_or_get_section(cls, course_offerings):
        academic_period = course_offerings[0].academic_period
        semester_number = course_offerings[0].semester_number

        sections = cls.objects.filter(
            section_course_offerings__course_offering__in=course_offerings
        ).annotate(
            course_count=Count('section_course_offerings')
        ).filter(course_count=len(course_offerings))

        for section in sections:
            enrolled_student_count = Enrollment.objects.filter(
                section_course_offering__section=section,
                section_course_offering__course_offering__academic_period=academic_period,
                section_course_offering__course_offering__semester_number=semester_number
            ).values('student_record').distinct().count()

            if enrolled_student_count < section.max_students:
                return section

        department = course_offerings[0].course_department.department
        new_section_name = f"{department.department_name[:3]}-{sections.count() + 1}sem({semester_number})"
        new_section = cls.objects.create(
            section_name=new_section_name,
            max_students=30
        )
        
        for course_offering in course_offerings:
            SectionCourseOffering.objects.create(section=new_section, course_offering=course_offering)

        return new_section

    class Meta:
        indexes = [
            models.Index(fields=['section_name']),
        ]

class SectionCourseOffering(BaseModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_course_offerings')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='section_course_offerings')

    class Meta:
        unique_together = ('section', 'course_offering')

    def __str__(self):
        return f"{self.section} - {self.course_offering}"

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

    def get_student_records(self):
        return self.student_records.all()

class TeacherAssignment(BaseModel):
    assignment_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="TeAs", alphabet="1234567890", primary_key=True)
    teacher = models.ForeignKey('Users.Teacher', on_delete=models.CASCADE, related_name='assignments')
    section_course_offering = models.ForeignKey(SectionCourseOffering, on_delete=models.CASCADE, related_name='teacher_assignments')

    class Meta:
        unique_together = ('teacher', 'section_course_offering')
        indexes = [
            models.Index(fields=['teacher', 'section_course_offering']),
        ]

    def __str__(self):
        return f"{self.teacher} - {self.section_course_offering}"

    def get_teacher(self):
        return self.teacher

    def get_section_course_offering(self):
        return self.section_course_offering

class StudentAcademicRecord(BaseModel):
    record_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="StAc", alphabet="1234567890", primary_key=True)
    student = models.ForeignKey('Users.Student', on_delete=models.CASCADE, related_name='academic_records')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='student_records')
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name='student_records')
    academic_status = models.ForeignKey(AcademicStatus, on_delete=models.CASCADE, related_name='student_records')
    semester_number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    is_current = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = ('student', 'academic_period')
        indexes = [
            models.Index(fields=['student', 'academic_period']),
            models.Index(fields=['department', 'academic_period']),
        ]

    def __str__(self):
        return f"{self.student} - {self.department} - {self.academic_period}"

    def get_student(self):
        return self.student

    def get_department(self):
        return self.department

    def get_academic_period(self):
        return self.academic_period

    def get_academic_status(self):
        return self.academic_status

    def get_enrollments(self):
        return self.enrollments.all()

    def enroll_in_courses(self, course_offerings):
        """
        Enroll the student in multiple course offerings if they are eligible.
        
        Args:
            course_offerings (list): List of CourseOffering objects to enroll in.
        
        Returns:
            list: List of created Enrollment objects if successful.
        
        Raises:
            ValidationError: If the student is not eligible for enrollment.
        """
        existing_enrollment = Enrollment.objects.filter(
            student_record=self,
            section_course_offering__course_offering__academic_period=self.academic_period,
            section_course_offering__course_offering__semester_number=self.semester_number
        ).first()

        if existing_enrollment:
            section = existing_enrollment.section_course_offering.section
        else:
            section = Section.create_or_get_section(course_offerings)

        enrollments = []
        for course_offering in course_offerings:
            section_course_offering, _ = SectionCourseOffering.objects.get_or_create(
                section=section,
                course_offering=course_offering
            )
            enrollment, created = Enrollment.objects.get_or_create(
                student_record=self,
                section_course_offering=section_course_offering
            )
            if created:
                enrollments.append(enrollment)

        return enrollments

    def get_compatible_courses(self):
        """
        Retrieve courses that are compatible with the student's current academic period,
        semester, and year.

        Returns:
            QuerySet: A queryset of CourseOffering objects that are compatible for enrollment.
        """
        return CourseOffering.objects.filter(
            Q(academic_period=self.academic_period) &
            Q(semester_number=self.semester_number) &
            Q(course_department__department=self.department)
        ).select_related(
            'course_department__course',
            'course_department__department',
            'academic_period'
        ).prefetch_related('sections')

    def batch_enroll(self, course_offering_ids):
        """
        Enroll the student in multiple course offerings.

        Args:
            course_offering_ids (list): List of CourseOffering IDs to enroll in.

        Returns:
            tuple: (success_count, error_messages)
        """
        success_count = 0
        error_messages = []

        for offering_id in course_offering_ids:
            try:
                course_offering = CourseOffering.objects.get(offering_id=offering_id)
                self.enroll_in_courses([course_offering])
                success_count += 1
            except (CourseOffering.DoesNotExist, ValidationError) as e:
                error_messages.append(str(e))

        return success_count, error_messages

    def get_enrolled_course_ids(self):
        """
        Get the IDs of courses the student is currently enrolled in.

        Returns:
            QuerySet: A queryset of enrolled CourseOffering IDs.
        """
        return Enrollment.objects.filter(
            student_record=self,
            section_course_offering__course_offering__academic_period=self.academic_period
        ).values_list('section_course_offering__course_offering_id', flat=True)

class Enrollment(BaseModel):
    enrollment_id = ShortUUIDField(unique=True, length=9, max_length=10, prefix="Enro", alphabet="1234567890", primary_key=True)
    student_record = models.ForeignKey(StudentAcademicRecord, on_delete=models.CASCADE, related_name='enrollments')
    section_course_offering = models.ForeignKey(SectionCourseOffering, on_delete=models.CASCADE, related_name='enrollments')
    registration_date = models.DateTimeField(auto_now_add=True)
    is_retake = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student_record', 'section_course_offering')
        indexes = [
            models.Index(fields=['student_record', 'section_course_offering']),
            models.Index(fields=['registration_date']),
        ]

    def __str__(self):
        return f"{self.student_record.student} enrolled in {self.section_course_offering}"

    def get_student_record(self):
        return self.student_record

    def get_section_offering(self):
        return self.section_course_offering
  
 
 