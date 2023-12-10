from django.urls import path,include
from django.contrib import admin
from . import views,files
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login),
    path('login', views.login,name='login'),
    path('dj-admin',admin.site.urls),
    path('logout/', views.logout),
    path('accountSetting/<id>/',views.editProfile,name= 'edit-profile'),
    path('uploadImage/',views.uploadImage,name="upload-image"),
    path('index',views.index, name='index'),
    path('register',views.register, name='registration'),
    path('addLecturer/',views.addLecturer, name='addLecturer'),
    path('addCourse/',views.addCourse),
    path('profile/',views.profile,name='users-profile'),
    path('lecturer/',views.viewLecturer),
    path('course/',views.viewCourse),
    path('course/<id>',views.editCourse,name= 'edit-course'),
    path('delete/<id>',views.deleteCourse,name= 'delete-course'),
    path('lecturerE/<id>',views.editLecturer,name= 'edit-lecturer'),
    path('deleteE/<id>',views.deleteLecturer,name= 'delete-lecturer'),
    path('MySubject/',views.mySubject),
    path('viewSubject/',views.ViewASubject),
    path('registerSubject/(?P<id>\d+)(?:/(?P<uid>\d+))?',views.registerSubject,name= 'register-subject'),
    path('dropSubject/(?P<id>\d+)',views.dropSubject,name= 'drop-subject'),
    path('viewTimetable',views.viewTimetable),
    path('addTimetable',views.addTimetable),
    path('timetable/<id>',views.editTimetable,name= 'edit-timetable'),
    path('deleteT/<id>',views.deleteTimetable,name='delete-timetable'),
    path('viewClass',views.ViewClass),
    path('viewAttendance',views.viewAttendance),
    path('attendanceSessions/<id>',views.attendanceSessions,name='attendance-sessions'),
    path('attendanceReport/<str:date>/<int:course_id>/',views.attendanceReport,name='attendance-report'),
    path('studentAttendance',views.studentAttendance,name='student-attendance'),    
    path('attendanceStatistic/<int:course_id>/',views.studentStatistic,name='attendance-statistic'),
    path('takingAttendance/courseId=<int:course_id>/', views.takingAttendance, name='taking-attendance'),
    path('get_realtime_data/courseId=<int:course_id>/', views.get_realtime_data, name='get-realtime-data'),
    path('update-status/', views.update_status, name='update-status'),
    path('studentUploadImages/',views.studentUploadImages,name='student-images'),
    
    
    
    path('upload',files.upload_file),
    path('train',files.train_file,name="train"),
    path('recognize',files.recognize,name ="recognize"),
    # path('detect/<name>/',files.detect,name="detect"),
    path('detect/<name>/',files.detect,name="detect"),

    path('populate_attendance/',files.populate_attendance)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
