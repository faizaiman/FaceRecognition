from django.http import HttpResponse, JsonResponse
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
        url = 'http://raspberrypi.local:5000/face/recognize'
        requests.get(url,timeout=0.0000000001)
    except requests.exceptions.ReadTimeout: 
        return JsonResponse({'ok':'true', 'status':'200'})

def detect(request,name):
    print("DETECT FACE")
    print(name)
    return JsonResponse({'ok':'true', 'status':'200'})
    
def upload_file(request, path="", insecure=False, **kwargs):
  print("UPLAOD FILE")
  
  url = 'http://raspberrypi.local:5000/upload/'
  filepath = 'C:\laragon\www\facial_recognition_flask\encodings.pickle'
  
  with open(filepath, 'rb') as f:
    requests.post(url, data=f)
  
  return JsonResponse({'ok':'true', 'status':'200'})
