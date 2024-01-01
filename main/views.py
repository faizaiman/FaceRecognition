from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from django.contrib.auth import authenticate,login as _login, logout as _logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth import views as auth_views,get_user_model
from .forms import StudentSignUpForm,LecturerSignUpForm,LoginForm,addCourseForm,editUserProfile,UploadImage,addTimetableForm,DatasetImageForm,LeaveForm, LeaveApprovalForm
from .models import Lecturer,Course,Student,Enrollment,Timetable,Attendance,DatasetImages,Leave
from django.db.models import Count,F,ExpressionWrapper, fields,Exists,OuterRef
from django.db.models.functions import TruncMonth,TruncDate
from django.views.decorators.http import require_POST
from datetime import datetime,timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

import pytz

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

    total_lecture = get_user_model().objects.select_related('lecturer').filter(is_lecturer=True).count()
    total_student = get_user_model().objects.select_related('student').filter(is_student=True).count()
    student_tclass = Enrollment.objects.select_related('course').select_related('student').filter(student_id = request.user.id).count()
    lecturer_class = Timetable.objects.all().select_related('lecturer').select_related('course').filter(lecturer_id = request.user.id).count()
    timetable =Timetable.objects.filter(course__enrollment__student=request.user.id).select_related('course', 'lecturer').all()

    lect_timetable = Timetable.objects.filter(lecturer_id=request.user.id).select_related('course', 'lecturer').prefetch_related('course__enrollment_set__student').all()


    # Start of chart query
    users= get_user_model().objects.all()
    user_registrations = users.annotate(
        registration_date=TruncMonth('date_joined')
    ).values('registration_date').annotate(
        registration_count=Count('id')
    ).order_by('registration_date')
    data = [entry['registration_count'] for entry in user_registrations]
    labels = [entry['registration_date'].strftime('%B-%Y') for entry in user_registrations]
    # end of chart query
    
   
    
    # dd(labels)
   
    return render(request,"index.html",{'total_lecturer':total_lecture,'total_student':total_student,'total_stclass':student_tclass,'t_lc':lecturer_class,'tb':timetable,'lect_tb':lect_timetable,'data':data,'labels':labels})
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

def ViewClass(request):
    if not request.user.is_authenticated:
        return redirect(login)
    
    lect_timetable = Timetable.objects.filter(lecturer_id=request.user.id).select_related('course', 'lecturer').prefetch_related('course__enrollment_set__student').all()

    
    return render(request,'lecturer/viewClass.html',{'lect_tb':lect_timetable})

def viewAttendance(request):
    if not request.user.is_authenticated:
        return redirect(login)
    lect_timetable = Timetable.objects.filter(lecturer_id=request.user.id).select_related('course', 'lecturer').prefetch_related('course__enrollment_set__student').all()

    
    return render(request,'lecturer/attendance.html',{'lect_tb':lect_timetable})

def attendanceSessions(request,id):
    if not request.user.is_authenticated:
        return redirect(login)
    
    
    attendance_sessions =( 
                            Attendance.objects
                    .filter(course_id=id)
                    .select_related('course__timetable')
                    .annotate(date=TruncDate('timestamp'))
                    .values('date', 'course__timetable__DayOfTheWeek', 'course__timetable__StartTime', 'course__timetable__EndTime','course_id')
                    .annotate(session_count=Count('id'))
                    .order_by('date')
                          )
    
    class_info = Course.objects.values('course_code', 'course_name', 'lecturer__first_name', 'lecturer__last_name').get(id=id)

    total_class_sessions = attendance_sessions.count()
    
    
    return render(request,'lecturer/attendance_sessions.html',{'attend_sessions':attendance_sessions,'class_info':class_info,'total_session':total_class_sessions})


# def attendanceSessions(request, id):
#     if not request.user.is_authenticated:
#         return redirect(login)
    
#     attendance_sessions = (
#         Attendance.objects
#         .filter(course_id=id)
#         .select_related('course__timetable')
#         .annotate(date=TruncDate('timestamp'))
#         .values(
#             'date', 
#             'course__timetable__DayOfTheWeek', 
#             'course__timetable__StartTime', 
#             'course__timetable__EndTime',
#             'course_id'
#         )
#         .annotate(
#             session_count=Count('id')
#         )
#         .order_by('date')
#     )
            
    
#     class_info = Course.objects.values('course_code', 'course_name', 'lecturer__first_name', 'lecturer__last_name').get(id=id)

#     total_class_sessions = attendance_sessions.count()
    
#     return render(request, 'lecturer/attendance_sessions.html', {'attend_sessions': attendance_sessions, 'class_info': class_info, 'total_session': total_class_sessions})



def attendanceReport(request,date,course_id):
    if not request.user.is_authenticated:
        return redirect(login)
    
    attendance_data = (
        Attendance.objects
        .filter(timestamp__date=date, course_id=course_id)
        .select_related('student')
    )
    course_info = Course.objects.values('course_code', 'course_name').get(id=course_id)
    total_absent_students = attendance_data.filter(status='absent').count()
    return render(request,'lecturer/attendance_report.html',{'attendance_data':attendance_data,'dates':date,'course_info':course_info,'total_absent':total_absent_students})




def studentAttendance(request):
    if not request.user.is_authenticated:
        return redirect('login')  

   
    # Retrieve the courses in which the student is enrolled
    enrolled_courses = Course.objects.filter(enrollment__student__user=request.user)

    # Retrieve timetable and attendance information for each enrolled course
    attendance_info = []
    
    for course in enrolled_courses:
        timetable_entries = Timetable.objects.filter(course=course).select_related('lecturer')
        attendance_entries = Attendance.objects.filter(student__user=request.user, course=course)

        total_sessions = attendance_entries.annotate(date=TruncDate('timestamp')).values('date').distinct().count()

        present_sessions = attendance_entries.filter(status='present').count()
        absent_sessions = total_sessions - present_sessions
        absent_percentage = (absent_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        attended_percentage = (present_sessions / total_sessions) * 100 if total_sessions > 0 else 0

        attendance_info.append({
            'course': course,
            'timetable_entries': timetable_entries,
            'attendance_entries': attendance_entries,
            'absent_percentage': round(absent_percentage, 2),
            'attended_percentage': round(attended_percentage, 2),
            'total_sessions': total_sessions,
        })

 
    return render(request,'student/studentAttendance.html', {'attendance_info': attendance_info})


def studentStatistic(request,course_id):
    
    if not request.user.is_authenticated:
        return redirect('login')  


    # Get timetable and attendance information for the specified course
    timetable_entries = Timetable.objects.filter(course_id=course_id)
    attendance_entries = Attendance.objects.filter(student__user=request.user, course_id=course_id)

    # Calculate total session count based on unique dates from attendance entries
    total_session = attendance_entries.annotate(date=TruncDate('timestamp')).values('date').distinct().count()

    # Calculate total absent sessions and absent percentage
    total_absent = attendance_entries.filter(status='absent').count()
    absent_percentage = (total_absent / total_session) * 100 if total_session > 0 else 0

    # Get class info from course id
    class_info = Course.objects.values('course_code', 'course_name', 'lecturer__first_name', 'lecturer__last_name').get(id=course_id)

    leave_check = Leave.objects.filter(
        attendance_id=OuterRef('pk'),
        status__in=['pending', 'approve']
    )
    # get attendance session by course
    attend_sessions = attendance_entries.annotate(
            date=TruncDate('timestamp'),
            has_leave_application=Exists(leave_check)
        ).values(
            'date', 
            'course__timetable__DayOfTheWeek', 
            'course__timetable__StartTime', 
            'course__timetable__EndTime', 
            'status',
            'id', 
            'has_leave_application'
        ).order_by('date')    
    # dd(has_leave_application)
    context = {
        'class_info': class_info,
        'total_session': total_session,
        'total_absent': total_absent,
        'absent_percentage': round(absent_percentage, 2),
        'attend_sessions': attend_sessions,
    }

    return render(request,'student/attendanceStatistic.html',context)


def leaveApplication(request,attendance_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    attendance =  get_object_or_404(Attendance,id=attendance_id)
    course = attendance.course
    form = LeaveForm()
    if  request.method =='POST':
        form = LeaveForm(request.POST,request.FILES)
        if form.is_valid():
            leave_application =  form.save(commit=False)
            leave_application.attendance = attendance
            leave_application.save()
            return redirect(index)
        
        else:
            form = LeaveForm()
        
    return render(request,'student/leaveApplication.html',{'form':form,'attendance':attendance,'course':course})

def leaveList(request):
    if not request.user.is_authenticated:
        return redirect(login)
    
    current_user  = request.user
    
    lecturer_course = current_user.lecturer.course_set.all()
    leaves  = Leave.objects.filter(attendance__course__in=lecturer_course)
    return render(request,'lecturer/leaveList.html',{'leaves':leaves})

def leaveApproval(request,leave_id):
    if not request.user.is_authenticated:
        return redirect(login)
    leave  = get_object_or_404(Leave,id=leave_id)
    form = LeaveApprovalForm(instance=leave)
    document_url = leave.document
    
    if request.method ==  'POST':
        form = LeaveApprovalForm(request.POST,instance=leave)
        if form.is_valid():
            form.save()
            if leave.leave_type == 'mc':
                leave.attendance.status = 'mc'
            elif leave.leave_type == 'el':
                leave.attendance.status = 'el'
            leave.attendance.save()
            return redirect(index)
        else:
            form = LeaveApprovalForm(instance=leave)
    return render(request,'lecturer/approveLeave.html',{'form':form,'leave':leave,'document_url':document_url})


def takingAttendance(request,course_id):
    if not request.user.is_authenticated:
        return redirect(login)  
    
    local_timezone = pytz.timezone('Asia/Kuala_Lumpur')

    utc_now = datetime.utcnow()
    local_now = datetime.now()
    
    # start of day & end of day in GMT+8 (local timezone)
    start_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = start_day + timedelta(days=1) - timedelta(microseconds=1)

    print("GMT8 Start Day:",start_day,"End Day:",end_day)

    #convert GMT+8 to utc timezone  
    # start_day_utc = start_day.astimezone(timezone.utc)
    # end_day_utc = end_day.astimezone(timezone.utc)
    
    course= get_object_or_404(Course,pk=course_id)
    attendance_record = Attendance.objects.filter(course=course, timestamp__range=(start_day, end_day))
    # dd(attendance_record)
    
    return render(request,'lecturer/takingAttendance.html',{'course':course,'attendance_record':attendance_record})


def get_realtime_data(request, course_id):
    
    local_timezone = pytz.timezone('Asia/Kuala_Lumpur')

    utc_now = datetime.utcnow()
    local_now = datetime.now()
    
    # start of day & end of day in GMT+8 (local timezone)
    start_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = start_day + timedelta(days=1) - timedelta(microseconds=1)
    
    
    #convert GMT+8 to utc timezone  
    # start_day_utc = start_day.astimezone(timezone.utc)
    # end_day_utc = end_day.astimezone(timezone.utc)
    
    course= get_object_or_404(Course,pk=course_id)
    attendance_record = Attendance.objects.filter(course=course, timestamp__range=(start_day, end_day))
    # dd(attendance_record)

    data = {
        'course_code': course.course_code,
        'course_name': course.course_name,
        'course_id':course.id,
        'attendance_record': [
            {'student_id': record.student.student_id,
             'name': f'{record.student.first_name} {record.student.last_name}', 
             'status': record.status,
             'timestamp':record.timestamp,
             'user_id':record.student.user_id}
            for record in attendance_record
        ],
    }

    return JsonResponse(data)

@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '')
        timestamp_str = request.POST.get('timestamp', '')
        new_status = request.POST.get('status', '')
        course_id = request.POST.get('courseId','')
        
        print("Received Data - Student ID:", student_id, "Timestamp:", timestamp_str, "New Status:", new_status,"Course ID",course_id)
        

        # date=TruncDate('timestamp')
        try:
            
            # local_now = datetime.now()
            # start_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            # end_day = start_day + timedelta(days=1) - timedelta(microseconds=1)
    
           
            # Convert the string to a datetime object
            datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            start_day = datetime_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_day = start_day + timedelta(days=1) - timedelta(microseconds=1)
            print ('start day',start_day,"end day",end_day)
            

            # Extract the date
            date = datetime_obj.date()
            # tz_kl = pytz.timezone('Asia/Kuala_Lumpur')
            # kl_time = date.replace(tzinfo=pytz.utc).astimezone(tz_kl)
            # print ('date',kl_time)

            # Assuming the timestamp is in the format "YYYY-MM-DD HH:mm:ss"
            attendance_obj = Attendance.objects.get(student_id=student_id, timestamp__date=date, course_id = course_id)
            print('Search Data From DB - Student_id:',attendance_obj.student_id,"Timestamp:",attendance_obj.timestamp,'Status',attendance_obj.status,'course',attendance_obj.course_id)
            # Update the status
        
            attendance_obj.status = new_status
            attendance_obj.save()

            return JsonResponse({'success': True})
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance record not found'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})


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



def studentUploadImages(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    
    
    form = DatasetImageForm()
    if request.method =='POST':

        form = DatasetImageForm(request.POST, request.FILES)
        if form.is_valid():
            currentUser=get_user_model().objects.get(id=request.user.id) #get login user 
            getUserStudent = get_object_or_404(Student,user_id=request.user.id) #get data from table main_student
            print('student:',getUserStudent)
            images = request.FILES.getlist('image')
            for image in images:
                DatasetImages.objects.create(student=getUserStudent, image=image)
            
            
            messages.success(request,f'Images sucessfully uploaded.')
            return redirect(studentUploadImages)

            
        else:
            form = DatasetImageForm()
            messages.error(request,f'Failed to upload images')

        
    return render(request,'student/studentImages.html',{'form':form})


