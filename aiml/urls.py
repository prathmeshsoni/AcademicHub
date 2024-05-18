"""
    aiml URL Configuration
    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/3.1/topics/http/urls/
    Examples :-
        -> Function views :
            1. Add an import:  from my_app import views
            2. Add a URL to urlpatterns:  path('', views.home, name='home')
        -> Class-based views :
            1. Add an import:  from other_app.views import Home
            2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
        -> Including another URLconf :
            1. Import the include() function: from django.urls import include, path
            2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.views.static import serve

from User.views import admin_side, get_user


def check_logger(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if request.session.get('userid'):
                if int("".join(request.path.split('.html')[0].split('_')[-1])) == int(request.session.get('userid')) \
                        or request.session.get('access') \
                        or request.session.get('type') == "faculty":
                    return view_func(request, *args, **kwargs)

            enroll = request.session.get('userid')
            if not request.META.get('HTTP_REFERER'):
                messages.success(
                    request, 'Denied entry! You took a Wrong Turn.....!')
                if enroll:
                    return redirect(f'/{enroll}/')
                else:
                    return redirect(f'/login/?next={request.path}')
        except:
            pass
        if "/".join(request.path.split('.txt')[0].split('/')[:-1]) == '/uploads/logs':
            if not get_user(request, 0):
                if request.session.get('enrollment'):
                    messages.success(request, 'Denied entry! You took a Wrong Turn.....!')
                    return redirect(f"/{request.session.get('enrollment')}/")
                else:
                    return redirect(f'/login/?next={request.path}')
            else:
                return view_func(request, *args, **kwargs)
        else:
            return view_func(request, *args, **kwargs)

    return wrapper


@check_logger
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_side/', admin_side),
    path('', include('Notification.urls')),
    path('', include('category.urls')),
    path('', include('User.urls')),
    re_path(r'^uploads/(?P<path>.*)$', protected_serve, {'document_root': settings.MEDIA_ROOT}),
]

handler404 = "User.views.page_not_found_view"
handler403 = "User.views.page_not_1"
handler500 = "User.views.page_not_2"
handler503 = "User.views.page_not_3"
handler400 = "User.views.page_not_4"
handler405 = "User.views.page_not_5"
handler410 = "User.views.page_not_6"
