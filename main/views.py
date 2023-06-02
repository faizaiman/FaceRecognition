from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from django.contrib.auth import authenticate,login as _login, logout as _logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth import views as auth_views,get_user_model
from .decorators import student_required,lecturer_required
from .forms import StudentSignUpForm,LecturerSignUpForm,LoginForm,addCourseForm,editUserProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from .models import Lecturer,Course,Student

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

# def handle500(request, *args, **argv):
#     response = render(request,'pages/error500.html')
#     response.status_code=500
#     return response

# def handle503(request, *args, **argv):
#     response = render(request,'pages/error503.html')
#     response.status_code=503
#     return response


# def page_not_found(request, *args, **argv):
#     response = render(request, 'pages/error404.html')
#     response.status_code =404
#     return response
    
# Create your views here.
User = get_user_model
def index(request):
    if not request.user.is_authenticated:
        return redirect(login)
   
    return render(request,"index.html")
# login auth
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            _login(request ,user)
            messages.success(request,f'You now logged isn as{username}.')
            return redirect(index)
            
        else:
            return render(request,'auth/login.html')
    elif request.method =='GET':
        if request.user.is_authenticated: 
            return redirect(index)
        return render(request,'auth/login.html')
# end of login auth

# logout
def logout(request):
    _logout(request)
    return redirect(login)
# end of logout

# student Register
def register(request):
    
    if request.method == 'POST':
        form  = StudentSignUpForm(request.POST)
    
        if form.is_valid():
            form.save()
           
            return redirect(login)
            
        else:
            print(form)
            form = StudentSignUpForm()
            
    return render(request,'auth/register.html',{'form':StudentSignUpForm()})
#end of student register

#view profile
def profile(request):
    if not request.user.is_authenticated:
        return redirect(login)

    return render(request, 'users/profile.html')
# end of view profile

# Edit Profile 
def editProfile(request,id):
    if not request.user.is_authenticated:
        return redirect(login)
    
    currentUser= get_user_model().objects.get(id=id) #get login user 
    form = editUserProfile(request.POST or None, instance=currentUser)

    if currentUser.is_lecturer ==True: #check if current user is lecturer or not/else current user is student
        getUserLecturer = get_object_or_404(Lecturer,user_id=id) #get data from table main_lecturer
    else: #is student 
        getUserStudent = get_object_or_404(Student,user_id=id) #get data from table main_student
    
    if form.is_valid(): #check if form is valid or not
        if currentUser.is_lecturer ==True: #check if current user is lecturer or not / else current user is student
            getUserLecturer.first_name = request.POST['first_name']
            getUserLecturer.last_name = request.POST['last_name']
            currentUser.save() #save to table main_user
            getUserLecturer.save()#save to table main_lecturer
            
            # print(currentUser.is_lecturer ==True)
        else: # else means current user is student
            
            getUserStudent.first_name = request.POST['first_name'] #get first name from form accountSetting.html
            getUserStudent.last_name = request.POST['last_name'] #get last name from form accountSetting.html
            currentUser.save()
            getUserStudent.save()
        # print(currentUser.is_student ==True)
        return redirect(profile) 
    else: 
        print(form)
        form = editUserProfile(request.POST or None, instance=currentUser)
    
    return render(request,'users/accountSetting.html',{'usr':currentUser})
# End of edit profile
    



#  add Course
def addCourse(request):
    if not request.user.is_authenticated:
        return redirect(login)
    
    lecturer=get_user_model().objects.select_related('lecturer').filter(is_lecturer=True) # get user where is lecturer to be send to addCourse.html 

    if request.method =='POST':
        
        form = addCourseForm(request.POST)
        # print(request.POST)
        if form.is_valid():
            course_code = request.POST['course_code'] #get course code from post
            course_name = request.POST['course_name'] #get course name from post
            credit_hours= request.POST['credit_hours'] #get credit hours from post
            lecturer_id = request.POST['lecturer_id'] #get selected lecturer from post 
            Course(course_code=course_code,course_name=course_name,credit_hours=credit_hours,lecturer_id=lecturer_id).save()
            return redirect(viewCourse)
        else:
            form = addCourseForm()
    # dd(lecturer)
    return render(request,"course/addCourse.html",{'lects':lecturer,'form':addCourseForm()})
# end of add course


# view course
def viewCourse(request):
    if not request.user.is_authenticated:
        return redirect(login)
    
    course = Course.objects.all().select_related('lecturer') #call data from table course and join table main_lecturer to get lecturer name 
    return render(request,"course/course.html",{'courses':course})
# end of view course

# edit course
def editCourse(request,id):
    course = get_object_or_404(Course,id=id)
    form = addCourseForm(request.POST or None, instance=course)
    lecturer=get_user_model().objects.select_related('lecturer').filter(is_lecturer=True)

    # dd(course)
    if form.is_valid():
        course.course_code = request.POST['course_code']
        course.course_name = request.POST['course_name']
        course.credit_hours= request.POST['credit_hours']
        course.lecturer_id = request.POST['lecturer_id']
        course.save()
        return redirect(viewCourse)
    else:
         form = addCourseForm(request.POST or None, instance=course)
    return render(request,"course/editCourse.html",{'course':course,'lects':lecturer})
# end of edit course

# delete course
def deleteCourse(request,id):
    course = get_object_or_404(Course,id=id)
    course.delete()
    return redirect(viewCourse)
# end of delete course

# add lecturer
def addLecturer(request):
    if not request.user.is_authenticated:
        return redirect(login)
    if request.method == 'POST':
        form = LecturerSignUpForm(request.POST)
        
        if form.is_valid():
            form.save()
         
            return redirect(viewLecturer)
        else:
            print(form)
            form = LecturerSignUpForm()
            
    return render(request,"lecturer/addLecturer.html",{'form':LecturerSignUpForm()})
# end of add lecturer

# view lecturer
def viewLecturer(request):
    if not request.user.is_authenticated:
        return redirect(login)
    all_lecturer = get_user_model().objects.select_related('lecturer').filter(is_lecturer=True) #join table main_user with table main_lecturer
    
    return render(request,"lecturer/lecturer.html",{'lects':all_lecturer})
# end of view lecturer

# edit lecturer
def editLecturer(request,id):
    if not request.user.is_authenticated:
        return redirect(login)
    lecturer = get_object_or_404(Lecturer,user_id=id) #get lecturer based on id
    getUserLecturer = get_user_model().objects.select_related('lecturer').get(pk=id) #get user from table main_user where and join table lecturer
    form = editUserProfile(request.POST or None, instance=getUserLecturer)
   
    if form.is_valid():
        getUserLecturer.save()
        lecturer.first_name = request.POST['first_name']
        lecturer.last_name = request.POST['last_name']
        lecturer.save()
        return redirect(viewLecturer)
    else:
        print(form)
        form = editUserProfile(request.POST or None, instance=getUserLecturer)

    return render(request,"lecturer/editLecturer.html",{'lect':getUserLecturer})
# end of edit lecturer

# delete lecturer
def deleteLecturer(request,id):
    lecturer = get_user_model().objects.select_related('lecturer').get(pk=id) #get user id from table main_user and join table main_lecturer
    lecturer.delete()
    return redirect(viewLecturer)
# end of delete lecturer