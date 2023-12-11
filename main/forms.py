from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Profile
from main.models import User, Profile,Student,Lecturer,Course,Timetable, DatasetImages
from django.forms import ModelForm



class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    student_id =forms.CharField(widget=forms.TextInput())
    
    class Meta(UserCreationForm.Meta):
        model= User
        fields= ('username','email','password1','password2','first_name','last_name')
    @transaction.atomic
    def save(self,commit =True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
            student = Student.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'), student_id=self.cleaned_data.get('student_id'))
            return user


class LecturerSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    
    class Meta(UserCreationForm.Meta):
        model= User
        fields= ('username','email','password1','password2','first_name','last_name')
    @transaction.atomic
    def save(self,commit =True):
        user = super().save(commit=False)
        user.is_lecturer = True
        if commit:
            user.save()
            lecturer = Lecturer.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))
            return user

class editUserProfile(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    email= forms.EmailField(widget=forms.EmailInput())
    username = forms.CharField(widget=forms.TextInput())
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email']
    @transaction.atomic
    def save(self,commit = True):
        user = super().save(commit=False)
        if user.is_lecturer == True:
            if commit:
                user.save()
                lecturer = Lecturer.objects.update(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))

        if user.is_student ==True:
             if commit:
                user.save()
                student = Student.objects.update(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'), student_id=self.cleaned_data.get('student_id'))

        return user
            

class addCourseForm(forms.ModelForm):
    course_code = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    course_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    credit_hours = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-input'}))
    lecturer_id = forms.CharField(widget=forms.TextInput)
    class Meta:
        model = Course
        fields = ['course_code','course_name','credit_hours','lecturer_id']


class addTimetableForm(forms.ModelForm):
    DayOfTheWeek = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    course_id = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    start_time = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    end_time = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    lecturer_id = forms.CharField(required=False)
    
    class Meta: 
        model = Timetable
        fields =['DayOfTheWeek','course_id','start_time','end_time','lecturer_id']
    


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class UploadImage(forms.ModelForm):

  

    class Meta:
        model = User
        fields=['profile_picture']
        
    # @transaction.atomic
    # def save(self,commit = True):
    #     user = super().save(commit=False)
    #     # if user.is_lecturer == True:
    #     #     if commit:
    #     #         user.save()
    #     #         lecturer = Lecturer.objects.update(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))

    #     if user.is_student ==True:
    #          if commit:
    #             user.save()
    #             student = Student.objects.update(user=user, profile_picture =self.cleaned_data.get('profile_picture') )

    #     return user
    
# class UpdateUserForm(forms.ModelForm): 
#     username = forms.CharField(max_length=100, required=True,widget=forms.TextInput(attrs={'class':'form-input'}))
#     email = forms.EmailField(required=True,widget=forms.TextInput(attrs={'class':'form-input'}))
#     class Meta: 
#         models = User
#         fields = ['username','email']
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields=['username','email']
    
        
class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class':'form-control-file'}))
    class Meta:
        models = Profile
        fields = ['avatar']

    
class DatasetImageForm(forms.ModelForm):
    class Meta:
        model= DatasetImages
        fields = ['image']