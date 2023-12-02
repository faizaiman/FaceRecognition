from django.http import HttpResponse, JsonResponse
from .models import Attendance,Student,Course,Enrollment
from datetime import datetime
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
        Attendance.objects.create(student=student,course=course,status="present")
    
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
    
    # Attendance.objects.filter(course=course_id,timestamp__range=())
    
    # 1. check course id for todays date not yet populated
    ## if !populated
    ### populate student and course id for todays date (default absent)
    
    ## if populated
    ### return
    
    # student=Student.objects.get(student_id=name)
    # course=Course.objects.get(id=course_id)
    
    return JsonResponse({'ok':'true', 'status':'200'})
