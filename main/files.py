from django.http import HttpResponse, JsonResponse
from .models import Attendance,Student,Course,Enrollment
from datetime import datetime,timedelta
from django.utils import timezone
import pytz
import requests

# https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests

def train_file(request):
    print("TRAIN")
    # import function to run
    from face_trainer import train_model
    
    # call function
    train_model.train()
    return JsonResponse({'ok':'true', 'status':'200'})

def recognize(request):
    try:
        url = 'http://raspberrypi.local:5000/face/recognize?course=courseid'
        requests.get(url,timeout=0.0000000001)
    except requests.exceptions.ReadTimeout: 
        return JsonResponse({'ok':'true', 'status':'200'})

def detect(request,name):
    course_id = request.GET.get('courseId', '')
    print("DETECT FACE")
    print(name, course_id)
    
    student=Student.objects.get(student_id=name)
    course=Course.objects.get(id=course_id)
    
    exist=Attendance.objects.filter(student=student,course=course).exists()
    
    if exist:
        
        logged=Attendance.objects.filter(student=student,course=course).values_list("timestamp","status")[0]
        datetime=logged[0]
        status=logged[1]
        
        print(datetime)
        print(status)
        
        local_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        # Convert UTC datetime to the local timezone
        local_logged = datetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        logged_date = '%s/%s/%s' % ( local_logged.day, local_logged.month, local_logged.year)
        print ("Extracted date:", logged_date)
        
        now = datetime.utcnow()
        
        local_now = now.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        now_date = '%s/%s/%s' % ( local_now.day, local_now.month, local_now.year)
        
        if (logged_date == now_date) and (status=='present'):
            print("Student logged")
        else:
            if status == 'absent':
                Attendance.objects.filter(student=student,course=course,timestamp=datetime).update(status='present')
    else:
        # Attendance.objects.create(student=student,course=course,status="present")
        return JsonResponse({'ok':'true', 'status':'200'})

    
    return JsonResponse({'ok':'true', 'status':'200'})

    
def upload_file(request, path="", insecure=False, **kwargs):
  print("UPLAOD FILE")
  
  url = 'http://raspberrypi.local:5000/upload/'
  filepath = 'C:\laragon\www\facial_recognition_flask\encodings.pickle'
  
  with open(filepath, 'rb') as f:
    requests.post(url, data=f)
  
  return JsonResponse({'ok':'true', 'status':'200'})

    
    
def populate_attendance(request):
    print('populate_attendance')
    
    course_id = request.GET.get('courseId', '')
    print(course_id)
    
    local_now = datetime.now()
    print("local now")
    print(local_now)
    # start of day & end of day in GMT+8 (local timezone)
    start_day = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = start_day + timedelta(days=1) - timedelta(microseconds=1)
    print("start day")
    print(start_day)
    
    print("end day")
    print(end_day)
    
    # start of day & end of day in GMT+8 (local timezone)
    # convert back to utc GMT0
    # value after converted utc, use in range
    
    # 1. check course id for today's date not yet populated
    ### populate student and course id for todays date (default absent)
    ### note: date in timerange, convert to GMT+8; get the start of day and end of day for today in GMT+8;
    ### timestamp__range=(startofday.toutc,endofday.toutc)
    ## if !populated 
    
    exist = Attendance.objects.filter(course=course_id, timestamp__range=(start_day, end_day)).exists()
    
    if not exist:
        students_enrolled = Enrollment.objects.filter(course=course_id).values_list('student_id', flat=True)

        for student_id in students_enrolled:
            student = Student.objects.get(user_id=student_id)
            print(student.student_id)
            Attendance.objects.create(course_id=course_id, student=student, timestamp=local_now, status='absent')
        
        return JsonResponse({'ok': 'true', 'status': '200'})
    
    # if already populated
    else:
        print("already populated")
        return JsonResponse({'ok': 'true', 'status': '200'})

