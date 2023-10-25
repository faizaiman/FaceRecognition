from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from django.contrib.auth import authenticate,login as _login, logout as _logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth import views as auth_views,get_user_model
from .decorators import student_required,lecturer_required
from .forms import StudentSignUpForm,LecturerSignUpForm,LoginForm,addCourseForm,editUserProfile,UploadImage,addTimetableForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from .models import Lecturer,Course,Student,Enrollment,Timetable

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
            messages.success(request,f'You now logged as {username}.')
            return redirect(index)
            
        else:
            messages.error(request,f'fail to login')
            return render(request,'auth/login.html')
    elif request.method =='GET':
        if request.user.is_authenticated: 
            return redirect(index)
        return render(request,'auth/login.html')
# end of login auth

# logout
def logout(request):
    _logout(request)
    messages.info(request,f'successful log out')
    return redirect(login)
# end of logout

# student Register
def register(request):
    
    if request.method == 'POST':
        form  = StudentSignUpForm(request.POST)
    
        if form.is_valid():
            form.save()
            messages.success(request,f'successful register')
            return redirect(login)
            
        else:
            print(form)
            messages.error(request,f'Unsuccessful')
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
    elif currentUser.is_student ==True: #is student 
        getUserStudent = get_object_or_404(Student,user_id=id) #get data from table main_student
    else:
        currentUser= get_user_model().objects.get(id=id) #get admin profile
        getUserAdmin= get_user_model().objects.get(id=id) #get login user 

        
    if form.is_valid(): #check if form is valid or not
        if currentUser.is_lecturer ==True: #check if current user is lecturer or not / else current user is student
            getUserLecturer.first_name = request.POST['first_name']
            getUserLecturer.last_name = request.POST['last_name']
            currentUser.save() #save to table main_user
            getUserLecturer.save()#save to table main_lecturer
            
            # print(currentUser.is_lecturer ==True)
        elif currentUser.is_student == True: # else means current user is student
            
            getUserStudent.first_name = request.POST['first_name'] #get first name from form accountSetting.html
            getUserStudent.last_name = request.POST['last_name'] #get last name from form accountSetting.html
            currentUser.save()
            getUserStudent.save()
            
        else:
            currentUser.first_name = request.POST['first_name'] #get first name from form accountSetting.html
            currentUser.last_name = request.POST['last_name'] #get last name from form accountSetting.html
            currentUser.save()
        # print(currentUser.is_student ==True)
        messages.success(request,"Successful Update Profile")
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
            messages.success(request,f'Course has been added')
            return redirect(viewCourse)

        else:
            messages.warning(request,f'Fail to register course')
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

# view timetable
def viewTimetable(request):
    if not request.user.is_authenticated:
        return redirect(login)
    
    timetable = Timetable.objects.all().select_related('lecturer').select_related('course')# call data from table timetable and join table lecturer to get lecturer name and join table course to get course code
    return render(request,'timetable/viewTimetable.html',{'tb':timetable})
#end of view timetable 


#addTimetable
def addTimetable(request):
    if not request.user.is_authenticated:
        return redirect(login)
    
    courses = Course.objects.all()
    # dd(courses)
    if request.method =='POST':
        form = addTimetableForm(request.POST)
        if form.is_valid():

            course_id = request.POST['course_id'] #get course code from post
            DayOfTheWeek = request.POST['DayOfTheWeek'] #get DayOfTheWeek from post
            StartTime= request.POST['start_time'] #get StartTime from post
            EndTime = request.POST['end_time'] #get EndTime from post 
            lct_id = Course.objects.filter(id=course_id).values_list('lecturer_id',flat=True) #get lecturer id from course table 
            lecturer_id = lct_id
            Timetable(DayOfTheWeek=DayOfTheWeek,StartTime=StartTime,EndTime=EndTime,lecturer_id=lecturer_id,course_id=course_id).save()
            # dd(lecturer_id)
            print (form)
            messages.success(request,f'Timetable has been created')
            return redirect(viewTimetable) 
        else:
            print(form)
            messages.warning(request,f'Fail to add Timetable')
            form = addTimetableForm()
    return render (request,'timetable/addTimetable.html',{'form':addTimetableForm(),'course':courses})
#end of addTimeTable


def editTimetable(request,id):
    if not request.user.is_authenticated:
        return redirect(login)
    
    timetable = get_object_or_404(Timetable,id=id)
    form = addTimetableForm(request.POST or None,instance=timetable)
    course  = Course.objects.all()
    
    if form.is_valid():
        timetable.course_id = request.POST['course_id'] #get course code from post
        timetable.DayOfTheWeek = request.POST['DayOfTheWeek'] #get DayOfTheWeek from post
        timetable.StartTime= request.POST['start_time'] #get StartTime from post
        timetable.EndTime = request.POST['end_time'] #get EndTime from post 
        lct_id = Course.objects.filter(id=timetable.course_id).values_list('lecturer_id',flat=True) #get lecturer id from course table 
        timetable.lecturer_id = lct_id
        timetable.save()      
        messages.success(request,f'Timetable has been updated')
        return redirect(viewTimetable)

    else:
        form = addTimetableForm(request.POST or None,instance=timetable)
    
    return render(request,"timetable/editTimetable.html",{'tbs':timetable,'course':course})

def deleteTimetable(request,id):
    timetable = get_object_or_404(Timetable,id=id)
    timetable.delete()
    return redirect(viewTimetable)

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
        messages.success(request,f'Course has been updated')
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

#upload image
def uploadImage(request):
    if not request.user.is_authenticated:
        return redirect(login)
    if request.method == 'POST' and request.FILES['profile_picture']:
        
        form = UploadImage(request.POST,request.FILES)
      #get login user 
        currentUser=get_user_model().objects.get(id=request.user.id) #get login user 
        if currentUser.is_lecturer ==True: #check if current user is lecturer or not/else current user is student
            getUserLecturer = get_object_or_404(Lecturer,user_id=request.user.id) #get data from table main_lecturer
        elif currentUser.is_student ==True: #is student 
            getUserStudent = get_object_or_404(Student,user_id=request.user.id) #get data from table main_student
        else:
            currentUser= get_user_model().objects.get(id=request.user.id) #get admin profile
            getUserAdmin= get_user_model().objects.get(id=request.user.id) #get login user 
        
        if form.is_valid():
            
                if currentUser.is_student ==True: #check if current user is student or not / else current user is lecturer/admin
                        currentUser.profile_picture=request.FILES['profile_picture']
                        getUserStudent.profile_picture=request.FILES['profile_picture']
                        image=form.cleaned_data['profile_picture']
                        print(form)
                        getUserStudent.save()
                
        
                currentUser.profile_picture=request.FILES['profile_picture']
                image=form.cleaned_data['profile_picture']
                print(form)
                currentUser.save()
                return redirect(profile)
        else:
            print(form)
        
        form = UploadImage()

   
    return render(request,"users/uploadImage.html",{'form':UploadImage()})
# end of uploadImage



# add lecturer
def addLecturer(request):
    if not request.user.is_authenticated:
        return redirect(login)
    if request.method == 'POST':
        form = LecturerSignUpForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request,f'Success register new lecturer')
            return redirect(viewLecturer)
        else:
            messages.error(request,f'Fail to register new lecturer')
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
        messages.success(request,f'Successful update lecturer')

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

# view student View MySubject
def mySubject(request):
    if not request.user.is_authenticated:
        return redirect(login)
    # all_lecturer = get_user_model().objects.select_related('lecturer').filter(is_lecturer=True) #join table main_user with table main_lecturer
    enrollment = Enrollment.objects.select_related('course').select_related('student').filter(student_id = request.user.id)
    # dd(request.user.id)
    return render(request,"student/viewSubject.html",{'enn':enrollment})
# end of student View MySubject

# view student View Available Subject
def ViewASubject(request):
    if not request.user.is_authenticated:
        return redirect(login)
    enrollment = Enrollment.objects.values_list('student_id',flat=True)
    student = Student.objects.get(pk=request.user.id) #get current login student based on request.user.id
    course = Course.objects.exclude(enrollment__student=student) #call data from table course
    return render(request,"student/registerSubject.html",{'cours':course,'enrl':enrollment})
# end of student View Available Subject

# Student Register Subject 
def registerSubject(request,id,uid):
    enrollment = Enrollment() #call models enrollment
    course = Course.objects.all().get(pk=id) #call data from table course
    getUserStudent = get_object_or_404(Student,user_id=uid) #get data from table main_student
    # dd(getUserStudent.user_id)
    enrollment.course_id = course.id 
    enrollment.student_id = getUserStudent.user_id
    enrollment.save()
    
    return redirect(mySubject)
# end of Student Register Subject 

# student drop subject
def dropSubject(request,id):
    enroll = get_object_or_404(Enrollment,id=id)
    enroll.delete()
    return redirect(mySubject)
# end of student drop subject

