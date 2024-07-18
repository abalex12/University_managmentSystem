from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import AbstractUser

ROLE = [
    ('Student', 'Student'),
    ('Teacher', 'Teacher'),
    ('Admin', 'Admin')
]
GENDER = [
    ('Male', 'Male'), 
    ('Female', 'Female'), 
    ('Other', 'Other') 
]

class User(AbstractUser):
    user_id = ShortUUIDField(unique=True, length=10, max_length=20, prefix="User", alphabet="1234567890", primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=20, choices=ROLE, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    account_status = models.CharField(max_length=20, default='Active', db_index=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['role', 'account_status']),
        ]

class Student(models.Model):
    student_id = ShortUUIDField(length=7, prefix='stu', primary_key=True, alphabet="1234567890")
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Student: {self.user.username}"

    class Meta:
        indexes = [models.Index(fields=['user'])]

class Teacher(models.Model):
    teacher_id = ShortUUIDField(length=7, prefix='tea', primary_key=True, alphabet="1234567890")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Academics.Department', on_delete=models.SET_NULL, null=True, related_name='teachers')

    def __str__(self):
        return f"Teacher: {self.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['department']),
        ]