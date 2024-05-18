from django.http import HttpResponse
from django.shortcuts import redirect

from User.views import get_student, JsonResponse, logger_send
from .models import *


def save_token(obj, token_val, user_obj):
    obj.token = token_val
    obj.user = user_obj
    obj.save()


def dynamic_token(val_obj, token_val, user_obj):
    if val_obj.user:
        if val_obj.user == user_obj and token_val == val_obj.token:
            return 0
        else:
            notification_obj = NotificationTokenModel()
            save_token(notification_obj, token_val, user_obj)
            return 1

    else:
        notification_obj = val_obj
        save_token(notification_obj, notification_obj.token, user_obj)
        return 1


# Get Notification Token and Save It
def send_token(request):
    if request.method == 'POST':
        user = request.session.get('enrollment')
        if user:
            user_obj = get_student(request)
            token_val = request.POST.get('token')
            check = NotificationTokenModel.objects.filter(token=token_val)
            if check:
                if len(check) >= 2:
                    val_list = []
                    for i in check:
                        val = dynamic_token(i, token_val, user_obj)
                        val_list.append(val)

                    val = 'ok' if 1 in val_list else 'done'
                    return JsonResponse({'status': val})

                else:
                    checks = dynamic_token(check.first(), token_val, user_obj)
                    val = 'ok' if checks == 1 else 'done'
                    return JsonResponse({'status': val})

            if not NotificationTokenModel.objects.filter(user=user_obj, token=token_val).first():
                notification_obj = NotificationTokenModel()
                save_token(notification_obj, token_val, user_obj)

                a = {'status': 'ok'}
                return JsonResponse(a)
        else:
            token_val = request.POST.get('token')
            if not NotificationTokenModel.objects.filter(token=token_val).first():
                notification_obj = NotificationTokenModel()
                save_token(notification_obj, token_val, notification_obj.user)

                a = {'status': 'ok'}
                return JsonResponse(a)

    if request.is_ajax():
        a = {'status': 'done'}
        return JsonResponse(a)
    else:
        logger_send(request, 'Seen request from network')
        return redirect('/')


# Request For Show Firebase JS
def showFirebaseJS(request):
    """
        Replace the firebaseConfig with your own firebaseConfig.
        You can get the firebaseConfig from the Firebase Console.
    """

    data = 'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
           'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
           'var firebaseConfig = {' \
           '        apiKey: "",' \
           '        authDomain: "",' \
           '        databaseURL: "",' \
           '        projectId: "",' \
           '        storageBucket: "",' \
           '        messagingSenderId: "",' \
           '        appId: "",' \
           '        measurementId: ""' \
           ' };' \
           'firebase.initializeApp(firebaseConfig);' \
           'const messaging=firebase.messaging();' \
           'messaging.setBackgroundMessageHandler(function (payload) {' \
           '    console.log(payload);' \
           '    const notification=JSON.parse(payload);' \
           '    const notificationOption={' \
           '        body:notification.body,' \
           '        icon:notification.icon' \
           '    };' \
           '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
           '});'

    return HttpResponse(data, content_type="text/javascript")
