import google.auth.transport.requests
import json
import os
import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from google.oauth2 import service_account

from User.models import Profile, timedelta

BASEURL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NotificationTokenModel(models.Model):
    token = models.TextField(max_length=5000)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='user_notification_token')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        if self.user:
            return f'{time} | {self.user.name} - {self.user.username}'
        else:
            return f'{time} | Unknown User'


class NotificationModel(models.Model):
    title = models.CharField(max_length=100)
    msg = models.TextField(max_length=1000)
    token = models.ForeignKey(NotificationTokenModel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        if self.token.user:
            return f'{time} | {self.title} - {self.msg} - {self.token.user.name}'
        else:
            return f'{time} | {self.title} - {self.msg} - Unknown User'


# Get Access Token
def _get_access_token():
    """
        Retrieve a valid access token that can be used to authorize requests.
        return: Access token.
    """

    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

    credentials = service_account.Credentials.from_service_account_file(
        f'{BASEURL}/Notification/Notification.json', scopes=SCOPES)

    request = google.auth.transport.requests.Request()
    credentials.refresh(request)

    return credentials.token


# Send Notification To Particular User
def send_notification(message_title, message_desc, registration_ids):
    json_data = open(f'{BASEURL}/Notification/Notification.json').read()
    data = json.loads(json_data)

    PROJECT_ID = data['project_id']

    url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'

    headers = {'Authorization': 'Bearer ' + _get_access_token(), 'Content-Type': 'application/json; UTF-8', }

    payload = {"message": {"token": registration_ids, "notification": {"body": message_desc, "title": message_title, }}}

    requests.post(url, data=json.dumps(payload), headers=headers)


# Send Notification After Save Notification Model In Admin Panel
@receiver(post_save, sender=NotificationModel)
def Send_Notification_receiver(sender, instance, created, **kwargs):
    try:
        send_notification(instance.title, instance.msg, instance.token.token)
    except Exception as e:
        if not os.path.exists(f'{BASEURL}/uploads/Notification'):
            os.makedirs(f'{BASEURL}/uploads/Notification')
        try:
            with open(f'{BASEURL}/uploads/Notification/notification_error.txt', 'a') as f:
                f.write(f'{e}\n')

        except:
            with open(f'{BASEURL}/uploads/Notification/notification_error.txt', 'w') as f:
                f.write(f'{e}\n')
