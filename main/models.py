from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User,AbstractUser

from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_images',default='default_avatar.png')

    
class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    student_id=models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_images',default='default_avatar.png')
    created_at = models.DateTimeField(default=timezone.now)

class Lecturer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

class Course(models.Model):
    course_code = models.CharField(max_length=100)
    course_name = models.CharField(max_length=200)
    credit_hours = models.IntegerField()
    lecturer = models.ForeignKey(Lecturer,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

class Enrollment(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    register_at = models.DateTimeField(default=timezone.now)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default_avatar.png', upload_to='profile_images')
    
    def __str__(self):
        return self.user.username
    
