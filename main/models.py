from django.db import models
from django.forms import ModelForm
# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=101)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    e_mail=models.EmailField(max_length=254)
    role = models.CharField(max_length=32, default="Student")
    image = models.ImageField(upload_to='main/profile', name="Image")
    student_id = models.CharField(max_length=128)
    

class Image(models.Model):
    id = models.IntegerField(name='ID',unique=True,primary_key=True,editable=True)
    image = models.ImageField(name='Image')
    user = models.ForeignKey('User',on_delete=models.CASCADE)
    
class UserForm(ModelForm):
    class Meta: 
        model = User
        exclude = ['id']
        
    def is_valid(self):
        return True
    
class ImageForm(ModelForm):
    class  Meta:
        model = Image
        exclude = ['id']