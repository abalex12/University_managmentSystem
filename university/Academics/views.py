# views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import StudentAcademicRecord
from django.shortcuts import get_object_or_404
from Users.models import Student



@login_required
def course_registration(request):
    student=get_object_or_404(Student,user=request.user)
    student_record = StudentAcademicRecord.objects.get(
        student=student,
        is_current=True
    )

    if not student_record:
        messages.error(request, "No active academic record found.")
        return redirect('student_dashboard')  

    available_courses = student_record.get_compatible_courses()
    enrolled_course_ids = student_record.get_enrolled_course_ids()
    success = False
    if request.method == 'POST':
        course_offering_ids = request.POST.getlist('course_offering_ids')
        success_count, error_messages = student_record.batch_enroll(course_offering_ids)

        if success_count:
            messages.success(request, f"Successfully enrolled in {success_count} course(s).")
            success = True
        
        for error in error_messages:
            messages.error(request, error)

        # Refresh the enrolled course IDs after enrollment
        enrolled_course_ids= student_record.get_enrolled_course_ids()

    context = {
        'student_record': student_record,
        'available_courses': available_courses,
        'enrolled_course_ids': enrolled_course_ids,
        'success':success
    }

    return render(request, 'academics/course_registration.html', context)