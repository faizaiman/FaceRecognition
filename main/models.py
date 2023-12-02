import os
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import post_save
from django.utils import timezone
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_picture',default='default_avatar.png')

    
def student_image_upload_path(instance,filename):
    student_id = instance.student_id
    dataset='dataset'
    base_filename, file_extension = os.path.splitext(filename)
    return f'{dataset}/{student_id}/{base_filename}{file_extension}'
class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    student_id=models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to=student_image_upload_path,default='default_avatar.png')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
   
@receiver(post_save, sender=Student) 
def create_student_folder(sender,instance,created,**kwargs):
    if created:
        student_folder = os.path.join("face_trainer/dataset",instance.student_id)
        os.makedirs(student_folder,exist_ok=True)

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

class Timetable(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer,on_delete=models.CASCADE)
    DayOfTheWeek = models.CharField(max_length=100)
    StartTime = models.CharField(max_length=100)
    EndTime = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

class Attendance(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default="absent")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default_avatar.png', upload_to='profile_images')
    
    def __str__(self):
        return self.user.username
    
