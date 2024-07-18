from django.contrib.auth import get_user_model
from Users.models import Student, Teacher
from Academics.models import  StudentAcademicRecord, Enrollment, AcademicPeriod,Course, Department,TeacherAssignment
from django.utils import timezone
from django.db.models import Prefetch


User = get_user_model()



def get_current_academic_period():
    return AcademicPeriod.objects.order_by('-start_date').first()

def user_role_context(request):
    if request.user.is_authenticated:
        user = request.user
        role = user.role
        user_data = {'user': user}
        current_academic_period = get_current_academic_period()
        user_data['current_academic_period'] = current_academic_period

        if role == 'Student':
            try:
                student_profile = Student.objects.get(user=user)
                user_data['student_profile'] = student_profile

                academic_record = StudentAcademicRecord.objects.select_related(
                    'department', 'academic_status'
                ).get(student=student_profile, academic_period=current_academic_period, is_current=True)

                enrollments = Enrollment.objects.filter(
                    student_record=academic_record
                ).select_related(
                    'section_course_offering__section',
                    'section_course_offering__course_offering__course_department__course',
                    'section_course_offering__course_offering__course_department__department'
                )

                user_data['academic_record'] = academic_record
                user_data['enrollments'] = enrollments
                user_data['current_year'] = academic_record.year
                user_data['current_semester'] = academic_record.semester_number
                user_data['department'] = academic_record.department
                user_data['academic_status'] = academic_record.academic_status

                current_courses = [
                    enrollment.section_course_offering.course_offering.course_department.course 
                    for enrollment in enrollments
                ]
                user_data['current_courses'] = current_courses

                compatible_courses = academic_record.get_compatible_courses()
                user_data['compatible_courses'] = compatible_courses

                enrolled_course_ids = academic_record.get_enrolled_course_ids()
                user_data['enrolled_course_ids'] = enrolled_course_ids

            except Student.DoesNotExist:
                user_data['student_profile'] = None
                user_data['academic_record'] = None
                user_data['enrollments'] = None
                user_data['current_courses'] = None
                user_data['compatible_courses'] = None
                user_data['enrolled_course_ids'] = None

        elif role == 'Teacher':
            try:
                teacher_profile = Teacher.objects.get(user=user)
                user_data['teacher_profile'] = teacher_profile

                teacher_assignments = TeacherAssignment.objects.filter(
                    teacher=teacher_profile,
                    section_course_offering__course_offering__academic_period=current_academic_period
                ).select_related(
                    'section_course_offering__section',
                    'section_course_offering__course_offering__course_department__course',
                    'section_course_offering__course_offering__course_department__department'
                )
                user_data['teacher_assignments'] = teacher_assignments

                taught_courses = [
                    assignment.section_course_offering.course_offering.course_department.course
                    for assignment in teacher_assignments
                ]
                user_data['taught_courses'] = taught_courses

                taught_sections = [
                    assignment.section_course_offering.section
                    for assignment in teacher_assignments
                ]
                user_data['taught_sections'] = taught_sections

            except Teacher.DoesNotExist:
                user_data['teacher_profile'] = None
                user_data['teacher_assignments'] = None
                user_data['taught_courses'] = None
                user_data['taught_sections'] = None

        elif role == 'Admin':
            user_data['admin_profile'] = user

            # Add any specific admin-related data here
            user_data['total_students'] = Student.objects.count()
            user_data['total_teachers'] = Teacher.objects.count()
            user_data['total_courses'] = Course.objects.count()
            user_data['total_departments'] = Department.objects.count()

        return user_data

    return {}

# def get_current_academic_year():
#     now = timezone.now()
#     current_month = now.month

#     if current_month in [7,8, 9, 10, 11, 12, 1]:  # Fall semester
#         current_semester = 'Fall'
#         if current_month == 1:  # January
#             current_year = now.year - 1
#         else:
#             current_year = now.year
#     elif current_month in [2, 3, 4, 5, 6]:  # Winter semester
#         current_semester = 'Winter'
#         current_year = now.year - 1
#     else:
        
#         return None

#     academic_year_name = f"{current_year}/{current_year + 1}"

#     try:
#         academic_year = AcademicPeriod.objects.get(academic_year=academic_year_name, semester=current_semester)
#         return f'{academic_year}'
#     except AcademicPeriod.DoesNotExist:
       
#         return None

# def students_past_data(student):
#     academic_records = StudentAcademicRecord.objects.filter(student=student)
#     return academic_records