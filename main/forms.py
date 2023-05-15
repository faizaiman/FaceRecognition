from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.fields import EmailField
from django.forms.forms import Form

from vristo import settings
from main.models import User

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    username = forms.CharField(max_length=101)
    mail = forms.EmailField(max_length=254)
    role = forms.CharField(max_length=32)
    image = forms.ImageField(max_length=128)
    student_id = forms.CharField(max_length=128)

# class UserRegisterForm(UserCreationForm):
#     # fields we want to include and customize in our form
#     first_name = forms.CharField(max_length=100,
#                                  required=True,
#                                  widget=forms.TextInput(attrs={'placeholder': 'First Name',
#                                                                'class': 'form-control',
#                                                                }))
#     last_name = forms.CharField(max_length=100,
#                                 required=True,
#                                 widget=forms.TextInput(attrs={'placeholder': 'Last Name',
#                                                               'class': 'form-control',
#                                                               }))
#     username = forms.CharField(max_length=100,
#                                required=True,
#                                widget=forms.TextInput(attrs={'placeholder': 'Username',
#                                                              'class': 'form-control',
#                                                              }))
#     email = forms.EmailField(required=True,
#                              widget=forms.TextInput(attrs={'placeholder': 'Email',
#                                                            'class': 'form-control',
#                                                            }))
#     password1 = forms.CharField(max_length=50,
#                                 required=True,
#                                 widget=forms.PasswordInput(attrs={'placeholder': 'Password',
#                                                                   'class': 'form-control',
#                                                                   'data-toggle': 'password',
#                                                                   'id': 'password',
#                                                                   }))
#     password2 = forms.CharField(max_length=50,
#                                 required=True,
#                                 widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
#                                                                   'class': 'form-control',
#                                                                   'data-toggle': 'password',
#                                                                   'id': 'password',
#                                                                   }))

#     class Meta:
#         model = User
#         fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']
       

    