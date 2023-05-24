from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from django.contrib.auth import authenticate,login as _login, logout as _logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth import views as auth_views,get_user_model
from .decorators import student_required,lecturer_required
from .forms import StudentSignUpForm,LecturerSignUpForm,LoginForm,addCourseForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from .models import Lecturer,Course

# from main.models import UserForm, User, Attendance, UserTask, Task
# from main import trainer, face_recognizer, photos_path, utility
# from main import task


from math import ceil
import base64
import os
import time
import datetime
from json import loads
from _thread import start_new_thread


# Create your views here.
User = get_user_model
def index(request):
    if not request.user.is_authenticated:
        return redirect(auth_cover_login)
   
    return render(request,"index.html")

def auth_cover_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            _login(request ,user)
            messages.success(request,f'You now logged isn as{username}.')
            return redirect(index)
            
        else:
            return render(request,'auth/cover-login.html')
    elif request.method =='GET':
        if request.user.is_authenticated: 
            return redirect(index)
        return render(request,'auth/cover-login.html')

def logout(request):
    _logout(request)
    return redirect(auth_cover_login)

def page_not_found(request, *args, **argv):
    response = render(request, 'pages/error404.html')
    response.status_code =404
    return response
    

def register(request):
    if request.method == 'POST':
        form  = StudentSignUpForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
           
            return redirect(auth_cover_login)
            
        else:
            form = StudentSignUpForm()
            
    return render(request,'auth/cover-register.html',{'form':StudentSignUpForm()})

def addLecturer(request):
    if not request.user.is_authenticated:
        return redirect(auth_cover_login)
    if request.method == 'POST':
        form = LecturerSignUpForm(request.POST)
        
        if form.is_valid():
            form.save()
         
            return redirect(viewLecturer)
        else:
            print(form)
            form = LecturerSignUpForm()
            
    return render(request,"addLecturer.html",{'form':LecturerSignUpForm()})



def profile(request):
    if not request.user.is_authenticated:
        return redirect(auth_cover_login)

    return render(request, 'users/accountSetting.html')

def handle500(request, *args, **argv):
    response = render(request,'pages/error500.html')
    response.status_code=500
    return response

def handle503(request, *args, **argv):
    response = render(request,'pages/error503.html')
    response.status_code=503
    return response
# def index(request):
#     return render(request, 'index.html')



def viewLecturer(request):
    if not request.user.is_authenticated:
        return redirect(auth_cover_login)
    all_lecturer = get_user_model().objects.select_related('lecturer').filter(is_lecturer=True)
    
    return render(request,"lecturer.html",{'lects':all_lecturer})

def addCourse(request):
    if not request.user.is_authenticated:
        return redirect(auth_cover_login)
    
    lecturer=get_user_model().objects.select_related('lecturer').filter(is_lecturer=True)

    if request.method =='POST':
        
        form = addCourseForm(request.POST)
        # print(request.POST)
        if form.is_valid():
            course_code = request.POST['course_code']
            course_name = request.POST['course_name']
            credit_hours= request.POST['credit_hours']
            lecturer_id = request.POST['lecturer_id']
            Course(course_code=course_code,course_name=course_name,credit_hours=credit_hours,lecturer_id=lecturer_id).save()
            return redirect(viewCourse)
        else:
            form = addCourseForm()
    # dd(lecturer)
    return render(request,"addCourse.html",{'lects':lecturer,'form':addCourseForm()})




def viewCourse(request):
    if not request.user.is_authenticated:
        return redirect(auth_cover_login)
    
    course = Course.objects.all().select_related('lecturer')
    return render(request,"course.html",{'courses':course})

def editCourse(request,id):
    course = get_object_or_404(Course,id=id)
    dd(course)
    return render(request,"editCourse.html")