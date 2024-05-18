from django.urls import path

from . import views

urlpatterns = [
    path('send_token/', views.send_token),
    path('firebase-messaging-sw.js', views.showFirebaseJS, name="show_firebase_js"),
]
