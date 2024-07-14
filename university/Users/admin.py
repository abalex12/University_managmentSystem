# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher

class CustomUserAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'role', 'account_status', 'date_joined', 'last_login')
    list_filter = ('role', 'account_status', 'is_staff', 'is_superuser')
    search_fields = ('user_id', 'username', 'email', 'phone')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('user_id', 'username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'phone')}),
        ('Permissions', {'fields': ('role', 'account_status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )
    readonly_fields = ('user_id', 'date_joined', 'last_login')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_username', 'get_email')
    search_fields = ('student_id', 'user__username', 'user__email')
    readonly_fields = ('student_id', 'user')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'get_username', 'get_email', 'department')
    list_filter = ('department',)
    search_fields = ('teacher_id', 'user__username', 'user__email', 'department__name')
    readonly_fields = ('teacher_id', 'user')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(User, CustomUserAdmin)