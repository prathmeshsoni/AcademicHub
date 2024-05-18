from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'User'

    def ready(self):
        try:
            from User.models import SendMailModel
            from User.mail import server_start

            obj = SendMailModel.objects.all()
            if obj.__len__() == 0:
                obj = SendMailModel.objects.create()
            else:
                obj = obj[0]
                if obj.server_start:
                    return

            server_start()
            obj.server_start = True
            obj.save()
        except:
            pass
