from django.contrib import admin

from .models import *

admin.site.register(NotificationModel)
admin.site.register(NotificationTokenModel)
