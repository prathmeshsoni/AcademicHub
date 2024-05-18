from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('developed-by/', views.developed_by),
    path('<str:name>/<str:social>/link/', views.social_link),

    path('site-tour/', views.site_tour, name='site-tour'),
    path('robots.txt', views.robots_txt, name='robots.txt'),

    path('history/', views.history),
    path('history/<int:history_id>/', views.history_detail),
    path('hiii/', views.logs_temp),

    path('register/', views.register),
    path('faculty/register/', views.register_faculty),
    path('login/', views.login, {'template_name': 'login.html', 'ksy': 'student'}),
    path('faculty/login/', views.login, {'template_name': 'login_faculty.html', 'ksy': 'faculty'}),
    path('verify/<auth_token>/', views.verify, name="verify"),
    path('forgot/', views.password_forgot),
    path('change/', views.password_change),
    path('reminder/', views.password_reminder),
    path('logout/', views.logout),

    path('profile/', views.set_username),
    path('student/profile/', views.student_profile),
    path('faculty/profile/', views.faculty_profile),

    path('contact/', views.contact),

    path('confession/', views.confession_add),
    path('confession/views/', views.confession_view),
    path('get_confession/', views.get_confession),
    path('add_like/', views.add_like),
    path('add_comment/', views.add_comment),
    path('delete_comment/', views.delete_comment),

    path('upload/', views.upload),
    path('upload/rollno/', views.upload_roll_no),
    path('download-csv/', views.download_csv),
    path('verification/', views.verify_data),
    path('verification/rollno/', views.verify_data_div_list),
    path('verification/delete/', views.verify_data_delete),
    path('update_item/<int:item_id>/', views.update_item, name='update_item'),

    path('students/', views.student_view),
    path('faculties/', views.faculty_view),

    path('branch/', views.branch_view),
    path('subject/', views.subject_view),

    path('<str:enroll>/', views.student_data),
    path('<str:branch>/<str:hid>/', views.student_branch_data),
    path('<str:branch>/<str:name>/<str:sem>/', views.branch_data_1),
    path('<str:branch>/<str:name>/<int:sem>/<str:batch>/', views.branch_data_2),
    path('<str:sem>/<str:branch>/<str:subject>/<str:mse>/', views.subject_request_1),
    path('<str:sem>/<str:branch>/<str:subject>/<str:mse>/<int:batch>/', views.subject_request_2),
]
