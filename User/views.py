import json
import math
import os
import uuid
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login as login_user, logout as logout_user
from django.db.models import Count, Sum, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from threading import Thread

from User.convert_pdf_csv import Final_csv
from User.forms import *
from .mail import send_mail

base_path_server = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}//'
main_domain = 'http://127.0.0.1:8000'

"""
######################################################################################################################
-->                                         Exception Handling Start
"""


def page_not_found_view(request, exception):
    if request.session.get('enrollment'):
        logger(request, request.session['enrollment'], '404')

    return render(request, '404.html', {'key': 404}, status=404)


def page_not_1(request, exception):
    return render(request, '404.html', {'key': 403}, status=404)


def page_not_2(request):
    return render(request, '404.html', {'key': 500}, status=404)


def page_not_3(request):
    return render(request, '404.html', {'key': 503}, status=404)


def page_not_4(request, exception):
    return render(request, '404.html', {'key': 400}, status=404)


def page_not_5(request):
    return render(request, '404.html', {'key': 405}, status=404)


def page_not_6(request):
    return render(request, '404.html', {'key': 410}, status=404)


"""
-->                                         Exception Handling End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                            DashBoard Start
"""


# Request For Index Page
def home(request):
    logger_send(request)
    user_name = ''
    try:
        obj = get_profile(request.session.get('userid'))
        user_name = " ".join(obj.name.split(' ')[:2]).title()
        messages.success(request, f'Welcome {user_name}.....!')
    except:
        try:
            obj = get_student(request)
            user_name = " ".join(obj.name.split(' ')[:2]).title()
            messages.success(request, f'Welcome {user_name}.....!')
            user_name = f'{user_name} (Faculty)'
        except:
            pass
    items = {
        'sid': 'home',
        'vname': f'DashBoard',
        'user_name': user_name,
    }
    return render(request, 'home.html', items)


"""
-->                                            DashBoard End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                       Developed By & Social Link Start
"""


# Request For Developed By
def developed_by(request):
    logger_send(request)
    developed_obj = DevelopedByModel.objects.filter(is_deleted=False)
    developed_gallery_obj = DevelopedGalleryModel.objects.filter(is_deleted=False)

    items = {
        'developed_by': developed_obj,
        'developed_gallery_obj': developed_gallery_obj,
        'sid': 'developed-by',
        'vname': f'Developed By',
    }
    return render(request, 'developed_by.html', items)


# Request For Social Link
def social_link(request, name, social):
    logger_send(request)
    try:
        developed_obj = DevelopedByModel.objects.get(short_name__iexact=name)
    except:
        return redirect('/developed-by/')

    social = social.lower()
    if social == 'linkedin':
        return redirect(developed_obj.linkedin)
    elif social == 'instagram':
        return redirect(developed_obj.instagram)
    else:
        return redirect('/developed-by/')


"""
-->                                       Developed By & Social Link Start
######################################################################################################################
"""

"""
######################################################################################################################
-->                                         Site Structure Start
"""


# Request For Site Tour Page
def site_tour(request):
    items = {
        'sid': 'structure',
        'vname': f'Website Structure',
    }
    logger_send(request)
    return render(request, 'site_tour.html', items)


# Request For Site Tour Page
def robots_txt(request):
    logger_send(request)
    return render(request, 'robots.html', content_type="text/plain; charset=utf-8")


"""
-->                                         Site Structure End
######################################################################################################################
"""

"""
######################################################################################################################
-->                     Custom Decorator For Login User, Not Login User & Special User Start
"""


def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        logger_send(request)
        name = request.session.get('userid')
        if not name:
            messages.error(request, 'First You Need to Login')
            if request.path != '/favicon.ico/':
                request.session['next_url'] = request.path
                next_url = '/login/?next=' + request.path
            else:
                next_url = '/login/'

            return redirect(next_url)

        return view_func(request, *args, **kwargs)

    return wrapper


def custom_login_required_not(view_func):
    def wrapper(request, *args, **kwargs):
        logger_send(request)
        name = request.session.get('userid')
        if name:
            if request.session.get('type'):
                next_url = '/branch/'
            else:
                next_url = f'/{name}/'

            return redirect(f'{next_url}')

        return view_func(request, *args, **kwargs)

    return wrapper


def history_access(view_func):
    def wrapper(request, *args, **kwargs):
        name = request.session.get('userid')
        if request.session.get('access'):
            logger(request, name, '')
            return view_func(request, *args, **kwargs)
        else:
            logger_send(request, 'Denied Entry')
            if name:
                if 3 < request.path.split('/').__len__():
                    path = request.path.split('/')[1]
                    if path.lower() == 'upload' or path.lower() == 'verification':
                        messages.success(request, 'Denied Entry! You took a Wrong Turn.....!')
                else:
                    path = name
                    messages.success(request, 'Denied Entry! You took a Wrong Turn.....!')
                return redirect(f'/{path}/')
            else:
                messages.success(request, 'First You Need to Login')
                if request.path != '/favicon.ico/':
                    request.session['next_url'] = request.path
                    next_url = '/login/?next=' + request.path
                else:
                    next_url = '/login/'

                return redirect(f'{next_url}')

    return wrapper


"""
-->                     Custom Decorator For Login User, Not Login User & Special User End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                             Manage User Logs Start
"""


def logger_send(request, text=None):
    if not text:
        if request.session.get('enrollment'):
            logger(request, request.session['enrollment'], '')
        else:
            logger(request, '', '')
    else:
        if request.session.get('enrollment'):
            logger(request, request.session['enrollment'], f'{text}')
        else:
            logger(request, '', f'{text}')


# save logs in txt file
def logger(request, enrollment, status, email=None, path=None, filename_s=None):
    if request.method == 'POST' and not status:
        return
    if status:
        if not status.isascii():
            status = "lovedee"
    if not email:
        email = request.session.get('email')
    try:
        try:
            if 'uploads/results' in request.META['HTTP_REFERER']:
                return
        except:
            pass
        if not path:
            path = request.path
        # if '/nasa/' in path:
        if request.META.get('QUERY_STRING'):
            path = f"{path}?{request.META.get('QUERY_STRING')}"
        if '/favicon.ico/' in request.path:
            request.session['favicon'] = 1
            path = request.META['HTTP_REFERER'].replace('https://cse-aiml.live', '')
        if request.session.get('favicon') and request.path == '/':
            del request.session['favicon']
            return

        user_id = Profile.objects.filter(username=enrollment, email=email).first()
        current_time = (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        file_name = f'not_in_session.txt'
        if filename_s:
            file_name = f'{filename_s}.txt'
        if not user_id:
            if not enrollment:
                if not status:
                    msg = f'[{current_time}] Unknown | {request.method} https://cse-aiml{path}\n'
                else:
                    msg = f'[{current_time}] Unknown | {request.method} https://cse-aiml{path} | {status}\n'

                if not os.path.exists(f'{base_path_server}uploads/logs'):
                    os.makedirs(f'{base_path_server}uploads/logs')

                try:
                    with open(f'{base_path_server}uploads/logs/{file_name}', 'a') as f:
                        f.write(msg)
                except:
                    with open(f'{base_path_server}uploads/logs/{file_name}', 'w') as f:
                        f.write(msg)
            return
        if not status:
            msg = f'[{current_time}] {enrollment} | {request.method} https://cse-aiml{path}\n'
        else:
            msg = f'[{current_time}] {enrollment} | {request.method} https://cse-aiml{path} | {status}\n'
        file_name = f'{user_id.id}.txt'
        if filename_s:
            file_name = f'{filename_s}.txt'

        file_path = f'{base_path_server}uploads/logs'

        if not os.path.exists(file_path):
            os.makedirs(file_path)
        try:
            with open(f'{file_path}/{file_name}', 'a') as f:
                f.write(msg)
        except:
            pass
            # with open(f'{file_path}/{file_name}', 'w') as f:
            #     f.write(msg)
    except Exception as e:
        logger(request, '', f'{e} | Log_error', filename_s='log_error')


# Request For History
@history_access
def history(request):
    profile_list = []
    profile_list_1 = []
    # Change Server
    folder_path = f'{base_path_server}uploads/logs'
    # folder_path = f'{base_path_pc}uploads\\logs'

    profile_all = Profile.objects.all()

    file_path_not = f'{folder_path}/not_in_session.txt'
    with open(file_path_not, 'r') as f:
        data = f.read()
        datas_not = data.split('\n')
        f.close()

    text_not = datas_not[-2]
    modification_not = text_not.split(']')[0].replace('[', '')

    for profile in profile_all:
        try:
            file_name = f'{profile.id}.txt'
            file_path = f'{folder_path}/{file_name}'
            profile.created_at = (profile.created_at + timedelta(hours=5, minutes=30)).strftime(
                "%d/%b/%y %I:%M %p")
            # profile.div = k.division
            # profile.branch = k.branch
            profile.email = profile.email.replace('@gmail.com', '')
            # profile.roll_no = k.roll_no
            profile.name = profile.name.title()
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = f.read()
                    datas = data.split('\n')
                    f.close()

                text = datas[-2]
                modification_time = text.split(']')[0].replace('[', '')

                profile.modified = str(modification_time)
                profile_list.append(profile)
            else:
                profile.modified = ''
                profile_list_1.append(profile)
        except:
            pass

    sorted_profiles = sorted(profile_list, key=lambda x: datetime.strptime(x.modified, "%d/%b/%y %I:%M %p"),
                             reverse=True)
    sorted_profiles_1 = sorted(profile_list_1, key=lambda x: datetime.strptime(x.created_at, "%d/%b/%y %I:%M %p"),
                               reverse=True)
    final_data = sorted_profiles + sorted_profiles_1
    for i in range(len(final_data)):
        final_data[i].h_id = final_data[i].id
        final_data[i].id = i + 1

    check_not = 0

    items = {
        'profile_list': final_data,
        'hid': 'AIML',
        'sid': 'history',
        'vname': f'history',
        'historys': 'no',
        'modified_not': modification_not,
    }

    return render(request, 'history.html', items)


# Request For History Detail
@history_access
def history_detail(request, history_id):
    if history_id == 0:
        profile = Profile.objects.filter(id=history_id)
        profile.id = 0
        profile.username = 'Not In Session'
        file_name = f'not_in_session.txt'
    else:
        try:
            profile = Profile.objects.get(id=history_id)
            file_name = f'{profile.id}.txt'
        except:
            return redirect('/history/')

    # Change Server
    file_path = f'{base_path_server}uploads/logs/{file_name}'
    # file_path = f'{base_path_pc}uploads\\logs\\{file_name}'

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = f.read()
            datas = data.split('\n')
            f.close()
    else:
        return redirect('/history/')

    text = datas[-2]
    modification_time = text.split(']')[0].replace('[', '')
    profile.modified = modification_time
    try:
        main_obj = get_profile(profile.username)
        profile.created_at = (profile.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        profile.div = main_obj.division
        profile.roll_no = main_obj.roll_no
        roll_no = main_obj.roll_no
    except:
        roll_no = 0
        pass

    final_data = []
    for data_ in datas:
        try:
            time = data_.split(']')[0].replace('[', '')
            check = data_.split('|', 1)[1].split('|', 2)
            path_method = check[0].strip().replace('https://cse-aiml', '').replace('.live', '').split(' ', 1)
            method = path_method[0]
            path = path_method[1]
            if len(check) > 1:
                if len(check) == 2:
                    error_value = ''
                else:
                    error_value = check[1].strip()
                error_name = check[-1].strip()
            else:
                error_value = ''
                error_name = ''
            final_data.append({
                'count': len(final_data) + 1,
                'time': time,
                'path': path,
                'method': method,
                'error_value': error_value,
                'error_name': error_name
            })
        except:
            pass

    items = {
        'profile_obj': profile,
        'data': final_data,
        'hid': 'AIML',
        'sid': 'history',
        'vname': f'history - {profile.username} - {roll_no}',
        'historys_': 'no'
    }
    return render(request, 'history-detail.html', items)


# Search Logs Ranking System
def logs_temp(request):
    if request.method == 'POST':
        try:
            massage = request.POST.get('data').strip()
            massage = massage.strip()
            if not massage:
                return JsonResponse({})

            try:
                text = request.META['HTTP_REFERER'].replace('https://cse-aiml.live', '')
            except:
                text = ''

            logger(request, request.session.get('enrollment'), f'{massage} | Search Logs', path=text)
            return JsonResponse({})
        except:
            return JsonResponse({})

    else:
        logger_send(request)
        return redirect('/')


"""
-->                                             Manage User Logs End
######################################################################################################################
"""

"""
######################################################################################################################
-->                     User Authentication, Account Creation, Password Reset, Activity etc Start
"""


# Login Super User To Admin Panel
@history_access
def super_user_login(request):
    login_user(request, User.objects.get(username='admin'))


# Redirect To Admin Panel
def admin_side(request):
    if StudentDataModel.objects.all().__len__() == 0:
        login_user(request, User.objects.get(username='admin'))
    else:
        super_user_login(request)

    return redirect('/admin/')


# Get Student Information From StudentDataModel
def get_profile(username):
    profile_obj = StudentDataModel.objects.get(enrollment_number=username)
    return profile_obj


# Get User Information From ProfileModel
def get_student(request):
    obj = Profile.objects.get(username=request.session.get('enrollment'),
                              email=request.session.get('email'))
    return obj


# Request For Get User is access or not
def get_user(request, check):
    try:
        access = AccessModel.objects.get(
            user__username=request.session.get('userid'),
            user__email=request.session.get('email')
        )
    except:
        access = None
    if check == 0:
        if access:
            return True
        else:
            return False
    else:
        s_type = request.session.get('type')
        if s_type == 'faculty':
            return True
        elif access:
            return True
        else:
            return False


# Get Student Roll No From Different Sem
def actualroll_pro(username, sem=None):
    if sem:
        profile_obj = ActualRollNoModel.objects.get(student__enrollment_number=username, sem__sem_name=sem)
    else:
        profile_obj = ActualRollNoModel.objects.get(student__enrollment_number=username)
    return profile_obj


# Get Number Of Faculty
def return_three_digit_len(number):
    if len(str(number)) == 1:
        return f'00{number}'
    elif len(str(number)) == 2:
        return f'0{number}'
    else:
        return number


# Password Generator
def password_generator():
    import random
    import string
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return password


# Request For User Register
@custom_login_required_not
def register(request):
    if request.method == 'POST':
        try:
            name_ = request.POST.get('username').lower().strip().replace(' ', '')
            username = request.POST.get('enroll')
            email = request.POST.get('email')
            email = email.lower().strip()
            password = password_generator()

            if username.isascii() == False or email.isascii() == False or password.isascii() == False or name_.isascii() == False:
                logger(request, '', f'Proper_Details')

                msg = 'Please Enter Proper Details.....!'
                a = {'status': True, 'create': 'details_error', 'msg': msg}
                return JsonResponse(a)

            if len(username) != 12:
                if request.session.get('enrollment'):
                    if int(username) != int(request.session.get('enrollment')):
                        logger(request, request.session.get('enrollment'), f'{username} | not size 12')
                else:
                    logger(request, '', f'{username}:{email} | wrong_enrollment')

                msg = 'Please Enter Current Enrollment Number.....!'
                a = {'status': True, 'create': 'enroll_error_len', 'msg': msg}
                return JsonResponse(a)
            try:
                int(username)
            except:
                if request.session.get('enrollment'):
                    if int(username) != int(request.session.get('enrollment')):
                        logger(request, request.session.get('enrollment'), f'{username} | Not in int')

                msg = 'Please Enter Current Enrollment Number.....!'
                a = {'status': True, 'create': 'enroll_error_int', 'msg': msg}
                return JsonResponse(a)

            try:
                student_obj = get_profile(username)
                name = " ".join(student_obj.name.split(' ')[:2])
            except:
                logger_send(request, f'{username}:{email} | wrong_enrollment')
                logger(request, request.session.get('enrollment'), f'{username} | wrong_enrollment',
                       filename_s='contacts')

                msg = 'The Current Enrollment Number Is Not Found. If You Are Not a Second-year or Third-year Student, Then Please <a href="/contact/" style="color: #247bf6; font-size: 15px; font-weight: 600;">Contact Us</a>.....!'
                a = {'status': True, 'create': 'enroll_error_len', 'msg': msg}
                return JsonResponse(a)

            if not email.endswith('@gmail.com'):
                logger_send(request, f'{username}:{email} | email_error')

                msg = 'Please Enter Proper Email Address.....!'
                a = {'status': True, 'create': 'email_error', 'msg': msg}
                return JsonResponse(a)

            try:
                temp_obj = Profile.objects.filter(username=username, email=email).first()
                if temp_obj:
                    msg = 'Account Already Created, We Have Already Sent You An Email With Login Link, Please Check Your Email.....!'
                    if request.session.get('enrollment'):
                        if int(username) == int(
                                request.session.get('enrollment')) and email.lower() == request.session.get(
                                'email').lower():
                            logger(request, request.session.get('enrollment'), 'exist_user')
                        else:
                            logger(request, request.session.get('enrollment'), f'{username}:{email} | exist_user')
                    else:
                        logger(request, username, f'{username}:{email} | exist_user not in session', email=email)
                        request.session['enrollment'] = username
                        request.session['email'] = email

                    checkss = request.session.get('mail_sent_demo')
                    if checkss != 'Yes':
                        try:
                            logger(request, username, f'reminder_mail_auto_start')
                            request.session['mail_sent_demo'] = 'Yes'

                            domain = f'{main_domain}/verify/'

                            email = temp_obj.email
                            name = " ".join(temp_obj.name.split(' ')[:2]).title()
                            users = temp_obj.username
                            site_url = f'{domain}{temp_obj.auth_token}/'
                            password = temp_obj.password

                            if temp_obj.user:
                                lol = temp_obj.user.username
                            else:
                                lol = None

                            reminder_mail_thread = Thread(target=send_mail,
                                                          args=(
                                                          email, name, users, site_url, password, 'reminder', lol))
                            reminder_mail_thread.start()
                        except Exception as e:
                            logger(request, username, f'reminder_mail_error | {e}')
                    else:
                        logger(request, '', f'| {checkss}')

                    a = {'status': True, 'exists': 'exist_user', 'msg': msg}
                    return JsonResponse(a)

                if request.session.get('enrollment'):
                    if int(username) == int(request.session.get('enrollment')) and email.lower() != request.session.get(
                            'email').lower():
                        logger(request, request.session.get('enrollment'), f'{email} | Change Email')
                    elif int(username) != int(
                            request.session.get('enrollment')) and email.lower() == request.session.get(
                            'email').lower():
                        msg = 'This Email Address Is Already Registered, So Try With Another Email Address.....!'
                        logger(request, request.session.get('enrollment'), f'{username}:{email} | suspended_user')
                        a = {'status': True, 'create': 'suspended_user', 'msg': msg}
                        return JsonResponse(a)

                if name_:
                    if User.objects.filter(username=name_).first():
                        msg = 'This Username Is Already Taken, So Try With Another Username.....!'
                        logger(request, request.session.get('enrollment'),
                               f'{name_}|{username}:{email} | already_taken')
                        a = {'status': True, 'create': 'already_taken', 'msg': msg}
                        return JsonResponse(a)

                    user_obj = User.objects.create(
                        username=name_,
                        email=email,
                        password=password,
                    )
                    user_obj.save()

                auth_token = str(uuid.uuid4())
                varify = False
                check = 1
                check_val = 'register'

                profile_obj = Profile.objects.create(
                    username=username,
                    email=email,
                    password=password,
                    name=student_obj.name,
                    auth_token=auth_token,
                    is_verified=varify,
                    branch=student_obj.branch,
                )
                if name_:
                    profile_obj.user = user_obj
                    lol = user_obj.username
                else:
                    lol = None
                profile_obj.save()

                site_url = f'{main_domain}/verify/{auth_token}/'

                try:
                    send_mail(
                        email=email,
                        first_name=name,
                        username=username,
                        site_url=site_url,
                        password=password,
                        check=check_val,
                        names=lol
                    )
                    s_ch = 1
                except Exception as e:
                    s_ch = 0
                    logger(request, username, f'email_send_error | {e}')

                if request.session.get('enrollment'):
                    if int(username) == int(request.session.get('enrollment')):
                        logger(request, request.session['enrollment'], 'user_create')
                    else:
                        logger(request, request.session['enrollment'], f'{username}:{email} | user_create')
                else:
                    logger(request, username, 'user_create', email=email)

                request.session['enrollment'] = profile_obj.username
                request.session['email'] = profile_obj.email
                request.session['password'] = profile_obj.password

                msg = 'Please Open Your Email Inbox / Spam Folder And Click The Login Button To Activate Your Account.....!'
                create = 'user_create'
                if not name:
                    msg_1 = f'Account Was Created For {username} And Activation Link Was Sent To {email}.'
                else:
                    msg_1 = f'Account Was Created For {name} And Activation Link Was Sent To {email}.'
                if s_ch == 0:
                    msg_1 = f'Account Was Created For {profile_obj.username}.'
                    msg = 'Sorry To Say, We Are Unable To Send You An Email, Just enter wrong password, after that enter your roll no.'
                    create = 'user_create_fail'
                msg_2 = ''
                msg_3 = ''

                a = {
                    'status': True, 'create': create, 'u_name': username,
                    'msg': msg, 'msg_1': msg_1, 'msg_2': msg_2, 'msg_3': msg_3
                }
                return JsonResponse(a)
            except Exception as e:
                logger_send(request, f'user_create_error | {e}')

                a = {'status': False}
                return JsonResponse(a)

        except Exception as e:
            logger_send(request, f'user_create_error | {e}')

            a = {'status': False}
            return JsonResponse(a)

    else:
        items = {
            'hid': 'AIML',
            'sid': 'register',
            'vname': f'register',
            'home_': 'aiml'
        }
        return render(request, 'register.html', items)


# Request For Faculty Register
def register_faculty(request):
    access = get_user(request, 0)
    if not access:
        logger_send(request, 'Denied Entry')

        enroll = request.session.get('enrollment')
        if enroll:
            link = enroll
            messages.error(request, 'You Are Not Authorised To Access This Page.....!')
        else:
            link = 'register'

        return redirect(f'/{link}/')

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            fullname = request.POST.get('Fullname')
            enroll_ = len(Profile.objects.filter(user_type='faculty')) + 1
            enroll = return_three_digit_len(enroll_)
            email = request.POST.get('email').lower().strip()
            password = password_generator()

            user_obj = User.objects.create(
                username=username,
                email=email,
                password=password,
            )
            user_obj.save()

            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(
                username=enroll,
                password=password,
                email=email,
                name=fullname,
                auth_token=auth_token,
                is_verified=True,
                branch='-',
                user_type='faculty',
                user=user_obj
            )
            profile_obj.save()

            logger(request, enroll, f'{username}:{email} | user_create', email=email, path='/register/')

            msg_1 = f'Account Was Created For {username}.'
            msg_2 = ''
            msg_3 = ''
            msg = 'Done ....!'
            create = 'user_create'

            a = {
                'status': True, 'create': create, 'u_name': username,
                'msg': msg, 'msg_1': msg_1, 'msg_2': msg_2, 'msg_3': msg_3
            }
            return JsonResponse(a)
        except Exception as e:
            a = {'status': e}
            return JsonResponse(a)

    else:
        items = {
            'hid': 'AIML',
            'sid': 'f_register',
            'vname': f'Faculty Register',
        }
        return render(request, 'register_faculty.html', items)


# Request For User & Faculty Login
@custom_login_required_not
def login(request, template_name, ksy):
    if request.method == 'POST':
        try:
            s_name = request.POST['f_name']
            if s_name.isascii():
                logger(request, '', f'{s_name} | forget_password_enquiry')
                logger(request, '', f'{s_name} | forget_password_enquiry', filename_s='contacts')
            return JsonResponse({'status': 'ok'})
        except:
            pass
        try:
            s_name = request.POST['f_name_']
            if s_name.isascii():
                logger(request, '', f'{s_name} | register_enquiry')
                logger(request, '', f'{s_name} | register_enquiry', filename_s='contacts')
            return JsonResponse({'status': 'ok'})
        except:
            pass
        path = request.META.get('HTTP_REFERER')
        temp = request.path

        try:
            check = request.POST.get('user_login')
            username = request.POST.get('name')
            enrollment = request.POST.get('Username')
            email = request.POST.get('Email')
            password = request.POST.get('Password')
            if username:
                username = username.lower().strip()
            else:
                username = ''
            if enrollment:
                enrollment = enrollment.lower().strip()
            else:
                enrollment = ''
            if email:
                email = email.lower().strip()
            else:
                email = ''

            if username or check:
                pro_obj = Profile.objects.filter(user__username=username).first()
            else:
                pro_obj = Profile.objects.filter(username=enrollment, email=email).first()

            if pro_obj:
                if not request.session.get('enrollment') == pro_obj.username:
                    if not request.session.get('enrollment'):
                        logger(request, '', f'{pro_obj.username}:{pro_obj.email}:- ({pro_obj.id}) | Login Change')
                    else:
                        logger(request, request.session.get('enrollment'),
                               f'{pro_obj.username}:{pro_obj.email}:- ({pro_obj.id}) | Login Change')

                    request.session['enrollment'] = pro_obj.username
                    request.session['email'] = pro_obj.email

                if not request.session.get('enrollment'):
                    request.session['enrollment'] = pro_obj.username
                    request.session['email'] = pro_obj.email

                if pro_obj.user_type == 'faculty':
                    if 'faculty' not in path:
                        if request.session.get('enrollment'):
                            logger(request, request.session.get('enrollment'), f'{pro_obj.username} | not_student')
                        else:
                            logger(request, '', f'{pro_obj.username} | not_student', filename_s='contacts')

                        msg = 'You are not authorized to access this page, Please proceed to the <a href="/faculty/login/" style="color: #247bf6; font-size: 15px; font-weight: 600;">Faculty Login</a>.....!'
                        a = {'status': True, 'create': 'not_faculty', 'msg': msg}
                        return JsonResponse(a)
                else:
                    if 'faculty' in path:
                        if request.session.get('enrollment'):
                            logger(request, request.session.get('enrollment'), f'{pro_obj.username} | not_faculty')
                        else:
                            logger(request, '', f'{pro_obj.username} | not_faculty', filename_s='contacts')

                        msg = 'You are not authorized to access this page, Please proceed to the <a href="/login/" style="color: #247bf6; font-size: 15px; font-weight: 600;">Student Login</a>.....!'
                        a = {'status': True, 'create': 'not_faculty', 'msg': msg}
                        return JsonResponse(a)

                logger(request, pro_obj.username, f'{pro_obj.username}:{pro_obj.email} | Login Start')

            if username.isascii() == False or enrollment.isascii() == False or email.isascii() == False:
                msg = 'Please Enter Proper Details.....!'
                if request.session.get('enrollment'):
                    logger(request, request.session.get('enrollment'), f'Proper_Details')
                else:
                    logger(request, '', f'Proper_Details')
                a = {'status': True, 'create': 'details_error', 'msg': msg}
                return JsonResponse(a)

            if not pro_obj:
                msg = 'Account Not Found, Please Create An Account.....<a href="/register/" style="color: #247bf6; font-size: 15px; font-weight: 600;">click here</a>'
                if '/faculty/login/' in temp or '/faculty/login/' in path:
                    msg = 'Faculty Account Missing! Contact Admin <a href="/developed-by/?keys=creare faculty account" style="color: #247bf6; font-size: 15px; font-weight: 600;">here</a> Or Fill <a href="/contact/?keys=creare faculty account" style="color: #247bf6; font-size: 15px; font-weight: 600;">Form</a>. ' \
                          'Non-faculty, Go To <a href="/login/" style="color: #247bf6; font-size: 15px; font-weight: 600;">Student Login</a>.'
                if request.session.get('enrollment'):
                    logger(request, request.session.get('enrollment'),
                           f'{username}:{enrollment}:{email} | not_exist_user')
                else:
                    logger(request, '', f'{username}:{enrollment}:{email} | not_exist_user')
                a = {'status': True, 'create': 'not_exist_user', 'msg': msg}
                return JsonResponse(a)

            if request.POST.get('s1'):
                s_ = []
                for i in ActualRollNoModel.objects.filter(student__enrollment_number=pro_obj.username).order_by(
                        '-sem__sem_name')[
                         :2]:
                    s_.append(f'{i.roll_no}')

                logger(
                    request, request.session.get('enrollment'),
                    f"['{request.POST.get('s1')}', '{request.POST.get('s2')}] - {s_}"
                )
                pas = [request.POST.get('s1'), request.POST.get('s2')] == s_
                if pas:
                    request.session['userid'] = pro_obj.username
                    request.session['email'] = pro_obj.email
                    request.session['enrollment'] = pro_obj.username
                    request.session['password'] = pro_obj.password

                    logger(request, request.session.get('enrollment'), f'Login Successfully with rollno')
                    msg = 'Login Successfully.....!'
                    url = '/change/'
                    a = {'status': True, 'create': 'login_success', 'msg': msg, 'url': f'{url}'}
                    return JsonResponse(a)
                else:
                    logger(request, request.session.get('enrollment'), f'Roll No Not Match')
                    msg = 'Roll No. Not Match.....!'
                    a = {'status': True, 'create': 'wrong', 'msg': msg}
                    return JsonResponse(a)

            if not pro_obj.password == password:
                s_ = []
                for i in ActualRollNoModel.objects.filter(student__enrollment_number=pro_obj.username).order_by(
                        '-sem__sem_name')[:2]:
                    s_.append(i.sem.sem_name)

                msg = 'Wrong Password, Check Your Email For Password.....!'
                a = {'status': True, 'create': 'wrong_password', 'msg': msg, 'sem': s_}
                if s_:
                    msg_1 = f'Just Enter Your Roll No. of Sem {s_[0]} below.'
                    a['msg_1'] = msg_1
                    try:
                        msg_2 = f'Just Enter Your Roll No. of Sem {s_[1]} below.'
                        a['msg_2'] = msg_2
                    except:
                        pass

                if request.session.get('enrollment'):
                    logger(request, pro_obj.username, f'{username}:{enrollment}:{email}:{password} | wrong_password')
                else:
                    logger(request, '', f'{username}:{enrollment}:{email}:{password} | wrong_password')

                return JsonResponse(a)

            if not pro_obj.is_verified:
                if request.session.get('enrollment'):
                    logger(request, pro_obj.username, f'{username}:{enrollment}:{email} | Verifying')
                else:
                    logger(request, '', f'{username}:{enrollment}:{email} | Verifying')
                pro_obj.is_verified = True
                pro_obj.save()

            if request.session.get('enrollment'):
                logger(request, request.session.get('enrollment'), 'login_success')
            else:
                logger(request, '', 'login_success')

            request.session['userid'] = pro_obj.username
            request.session['enrollment'] = pro_obj.username
            request.session['email'] = pro_obj.email
            request.session['password'] = pro_obj.password

            msg = 'Login Successfully.....!'

            if pro_obj.user_type == 'faculty':
                request.session['type'] = 'faculty'

            else:
                if request.session.get('type'):
                    del request.session['type']

            if get_user(request, 0):
                request.session['access'] = True
            else:
                request.session['access'] = False

            temp = request.META.get('HTTP_REFERER').split('=')
            if len(temp) > 1:
                temp = temp[-1]
                try:
                    if not int(f'{temp}'.replace('/', '')) == int(pro_obj.username):
                        temp = ''
                except:
                    pass
            else:
                temp = ''
            if temp:
                url = temp
            else:
                if pro_obj.user_type == 'faculty':
                    url = '/branch/'
                else:
                    url = f'/{pro_obj.username}/'

            messages.success(request, msg)

            a = {'status': True, 'create': 'login_success', 'msg': msg, 'url': f'{url}'}
            return JsonResponse(a)

        except:
            a = {'status': False}
            return JsonResponse(a)
    else:
        items = {
            'ksy': ksy,
            'hid': 'AIML',
            'sid': 'login',
            'vname': f'Login',
            'home_': 'aiml',
        }
        return render(request, template_name, items)


# Request For Verify Mail
def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if not profile_obj:
            if request.session.get('enrollment'):
                return redirect(f"/{request.session.get('enrollment')}/")
            else:
                return redirect('/login/')

        try:
            request.session['verify'] = 'yes'
            logout(request)
        except:
            pass
        try:
            logout_user(request)
        except:
            pass
        if profile_obj.user_type == 'faculty':
            request.session['type'] = 'faculty'
        else:
            if request.session.get('type'):
                del request.session['type']

        email = profile_obj.email
        name = profile_obj.username
        if not profile_obj.is_verified:
            profile_obj.is_verified = True
            profile_obj.save()

        logger_send(request, f'{name}:{email} | verify_login_success')
        request.session['userid'] = name
        request.session['enrollment'] = name
        request.session['email'] = email
        request.session['password'] = profile_obj.password
        logger_send(request, f'{name}:{email} | verify_login_success')

        if get_user(request, 0):
            request.session['access'] = True
        else:
            request.session['access'] = False

        return redirect(f'/{name}/')

    except Exception as e:
        logger_send(request, f'Verify_Error | {e}')
        if request.session.get('enrollment'):
            return redirect(f"/{request.session.get('enrollment')}/")
        else:
            return redirect(f'/login/')


# Request For Forgot Password
def password_forgot(request):
    if request.method == 'POST':
        username = request.POST.get('enroll')
        email = request.POST.get('email')
        email = email.lower().strip()

        try:
            student_obj = get_profile(username)
            name = " ".join(student_obj.name.split(' ')[:2])
        except:
            logger_send(request, f'{username}:{email} | wrong_enrollment')

            msg = 'Please Enter Current Enrollment Number.....!'
            a = {'status': True, 'create': 'email_error', 'msg': msg}
            return JsonResponse(a)

        if len(username) != 12:
            if request.session.get('enrollment'):
                if int(username) != int(request.session.get('enrollment')):
                    logger(request, request.session.get('enrollment'), f'{username} | wrong_enrollment')
            else:
                logger(request, '', f'{username}:{email} | wrong_enrollment')

            msg = 'Please Enter Current Enrollment Number.....!'
            a = {'status': True, 'create': 'email_error', 'msg': msg}
            return JsonResponse(a)
        try:
            int(username)
        except:
            if request.session.get('enrollment'):
                if int(username) != int(request.session.get('enrollment')):
                    logger(request, request.session.get('enrollment'), f'{username} | wrong_enrollment')

            msg = 'Please Enter Current Enrollment Number.....!'
            a = {'status': True, 'create': 'email_error', 'msg': msg}
            return JsonResponse(a)
        if not email.endswith('@gmail.com'):
            if request.session.get('enrollment'):
                if int(username) == int(request.session.get('enrollment')):
                    logger(request, request.session.get('enrollment'), f'{email} | email_error')
                else:
                    logger(request, request.session.get('enrollment'), f'{username}:{email} | email_error')
            else:
                logger(request, '', f'{username}:{email} | email_error')

            msg = 'Please Enter Proper Email Address.....!'
            a = {'status': True, 'exists': 'email_error', 'msg': msg}
            return JsonResponse(a)

        try:
            check = Profile.objects.filter(username=username, email=email).first()
            if not check:
                logger(request, '', f'{username}:{email} | not_found')
                msg = '<b> Account Not Found </b>, Please try with different Enrollment number/Email.....!'
                a = {'status': True, 'exists': 'not_found', 'msg': msg}
                return JsonResponse(a)

            if check.user:
                lol = check.user.username
            else:
                lol = None
            auth_token = check.auth_token
            password = check.password
            site_url = f'{main_domain}/verify/{auth_token}/'
            try:
                send_mail(
                    email=email,
                    first_name=name,
                    username=username,
                    site_url=site_url,
                    password=password,
                    check='forgot',
                    names=lol
                )

                logger(request, username, f'{username}:{email} | sent', email=email)

                msg = 'We Have Sent You An Email With Your Password And Login Link, Please Check Your Email Inbox / Spam Folder.....!'
                msg_1 = f'Email Was Sent To {email}.'
                exists = 'found'
            except Exception as e:
                logger(request, username, f'{username}:{email} | Mail Failed - {e}', email=email)

                msg = 'Sorry To Say, We Are Unable To Send You An Email, Please Login Using Your Roll no. After entering wrong password.'
                msg_1 = f''
                exists = 'email_error'

            a = {'status': True, 'exists': exists, 'msg': msg, 'msg_1': msg_1}
            return JsonResponse(a)

        except Exception as e:
            if request.session.get('enrollment'):
                logger(request, request.session.get('enrollment'), f'Some Error | {e}')
            else:
                logger(request, '', f'{e} | Some Error')
            a = {'status': False}
            return JsonResponse(a)

    else:
        logger_send(request)
        if request.session.get('userid'):
            return redirect(f'/change/')
        items = {
            'hid': 'AIML',
            'sid': 'perti',
            'vname': f'forgot',
            'home_': 'forgot'
        }
        return render(request, 'password-forgot.html', items)


# Request For Change Password
@custom_login_required
def password_change(request):
    if request.method == 'POST':
        userid = request.session.get('enrollment')
        try:
            password = request.POST['Password']
            new_password = request.POST['Confirm-Password']
            if password.isascii() == False or new_password.isascii() == False:
                logger(request, userid, f'Proper_Details')

                msg = 'Please Enter Proper Details.....!'
                a = {'status': 'details_error', 'msg': msg}
                return JsonResponse(a)

            if not password or not new_password:
                logger(request, userid, f'Password Not Entered')

                msg = 'Please Enter Password.....!'
                a = {'status': 'details_error', 'msg': msg}
                return JsonResponse(a)

            if password != new_password:
                logger(request, userid, f'Password Not Matched')

                msg = 'Password Not Matched.....!'
                a = {'status': 'password_error', 'msg': msg}
                return JsonResponse(a)

            user_obj = get_student(request)
            user_obj.password = password
            user_obj.save()

            try:
                user_obj_1 = User.objects.get(username=user_obj.user.username)
                user_obj_1.set_password(password)
                user_obj_1.save()
            except:
                pass

            request.session['password'] = password
            request.session['change'] = 'change'
            logger(request, userid, f'Password Changed')

            """
                Call Function For Change Password In Chat Server
            """
            users = user_obj.username
            email = user_obj.email

            try:
                logger(request, userid, f'change_password_Mail_send_start')
                site_url = f'{main_domain}/verify/{user_obj.auth_token}/'
                name = " ".join(user_obj.name.split(' ')[:2])
                if user_obj.user:
                    lol = user_obj.user.username
                else:
                    lol = None

                send_mail(
                    email=email,
                    first_name=name,
                    username=users,
                    site_url=site_url,
                    password=password,
                    check='change_password',
                    names=lol
                )
            except Exception as e:
                logger(request, userid, f'change_password_Mail_send_error | {e}')

            msg = 'Password Changed Successfully.....!'
            a = {'status': True, 'msg': msg}
            return JsonResponse(a)

        except:
            logger(request, userid, f'Delete_Details')

            msg = 'Please Enter Proper Details.....!'
            a = {'status': False, 'msg': msg}
            return JsonResponse(a)

    else:
        if request.session.get('change'):
            messages.success(request, 'Password Changed Successfully.....!')
            del request.session['change']

        items = {
            'hid': 'AIML',
            'sid': 'perti',
            'vname': f'change',
            'home_': 'change',
        }
        return render(request, 'password-change.html', items)


# Request For Send Reminder Mail
@history_access
def password_reminder(request):
    if request.method == 'POST':
        username = request.POST.get('enroll')
        email = request.POST.get('email')
        email = email.lower().strip()

        try:
            student_obj = get_profile(username)
            name = " ".join(student_obj.name.split(' ')[:2])
        except:
            msg = 'Please Enter Current Enrollment Number.....!'
            a = {'status': True, 'create': 'email_error', 'msg': msg}
            return JsonResponse(a)

        if len(username) != 12:
            msg = 'Please Enter Current Enrollment Number.....!'
            a = {'status': True, 'create': 'email_error', 'msg': msg}
            return JsonResponse(a)
        try:
            int(username)
        except:
            msg = 'Please Enter Current Enrollment Number.....!'
            a = {'status': True, 'create': 'email_error', 'msg': msg}
            return JsonResponse(a)
        if not email.endswith('@gmail.com'):
            msg = 'Please Enter Proper Email Address.....!'
            a = {'status': True, 'exists': 'email_error', 'msg': msg}
            return JsonResponse(a)

        try:
            check = Profile.objects.filter(username=username, email=email).first()
            if not check:
                msg = '<b> Account Not Found </b>, Please try with different Enrollment number/Email.....!'
                a = {'status': True, 'exists': 'not_found', 'msg': msg}
                return JsonResponse(a)

            if check.user:
                lol = check.user.username
            else:
                lol = None
            auth_token = check.auth_token
            password = check.password
            site_url = f'{main_domain}/verify/{auth_token}/'
            try:
                send_mail(
                    email=email,
                    first_name=name,
                    username=username,
                    site_url=site_url,
                    password=password,
                    check='reminder',
                    names=lol
                )

                msg = 'We Have Sent You An Email With Your Password And Login Link, Please Check Your Email Inbox / Spam Folder.....!'
                msg_1 = f'Email Was Sent To {email}.'
                logger(request, '', f'{username}:{email} | sent', filename_s='contacts')
                exists = 'found'
            except Exception as e:
                msg = 'Sorry To Say, We Are Unable To Send You An Email, Please Login Using Your Roll no. After entering wrong password.'
                msg_1 = f''
                logger(request, '', f'{username}:{email} | Mail Failed - {e}', filename_s='contacts')
                exists = 'email_error'

            a = {'status': True, 'exists': exists, 'msg': msg, 'msg_1': msg_1}
            return JsonResponse(a)

        except Exception as e:
            logger(request, '', f'{e} | Some Error', filename_s='contacts')
            a = {'status': False}
            return JsonResponse(a)

    else:
        items = {
            'hid': 'AIML',
            'sid': 'perti',
            'vname': f'Reminder Mail',
            'home_': 'reminder'
        }
        return render(request, 'password-reminder.html', items)


# Request For LogOut
def logout(request):
    if request.method == 'POST' or request.session.get('verify'):
        ss = request.session.get('userid')
        if request.method == 'POST' and not request.session.get('verify'):
            messages.success(request, 'You Have Logged Out Successfully.....!')
            logger(request, request.session.get('enrollment'), 'Logout')
        try:
            if request.session.get('userid'):
                logger(request, request.session['userid'], '')
                del request.session['userid']
            if request.session.get('access'):
                del request.session['access']
            if request.session.get('fake'):
                del request.session['fake']
            if request.session.get('access_1'):
                del request.session['access_1']
        except:
            pass
        if ss:
            urs = f'/login/?next=/{ss}/'
        else:
            urs = '/'
        return JsonResponse({'status': 'ok', 'url': urs})
    else:
        enroll = request.session.get('userid')
        if enroll:
            messages.success(request, 'Please click on the logout button to log out.....!')
            if request.session.get('type') == 'faculty':
                logger(request, enroll, 'faculty_logout')
                return redirect('/branch/')
            else:
                return redirect(f'/{enroll}/')
        else:
            if request.session.get('enrollment'):
                return redirect(f"/login/?next=/{request.session.get('enrollment')}/")
            else:
                return redirect(f'/login/')


# Request For Set Username
def set_username(request):
    logger_send(request)
    if not request.session.get('userid'):
        messages.error(request, 'First You Need to Login, Then You Can Change / Set Your Username.....!')
        return redirect('/login/?next=/profile/')

    if request.method == 'POST':
        username = request.POST.get('Username')
        username = username.strip().lower()

        if not username.isascii():
            logger(request, request.session.get('enrollment'), 'Proper_Details')

            msg = 'Please Enter Proper Username.....!'
            a = {'status': False, 'create': 'details_error', 'msg': msg}
            return JsonResponse(a)

        if not username.count(' ') == 0:
            logger(request, request.session.get('enrollment'), f'{username} | Space_Not_Allowed')

            msg = 'Space Not Allowed In Username.....!'
            a = {'status': False, 'create': 'details_error', 'msg': msg}
            return JsonResponse(a)

        user_name = ''
        user_name_obj = get_student(request)
        try:
            if user_name_obj.user:
                user_name = user_name_obj.user.username
        except:
            pass
        site_url = f'{main_domain}/verify/{user_name_obj.auth_token}/'
        if user_name:
            if username.lower() == user_name.lower():
                logger(request, request.session.get('enrollment'), f'same_user')

                msg = 'You Are Already Using This Username.....!'
                a = {'status': False, 'create': 'same_user', 'msg': msg}
                return JsonResponse(a)

            user_obj = User.objects.filter(username=username).first()
            if user_obj:
                logger(request, request.session.get('enrollment'), f'{user_name}:{username} | exist_user')

                msg = 'Username Already Exist.....!'
                a = {'status': False, 'create': 'exist_user', 'msg': msg}
                return JsonResponse(a)

            user_obj = User.objects.get(username=user_name)
            user_obj.username = username
            user_obj.save()

            user_name_obj.user = user_obj
            user_name_obj.save()

            logger(request, request.session.get('enrollment'), f'{user_name}:{username} | update_user')

            msg = 'Username Changed Successfully.'
            a = {'status': True, 'msg': msg, 'url': f'/profile/', 'username': username}
            return JsonResponse(a)
        else:
            user_obj = User.objects.filter(username=username).first()
            if user_obj:
                logger(request, request.session.get('enrollment'), f'{username} | exist_user')

                msg = 'Username Already Exist.....!'
                a = {'status': False, 'create': 'exist_user', 'msg': msg}
                return JsonResponse(a)

            user_obj = User.objects.create_user(username=username, password=user_name_obj.password)
            user_obj.save()

            user_name_obj.user = user_obj
            user_name_obj.save()

            logger(request, request.session.get('enrollment'), f'{username} | create_user')

            msg = 'Username Created Successfully.'
            a = {'status': True, 'msg': msg, 'url': f'{site_url}', 'username': username}
            return JsonResponse(a)

    else:
        items = {
            'hid': f'Proa',
            'sid': 'perti',
            'vname': f'Profile',
            'home_': f'profile'
        }
        try:
            user_name_obj = get_student(request)
            items['token'] = user_name_obj.auth_token
            if user_name_obj.user:
                items['user_name'] = user_name_obj.user.username
        except:
            pass

    return render(request, 'set-username.html', items)


# Request For Student Profile
@custom_login_required
def student_profile(request):
    logger_send(request)
    return render(request, 'coming-soon.html', {'vname': 'Profile'})


# Request For Faculty Profile
@custom_login_required
def faculty_profile(request):
    logger_send(request)
    return render(request, 'coming-soon.html', {'vname': 'Profile'})


"""
-->                     User Authentication, Account Creation, Password Reset, Activity etc End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                             Contact Section Start
"""


# Request For Contact Page
def contact(request):
    logger_send(request)
    if request.method == 'POST':
        try:
            con_obj = ContactModel()
            msg = request.POST.get('message').strip()
            if not msg:
                a = {'status': False, 'create': 'field_error', 'msg': 'Please Fill Massage Field.....!'}
                return JsonResponse(a)

            name = request.POST.get('name').strip()
            email = request.POST.get('Email').lower().strip()
            if not email.endswith('@gmail.com'):
                a = {'status': False, 'create': 'email_error', 'msg': 'Please Enter Proper Email Address.....!'}
                return JsonResponse(a)

            if name == '' or msg == '' or email == '':
                a = {'status': False, 'create': 'field_error', 'msg': 'Please Fill All The Fields.....!'}
                return JsonResponse(a)

            con_obj.name = name
            con_obj.email = email
            con_obj.msg = msg
            con_obj.save()

        except:
            pass

        a = {'status': True, 'create': 'Success', 'msg': 'Thank You For Messaging Us, We Will Contact You Soon.....!'}
        return JsonResponse(a)
    else:
        items = {
            'hid': 'AIML',
            'sid': 'contact',
            'vname': f'contact',
        }
        return render(request, 'contact.html', items)


"""
-->                                             Contact Section End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                             Confession Activity Start
"""


# Request For Add Confession Page
def confession_add(request):
    if request.method == 'POST':
        massage = request.POST.get('message').strip()
        try:
            count = int(request.POST.get('just_temp'))
        except:
            count = 0
        if not massage:
            msg = 'Please Fill Massage Field.....!'
            a = {'status': False, 'create': 'field_error', 'msg': msg}
            return JsonResponse(a)

        if count > 300:
            msg = 'Please Enter Less Than 300 Characters.....!'
            a = {'status': False, 'create': 'field_error', 'msg': msg}
            return JsonResponse(a)

        confession_obj = ConfessionModel()
        confession_obj.msg = massage
        confession_obj.status = True
        confession_obj.save()

        msg = 'Thank You For Confession, See Your Confession <a href="/confession/views/">Here</a>.....!'
        a = {'status': True, 'create': 'Success', 'msg': msg}
        return JsonResponse(a)

    else:
        items = {
            'hid': 'AIML',
            'sid': 'add_confession',
            'vname': f'confession',
        }
        return render(request, 'confession-add.html', items)


# Request For View Confession Page
def confession_view(request):
    items = {
        'sid': 'confession',
        'home_': 'one',
        'vname': f'confession Page',
    }
    confession_obj = ConfessionModel.objects.filter(status=True).order_by('-created_at')
    for con in confession_obj:
        like_count = con.confession_like.filter(deleted=False).count()
        comment_count = con.confession_comment.filter(deleted=False).count()
        con.likes = like_count
        con.comments = comment_count
    if request.session.get('userid'):
        for i in confession_obj:
            try:
                obj = get_student(request)
                confession_like_obj = ConfessionLikeModel.objects.get(student=obj, confession=i)
                i.check = confession_like_obj.deleted
            except:
                i.check = True
        items['auth'] = 'yes'
    else:
        for i in confession_obj:
            i.check = True
    items['conf'] = confession_obj

    return render(request, 'confession-view.html', items)


# Request For View Comments in Confession Page
def get_confession(request):
    if request.method == 'POST':
        con_list = []
        confession_id = request.POST.get('id')
        confession_obj = ConfessionModel.objects.get(id=confession_id)
        msg = confession_obj.msg

        get_con = ConfessionCommentModel.objects.filter(confession=confession_obj, deleted=False).order_by(
            'created_at')
        if request.session.get('userid'):
            profile_obj = get_student(request)
            temp = 0
        else:
            temp = 1

        for i in get_con:
            items = {
                'msg': i.msg,
            }
            if temp == 0:
                if int(i.student.username) == int(profile_obj.username) and i.student.email.lower() == (
                        profile_obj.email).lower():
                    check = 'yes'
                    items['id'] = i.id
                else:
                    check = 'no'
            else:
                check = 'no'

            items['check'] = check
            con_list.append(items)

        logger_send(request, f'{confession_id}:View_comment')

        a = {
            'status': True,
            'msg': msg,
            'con_list': con_list
        }
        return JsonResponse(a)

    logger_send(request)
    return redirect('/confession/views/')


# Request For Add & Delete Like in Confession Page
def add_like(request):
    if request.method == 'POST':
        confession_id = request.POST.get('id')
        check = request.POST.get('check')
        obj = get_student(request)

        confession_obj = ConfessionModel.objects.get(id=confession_id)
        if int(check) == 0:
            confession_like_obj = ConfessionLikeModel.objects.get(student=obj, confession=confession_obj)
            logger(request, request.session.get('userid'), f'{confession_obj.id}:dislike')
            confession_like_obj.deleted = True
        else:
            try:
                confession_like_obj = ConfessionLikeModel.objects.get(student=obj, confession=confession_obj)
            except:
                confession_like_obj = ConfessionLikeModel()
            confession_like_obj.deleted = False
            logger(request, request.session.get('userid'), f'{confession_obj.id}:like')

        confession_like_obj.student = obj
        confession_like_obj.confession = confession_obj
        confession_like_obj.save()

        a = {'status': True, 'msg': 'Thank You For Liking.....!'}
        return JsonResponse(a)

    return redirect('/confession/views/')


# Request For Add Comment in Confession Page
def add_comment(request):
    logger_send(request)
    if not request.session.get('userid'):
        return redirect('/confession/views/')

    if request.method == 'POST':
        confession_id = request.POST.get('comment_id')
        msg = request.POST.get('comment')

        if msg:
            msg = msg.strip()
        if not msg:
            logger(request, '', 'Please_Fill_comment')
            a = {'status': False, 'create': 'field_error', 'msg': 'Please Fill Massage Field.....!'}
            return JsonResponse(a)

        obj = get_student(request)
        confession_obj = ConfessionModel.objects.get(id=confession_id)
        confession_obj.comments = confession_obj.comments + 1
        confession_obj.save()
        confession_comment_obj = ConfessionCommentModel()
        confession_comment_obj.student = obj
        confession_comment_obj.confession = confession_obj
        confession_comment_obj.msg = msg
        confession_comment_obj.save()

        logger(request, request.session.get('userid'), f'{confession_id}:add_comment')

        a = {'status': True, 'create': 'Success', 'msg': 'Thank You For Commenting.....!', 'id': confession_id}
        return JsonResponse(a)

    return redirect('/confession/views/')


# Request For Delete Comment in Confession Page
def delete_comment(request):
    logger_send(request)
    if not request.session.get('userid'):
        return redirect('/confession/views/')

    if request.method == 'POST':
        confession_id = request.POST.get('confession_id')

        obj = get_student(request)
        try:
            confession_obj = ConfessionCommentModel.objects.get(id=confession_id, student=obj)
            confession_obj.deleted = True
            confession_obj.save()

            logger(request, request.session.get('userid'), f'{confession_id}:delete_comment')

            a = {'status': True, 'msg': 'Comment Deleted Successfully.....!', 'id': confession_obj.confession.id}
            return JsonResponse(a)
        except:
            logger(request, request.session.get('userid'), f'{confession_id}:delete_comment_but_someone')
            a = {'status': False, 'msg': 'You Are Not Authorised To Delete This Comment.....!', 'id': confession_id}
            return JsonResponse(a)

    return redirect('/confession/views/')


"""
-->                                             Confession Activity End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                              Upload Result Start
"""


# Upload Result Page
def upload(request):
    return upload_dynamic(request, 0)


# Upload Actual Roll No Page
def upload_roll_no(request):
    main_access = get_user(request, 1)
    if not main_access:
        if request.session.get('enrollment'):
            logger(request, request.session.get('enrollment'), 'Denied Entry')
        else:
            logger(request, '', 'Denied Entry')
        messages.error(request, 'Upload division page access denied due to lack of authorization......!')
        return redirect(f'/upload/')

    return upload_dynamic(request, 1)


# Request For Uploading Result, Actual Roll & insert Result, Actual Roll in Database
def upload_dynamic(request, result_roll):
    branch_obj = BranchNameModel.objects.all()
    msc_obj = MscNameModel.objects.all()
    subject_obj = SubjectNameModel.objects.all()
    batch_obj = YearBatchModel.objects.all()
    sem_obj = SemModel.objects.all()
    passwordss = {
        'branch_obj': branch_obj,
        'msc_obj': msc_obj,
        'subject_objs': subject_obj,
        'batch_obj': batch_obj,
        'sem_obj': sem_obj,
        'vname': f'Upload'
    }
    if result_roll == 0:
        passwordss['sid'] = 'upload'
    else:
        passwordss['sid'] = 'upload_div'

    if request.method == "POST":
        link = request.POST.get('verify_data')
        if link == 'verify_data':
            link = 'verification'
        else:
            link = ''

        try:
            password = request.POST['fake-password']
            password2 = request.POST['nahi-password']
            check_again = 1
            if link == 'verification':
                check_data = request.session.get('final_data')
            else:
                check_data = None
        except:
            password = 11
            password2 = 11
            check_data = None
            check_again = 0
        if check_again == 1:
            current_time = (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%I:%M %p %d %B %Y")
            itemss = {
                'time': current_time,
                'password1': password,
                'password2': password2,
                'username': request.session.get('enrollment'),
                'email': request.session.get('email'),
            }
            msgs, condition, passwordss = password_check(password, password2, passwordss)
            if condition == 0:
                messages.error(request, msgs)
                logger(request, request.session.get('enrollment'),
                       f'{itemss["password1"]} - {itemss["password2"]} | {msgs}')
                if link == 'verification':
                    # return redirect('/verification/')
                    url = '/verification/'
                else:
                    # return redirect('/upload/')
                    url = '/upload/'
                if request.is_ajax():
                    a = {'status': True, 'msg': msgs, 'url': url}
                    return JsonResponse(a)
                else:
                    return redirect(f'{url}')
            elif condition == 1:
                if link == 'verification':
                    messages.success(request, msgs)
                    logger(request, request.session.get('enrollment'), f"{passwordss['vname']} | {msgs}")
                    if request.is_ajax():
                        a = {'status': True, 'msg': msgs, 'url': '/verification/'}
                        return JsonResponse(a)
                    else:
                        mse = request.session.get('hidden_msc')
                        sem = request.session.get('hidden_semester')
                        batch = request.session.get('hidden_batch')
                        branch_name = request.session.get('hidden_branch')
                        subject_name = request.session.get('hidden_subject')
                        passwordss['vname'] = f'{batch} sem {sem} {branch_name} {subject_name} mse {mse}'
                        logger(request, request.session.get('enrollment'), f"{passwordss['vname']} | {msgs}")
                        return render(request, 'upload-verify_data.html', passwordss)
                else:
                    messages.success(request, msgs)
                    logger(request, request.session.get('enrollment'), f"{msgs}")
                    if request.is_ajax():
                        a = {'status': True, 'msg': msgs}
                        return JsonResponse(a)
                    else:
                        passwordss['vname'] = f'Upload Result'
                        logger(request, request.session.get('enrollment'), f"{msgs}")
                        return render(request, 'upload-data.html', passwordss)

        # if link == 'verification':
        #     check_data = request.session.get('table_aa')
        # else:
        #     check_data = None

        if not check_data:
            batch_name = request.POST.get('batch')
            branch_name = request.POST.get('branch')
            semester_name = request.POST.get('semester')
            subject_name = request.POST.get('subject')
            msc = request.POST.get('msc')

            try:
                form = PdfDetails_Form(request.POST, request.FILES)
                if form.is_valid():
                    pdf_ = form.instance.pdf_file.file.name
                    form.save()
                    pdf_ = form.instance.pdf_file.file.name
                else:
                    msgs = f'Please Upload PDF File.....!'
                    messages.error(request, msgs)
                    if request.session.get('enrollment'):
                        logger(request, request.session.get('enrollment'), msgs)
                    else:
                        logger(request, '', msgs)
                    if request.is_ajax():
                        a = {'status': True, 'msg': msgs, 'url': '/upload/'}
                        return JsonResponse(a)
                    else:
                        return redirect('/upload/')

            except:
                passwordss['confirm_auth'] = True

                if request.session.get('final_data'):
                    msgs = f'Please Insert Password First....!'
                    messages.error(request, msgs)
                    if request.session.get('enrollment'):
                        logger(request, request.session.get('enrollment'), msgs)
                    else:
                        logger(request, '', msgs)
                    if request.is_ajax():
                        a = {'status': True, 'msg': msgs, 'url': '/verification/'}
                        return JsonResponse(a)
                    else:
                        return redirect('/verification/')
                else:
                    msgs = f'Please Upload Result First....!'
                    messages.error(request, msgs)
                    if request.session.get('enrollment'):
                        logger(request, request.session.get('enrollment'), msgs)
                    else:
                        logger(request, '', msgs)
                    if request.is_ajax():
                        a = {'status': True, 'msg': msgs, 'url': '/upload/'}
                        return JsonResponse(a)
                    else:
                        return redirect('/upload/')

            msg1, passwordss, cons = check_format(msc, subject_name, branch_name, semester_name, batch_name, pdf_,
                                                  passwordss,
                                                  request, pdf_, result_roll)
            if cons == 0:
                messages.error(request, msg1)
                if request.session.get('enrollment'):
                    logger(request, request.session.get('enrollment'), msg1)
                else:
                    logger(request, '', msg1)
                if request.is_ajax():
                    a = {'status': True, 'msg': msg1, 'url': '/upload/'}
                    return JsonResponse(a)
                else:
                    return render(request, 'upload-data.html', passwordss)
            else:
                # response = HttpResponse(content_type='text/csv')
                # response['Content-Disposition'] = f'attachment; filename="{msg1.split("/")[-1]}"'
                # html = render_to_string('verify_data.html', passwordss)
                # response.write(html)
                #
                # return response
                # passwordss['vname'] = f'{subject_name} MSE {msc}'
                # messages.error(request, msg1)
                # if request.session.get('enrollment'):
                #     logger(request, request.session.get('enrollment'), msg1)
                # else:
                #     logger(request, '', msg1)

                if result_roll == 0:
                    url = '/verification/'
                else:
                    url = '/verification/rollno/'
                if request.is_ajax():
                    a = {'status': True, 'url': f'{url}'}
                    return JsonResponse(a)
                else:
                    passwordss['vname'] = f'{batch_name} sem {semester_name} {branch_name} {subject_name} mse {msc}'
                    passwordss['on_load'] = 1
                    logger(request, request.session.get('enrollment'), f"{pdf_.split('/')[-1]} | {passwordss['vname']}")
                    if result_roll == 0:
                        return render(request, 'upload-verify_data.html', passwordss)
                    else:
                        return render(request, 'upload-verify_data_roll.html', passwordss)

        else:
            msc = request.session.get('hidden_msc')
            subject_name = request.session.get('hidden_subject')
            branch_name = request.session.get('hidden_branch')
            semester = request.session.get('hidden_semester')
            batch = request.session.get('hidden_batch')

            if request.session.get('hidden_result_roll') == 0 and result_roll == 0:
                msg = insert_data(check_data, msc, subject_name, branch_name, semester, batch)
            else:
                msg = insert_data_div_list(check_data, semester)
            logger(request, request.session.get('enrollment'), f"{msg}")
            messages.success(request, msg)

        delete_session(request)

        a = {'status': True, 'url': '/upload/'}
        if request.is_ajax():
            return JsonResponse(a)
        else:
            return redirect('/upload/')

    else:
        logger_send(request)
        if result_roll == 0:
            return render(request, 'upload-data.html', passwordss)
        else:
            return render(request, 'upload-roll.html', passwordss)


# Delete Upload Related Sessions
def delete_session(request):
    try:
        del request.session['table_aa']
    except:
        pass
    try:
        del request.session['final_data']
    except:
        pass
    try:
        del request.session['table_aa_1']
    except:
        pass
    try:
        del request.session['final_data_1']
    except:
        pass
    try:
        del request.session['csv_path']
    except:
        pass
    try:
        del request.session['csv_name']
    except:
        pass
    try:
        del request.session['hidden_msc']
    except:
        pass
    try:
        del request.session['hidden_batch']
    except:
        pass
    try:
        del request.session['hidden_subject']
    except:
        pass
    try:
        del request.session['hidden_branch']
    except:
        pass
    try:
        del request.session['hidden_semester']
    except:
        pass
    try:
        del request.session['hidden_result_roll']
    except:
        pass


# Password Check
def password_check(password, password2, passwordss):
    try:
        if int(password) == 0000:
            passwordss['fake_password'] = 0000
            try:
                if int(password2) == 0000:
                    passwordss['nahi_password'] = 0000
                    return '', 2, passwordss
                else:
                    return f'Please Enter Auth Password 2 Correctly.....! ', 1, passwordss

            except:
                return f'Please Enter Auth Password 2 Correctly.....!', 1, passwordss

        else:
            return 'Wrong Password No Access.....!', 0, ''

    except Exception as e:
        return 'Wrong Password No Access.....!', 0, ''


# Insert Upload Result Data In Final Table
def insert_data(f_list, msc, subject_name, branch_name, semester, batch):
    countss = 0
    for i in f_list:
        try:
            if len(i) == 9:
                try:
                    mark_1 = int(i[-3])
                except:
                    mark_1 = 0
                try:
                    mark_2 = int(i[-2])
                except:
                    mark_2 = 0
            else:
                try:
                    mark_1 = int(i[-2])
                except:
                    mark_1 = 0
                try:
                    mark_2 = int(i[-1])
                except:
                    mark_2 = 0
            enrollment_number = i[1]
            division = i[3]
            name = i[4]
            try:
                obj = get_profile(enrollment_number)
                exist = True
            except:
                obj = StudentDataModel()
                exist = False

            # if int(semester) == 3:
            #     batch_name = 2022
            # else:
            #     batch_name = 2021

            # Insert Data In Student Table
            if not exist:
                try:
                    batch_obj = YearBatchModel.objects.get(batch_name=batch)
                except:
                    batch_obj = YearBatchModel.objects.create(batch_name=batch)
                    batch_obj.save()

                obj.enrollment_number = enrollment_number
                obj.name = name
                obj.division = division
                obj.total_mark = 0
                obj.branch = branch_name
                obj.roll_no = i[0]
                obj.batch = batch_obj
                obj.save()

            msc_id = MscNameModel.objects.get(msc_name=msc)
            subject_name_id = SubjectNameModel.objects.get(subject_name=subject_name)
            sem_obj = SemModel.objects.get(sem_name=semester)
            try:
                subject_obj = SubjectModel.objects.get(
                    msc=msc_id.id,
                    subject=subject_name_id.id,
                    student=obj.id,
                    sem=sem_obj.id
                )
                exist = True
            except:
                subject_obj = SubjectModel()
                exist = False

            # Insert Data In Final Table
            if not exist:
                countss += 1
                subject_obj.msc = msc_id
                subject_obj.subject = subject_name_id
                subject_obj.student = obj
                subject_obj.sem = sem_obj
                subject_obj.section_A = mark_1
                subject_obj.section_B = mark_2
                subject_obj.save()
        except:
            pass

    if countss == 0:
        return 'Data Already Exists.'
    else:
        return 'Data Insert Successfully.'


# Insert Actual Roll Data In Final Table
def insert_data_div_list(f_list, semester):
    countss = 0
    for i in f_list:
        try:
            roll_no = i[0]
            enrollment_number = i[1]
            division = i[2]
            try:
                obj = actualroll_pro(enrollment_number, semester)
                exist = True
            except:
                obj = ActualRollNoModel()
                exist = False

            # Insert Data In Actual RollNo Table
            if not exist:
                try:
                    obj_1 = get_profile(enrollment_number)
                    sem_obj = SemModel.objects.get(sem_name=semester)
                except:
                    continue

                countss += 1
                obj.roll_no = roll_no
                obj.division = division
                obj.sem = sem_obj
                obj.student = obj_1
                obj.save()

        except:
            pass

    if countss == 0:
        return 'Data Already Exists.'
    else:
        return 'Data Insert Successfully.'


# Check Format Of Uploaded File
def check_format(msc, subject_name, branch_name, semester_name, batch_name, pdf_, passwordss, request, pdf_11,
                 result_roll):
    try:
        names = f'{batch_name}_{semester_name}_{branch_name}_{subject_name}_{msc}'
        counts = 0

        while True:
            if pdf_.endswith('.csv'):
                x_lists, f_list, filename, l_check = Final_csv(pdf_, names, counts, request).get_content(0, result_roll)
                if x_lists and f_list and filename:
                    final_check = 2
                else:
                    final_check = 1
                break
            elif pdf_.endswith('.pdf'):
                x_lists, f_list, filename, l_check = Final_csv(pdf_, names, counts, request).get_content(1, result_roll)
                if l_check == 0:
                    final_check = 2
                    break
                if x_lists and f_list and filename:
                    final_check = 2
                    break
                elif filename == 'fail':
                    final_check = 1
                    break
            elif pdf_.endswith('.txt'):
                if request.session.get('userid') == '221433142036':
                    x_lists = Final_csv(pdf_, pdf_11, counts, request).get_content(2, result_roll)
                    final_check = 10
                    break
                else:
                    final_check = 1
                    break
            else:
                final_check = 1
                break

            if counts >= 3:
                final_check = 1
                break

            counts += 1

        if final_check == 10:
            check = update_contacts(x_lists)
            if check != 0:
                msg = f'Contact Updated Successfully.....!'
            else:
                msg = f'Contact Not Updated.....!'
            return msg, passwordss, 0

        if final_check == 1:
            return f'Incorrect Format.....', passwordss, 0
        # pdf_obj = PdfDetailsModel()
        # pdf_obj.pdf_file = filename
        # pdf_obj.save()
        if f_list:
            try:
                aa = [{
                    'data': x_lists
                }]
                set_session(request, aa, f_list, filename, msc, subject_name, branch_name, semester_name, batch_name,
                            result_roll=0)
            except Exception as e:
                logger(request, '', f'{e} | session', filename_s='pdf_to_csv')

            return filename, passwordss, 1
        else:
            logger(request, '', f'Not Found', filename_s='pdf_to_csv')
            return f'Incorrect Format !!.....!!', passwordss, 0

    except Exception as e:
        logger(request, '', f'{e} | main last except', filename_s='pdf_to_csv')
        return f'Incorrect Format !!.....!!', passwordss, 0


# Set Upload Related Sessions
def set_session(request, aa, f_list, filename, msc, subject_name, branch_name, semester_name, batch_name,
                result_roll=0):
    request.session['table_aa'] = aa
    request.session['final_data'] = f_list
    request.session['table_aa_1'] = aa
    request.session['final_data_1'] = f_list
    request.session['csv_path'] = f'{base_path_server}uploads/{filename}'
    request.session['csv_name'] = f'{filename.split("/")[-1]}'
    request.session['hidden_msc'] = msc
    request.session['hidden_subject'] = subject_name
    request.session['hidden_branch'] = branch_name
    request.session['hidden_semester'] = semester_name
    request.session['hidden_batch'] = batch_name
    request.session['hidden_result_roll'] = result_roll


# Request For Download Result
def download_csv(request):
    if request.method == 'POST':
        # Get path to csv file
        csv_path = request.session.get('csv_path')

        if os.path.exists(csv_path):
            with open(csv_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/csv")
                csv_name = request.session.get('csv_name')
                response['Content-Disposition'] = f'attachment; filename={csv_name}'
                return response

        raise '404'
    else:
        return redirect('/verification/')


# Request For Showing Uploaded Result
def verify_data(request):
    passwordss = {'sid': f'verification'}
    mse = request.session.get('hidden_msc')
    subject_name = request.session.get('hidden_subject')
    branch_name = request.session.get('hidden_branch')
    sem = request.session.get('hidden_semester')
    batch = request.session.get('hidden_batch')

    if not mse:
        passwordss['vname'] = f'Verification Page'
    else:
        passwordss['vname'] = f'{batch} Sem {sem} {branch_name} {subject_name} Mse {mse}'
    return render(request, 'upload-verify_data.html', passwordss)


# Request For Showing Uploaded Actual Roll
def verify_data_div_list(request):
    main_access = get_user(request, 1)
    if not main_access:
        if request.session.get('enrollment'):
            logger(request, request.session.get('enrollment'), 'Denied Entry')
        else:
            logger(request, '', 'Denied Entry')
        messages.error(request, 'Upload division page access denied due to lack of authorization......!')
        return redirect(f'/verification/')

    passwordss = {'sid': f'verifications'}
    branch_name = request.session.get('hidden_branch')
    sem = request.session.get('hidden_semester')
    batch = request.session.get('hidden_batch')

    x_lists = request.session.get('table_aa')
    try:
        obj = get_profile(x_lists[0]['data'][0]['enroll'])
        branch_name = obj.branch
        batch = obj.batch.batch_name
    except:
        pass

    if not sem:
        passwordss['vname'] = f'Verification Page'
    else:
        passwordss['vname'] = f'{batch} Sem {sem} {branch_name}'
    return render(request, 'upload-verify_data_roll.html', passwordss)


# Delete Uploaded Result, Actual Roll } Verification Page Session
def verify_data_delete(request):
    if request.method == 'POST':
        if request.session.get('enrollment'):
            logger(request, request.session['enrollment'], '')

        delete_session(request)
        messages.success(request, 'Uploaded Result Deleted Successfully.....!')

    logger_send(request)
    return redirect('/upload/')


# Request For Changing Marks
@csrf_exempt
def update_item(request, item_id):
    if request.method == 'POST':
        if request.session.get('enrollment'):
            logger(request, request.session['enrollment'], '')
        data = json.loads(request.body)
        field = data.get('field', '')
        value = data.get('value', '')

        try:
            data_list_1 = request.session.get('final_data')
            data_list_2 = request.session.get('table_aa')
            for i in range(len(data_list_1)):
                if int(data_list_1[i][1]) == item_id:
                    if field == 'section_1':
                        data_list_1[i][-3] = value
                    elif field == 'section_2':
                        data_list_1[i][-2] = value

                    break
            for j in range(len(data_list_2[0]['data'])):
                if int(data_list_2[0]['data'][j]['enroll']) == item_id:
                    if field == 'section_1':
                        data_list_2[0]['data'][j]['section_1'] = value
                    elif field == 'section_2':
                        data_list_2[0]['data'][j]['section_2'] = value

                    break
            request.session['final_data'] = data_list_1
            request.session['table_aa'] = data_list_2

            return JsonResponse({'message': 'Item updated successfully'})
        except:
            return JsonResponse({'message': 'Item not found'}, status=404)

    else:
        logger_send(request)
        return redirect('/verification/')


# Update Contacts
def update_contacts(c_list):
    count = 0
    for i in c_list:
        try:
            obj = get_profile(i['enroll'])
            if int(obj.contact) == 0:
                obj.contact = i['contact']
                obj.save()
                count += 1
        except:
            pass
    return count


"""
-->                                              Upload Result End
######################################################################################################################
"""

"""
######################################################################################################################
-->                                 Student Profile, Branch, Subject View Start
"""


def sort_branches(semester):
    return sorted(semester['list'], key=lambda x: (x['Access'] == 'False', x['branch']))


# Request For View All Branch List
def branch_view(request):
    logger_send(request)
    temp_obj_1 = list(
        SubjectModel.objects.filter(student__enrollment_number=request.session.get('userid')).values('sem__sem_name',
                                                                                                     'student__branch',
                                                                                                     'student__batch__batch_name').distinct())
    temp_obj = list(
        SubjectModel.objects.values('sem__sem_name', 'student__branch', 'student__batch__batch_name').distinct())
    list_1 = [{**item, 'Access': 'False'} for item in temp_obj if item not in temp_obj_1]
    list_2 = [{**item, 'Access': 'True'} for item in temp_obj_1]

    temp_obj_2 = list_1 + list_2
    branch_obj = {}
    for i in temp_obj_2:
        batch = i['student__batch__batch_name']
        sem = i['sem__sem_name']
        branch = i['student__branch']
        access = i['Access']

        if batch not in branch_obj:
            branch_obj[batch] = {}

        if sem not in branch_obj[batch]:
            branch_obj[batch][sem] = []

        if branch not in branch_obj[batch][sem]:
            branch_obj[batch][sem].append(
                {
                    'branch': branch,
                    'Access': access
                }
            )

    final_temp = {}
    for batch, sem_list in branch_obj.items():
        final_temp[batch] = {}

        for sem, branch_list in sem_list.items():
            final_temp[batch][sem] = {}

            temp_count = len([item['Access'] for item in branch_list if item['Access'] == 'True'])
            main_access = "True" if temp_count > 0 else "False"
            final = {
                'Main_access': main_access,
                'list': branch_list
            }

            final_temp[batch][sem] = final

    sorted_branch_obj = {
        year: {sem: {'Main_access': semester['Main_access'], 'list': sort_branches(semester)} for sem, semester in
               sorted(semesters.items())} for year, semesters in sorted(final_temp.items())}

    items = {
        'sid': 'branchs',
        'vname': f'Branch Wise Rank List',
        'home_': 'Branch_1',
        'branch_obj': sorted_branch_obj
    }

    keys = request.GET.get('keys')
    if keys:
        try:
            keys = keys.split('/')[1:-1]
            items['key_branch_all'] = f'{keys[3]}_{keys[2]}'
        except:
            pass

    return render(request, 'branch-all.html', items)


# Request For View All Subject List
def subject_view(request):
    logger_send(request)
    items = {
        'sid': 'sub',
        'vname': f'Subject Wise MSE Result',
        'home_': 'subject',
    }
    keys = request.GET.get('keys')
    if keys:
        try:
            keys = keys.split('/')[1:-1]
            items['key_subject_all_1'] = f'{keys[0]}_{keys[1]}_{keys[2]}_{keys[4]}'
            items['key_subject_all'] = f'{keys[0]}_{keys[1]}_{keys[4]}'
        except:
            try:
                items['key_subject_all_1'] = f'{keys[0]}_{keys[1]}_{keys[3]}'
            except:
                pass

    return render(request, 'subject-all.html', items)


# Request For View All Student List
@custom_login_required
def student_view(request):
    access = get_user(request, 1)
    if not access:
        all_student, title, vname = None, None, None
    else:
        all_student = StudentDataModel.objects.all()
        title, vname = 'All Student List', 'All Student List'

    group_by = {}

    if not all_student:
        get_profile_data = get_profile(request.session.get('userid'))
        all_student = StudentDataModel.objects.filter(branch=get_profile_data.branch, batch=get_profile_data.batch)
        title, vname = f'Your Branch Student List', 'Student List'

    for i in all_student:
        key = f'{i.branch}_{i.batch}'
        if int(i.batch.batch_name) == 2021:
            f = 'Regular 2021 & D2D 2022'
        else:
            f = 'Regular 2022 & D2D 2023'
        if key in group_by:
            group_by[key]['list'].append(i)
        else:
            group_by[key] = {
                'list': [i],
                'branch': i.branch,
                'batch': i.batch.batch_name,
                'key_': f,
                'count': len(group_by) + 1
            }

    items = {
        'title': f'{title}',
        'all_student': group_by,
        'hid': f'students',
        'sid': 'students',
        'vname': f'{vname}',
        'home_': f'students',
    }

    return render(request, 'student-all.html', items)


# Request For View All Faculty List
@custom_login_required
def faculty_view(request):
    main_access = get_user(request, 1)
    if not main_access:
        enroll = request.session.get('userid')
        messages.error(request, 'Faculties page access denied due to lack of authorization......!')
        return redirect(f'/{enroll}/')

    access = get_user(request, 0)
    title, vname = 'All Faculty List', 'All Faculty List'

    all_faculty = FacultyDataModel.objects.all()

    items = {
        'title': f'{title}',
        'faculty_obj': all_faculty,
        'hid': f'faculty',
        'sid': 'faculty',
        'vname': f'{vname}',
        'home_': f'faculty',
    }

    return render(request, 'all_faculty.html', items)


def div_list_dynamic(enroll, sem):
    obj = actualroll_pro(enroll, sem)
    return [obj.roll_no, obj.division]


# Request For Get Student Profile Data
def get_grouped_data(branch, sem, batch, check, subname=None):
    grouped_data = ''
    if not subname:
        if check == 1:
            grouped_data = SubjectModel.objects.filter(
                student__branch=branch, sem__sem_name=sem, student__batch__batch_name=batch
            ) \
                .values(
                'student__enrollment_number',
                'student__name',
                'student__branch',
                'student__division',
                'student__batch__batch_name'
            ) \
                .exclude(
                subject__subject_name='ic'
            ) \
                .annotate(
                total_mark=Sum('section_A') + Sum('section_B'),
                subjects_count=Count('id')
            ) \
                .order_by('-total_mark')

            counts = 0
            for i in range(len(grouped_data)):
                try:
                    grouped_data[i]['a_roll_no'], grouped_data[i]['a_division'] = \
                        div_list_dynamic(grouped_data[i]['student__enrollment_number'], int(sem) + 1)
                    counts += 1
                except:
                    pass
                try:
                    grouped_data[i]['p_division'] = get_rank(branch, batch, i + 1)
                except:
                    grouped_data[i]['p_division'] = "Not Available"
            if counts == 0:
                count_ = 'no'
            else:
                count_ = 'yes'
            return grouped_data, count_

        elif check == 2:
            grouped_data = SubjectModel.objects.filter(student__branch=branch, semester=sem, student__batch='') \
                .values(
                'student__enrollment_number',
                'student__name',
                'student__branch',
                'student__division'
            ) \
                .exclude(
                subject__subject_name='cpdp') \
                .annotate(
                total_mark=Sum('section_A') + Sum('section_B'),
                subjects_count=Count('id')
            ) \
                .order_by('-total_mark')

        elif check == 3:
            grouped_data = SubjectModel.objects \
                .filter(
                student__branch=branch, sem__sem_name=sem, student__batch__batch_name=batch
            ) \
                .values(
                'student__enrollment_number',
                'student__name',
            ) \
                .exclude(
                subject__subject_name='ic'
            ) \
                .annotate(
                total_mark=Sum('section_A') + Sum('section_B'),
                subjects_count=Count('id')
            ) \
                .order_by('-total_mark')

        elif check == 5:
            grouped_data = SubjectModel.objects.filter(
                student__branch=branch, sem__sem_name=sem, student__batch__batch_name=batch
            ) \
                .values(
                'student__enrollment_number',
                'student__name',
                'student__branch',
                'student__division',
                'student__batch__batch_name'
            ) \
                .exclude(
                subject__subject_name='cpdp'
            ) \
                .annotate(
                total_mark=Sum('section_A') + Sum('section_B'),
                subjects_count=Count('id')
            ) \
                .order_by('-total_mark')

    else:
        if check == 1:
            grouped_data = SubjectModel.objects.filter(
                student__branch=branch, sem__sem_name=sem, student__batch__batch_name=batch,
                subject__subject_name=subname
            ) \
                .values(
                'student__enrollment_number',
                'student__name',
                'student__branch',
                'student__division',
                'student__batch__batch_name'
            ) \
                .annotate(
                total_mark=Sum('section_A') + Sum('section_B'),
                subjects_count=Count('id')
            ) \
                .order_by('-total_mark')
        elif check == 2:
            queryset = SubjectModel.objects.filter(
                student__branch=branch,
                sem__sem_name=sem,
                student__batch__batch_name=batch
            ).values(
                'student__enrollment_number',
                'student__name',
                'student__branch',
                'student__division',
                'student__batch__batch_name'
            ).exclude(
                subject__subject_name='cpdp'
            )

            for subject_name in subname:
                queryset = queryset.exclude(subject__subject_name=subject_name)

            # Annotate and order the queryset
            grouped_data = queryset.annotate(
                total_mark=Sum('section_A') + Sum('section_B'),
                subjects_count=Count('id')
            ).order_by('-total_mark')

            grouped_data

    return grouped_data


# Request For Get Predicted Roll No
def get_rank(check_branch, check_batch, rank):
    div = ''
    if check_branch.lower() == 'aiml' and int(check_batch) == 2021:
        if 1 <= rank <= 33:
            div = 'D1'
        elif 34 <= rank <= 66:
            div = 'D2'
        elif 67 <= rank <= 99:
            div = 'D3'
        else:
            div = 'D4'

    elif check_branch.lower() == 'it' and int(check_batch) == 2021:
        if 1 <= rank <= 39:
            div = 'D1'
        else:
            div = 'D2'

    elif check_branch.lower() == 'cse' and int(check_batch) == 2021:
        if 1 <= rank <= 37:
            div = 'D1'
        else:
            div = 'D2'

    elif check_branch.lower() == 'cse' and int(check_batch) == 2022:
        if 1 <= rank <= 37:
            div = 'D1'
        elif 38 <= rank <= 74:
            div = 'D2'
        elif 75 <= rank <= 111:
            div = 'D3'
        elif 112 <= rank <= 147:
            div = 'D4'
        elif 148 <= rank <= 183:
            div = 'D5'
        else:
            div = 'D6'

    elif check_branch.lower() == 'aiml' and int(check_batch) == 2022:
        if 1 <= rank <= 39:
            div = 'D1'
        else:
            div = 'D2'

    return div


def get_division_list(check_branch, check_batch):
    div = ''
    if check_branch.lower() == 'aiml' and int(check_batch) == 2021:
        div = [33, 66, 99]

    elif check_branch.lower() == 'it' and int(check_batch) == 2021:
        div = [39]

    elif check_branch.lower() == 'cse' and int(check_batch) == 2021:
        div = [37]

    elif check_branch.lower() == 'cse' and int(check_batch) == 2022:
        div = [37, 74, 111, 147, 183]

    elif check_branch.lower() == 'aiml' and int(check_batch) == 2022:
        div = [39]

    return div


# Request For Get Sem List
def get_sem(request, enroll, check):
    if check:
        if not check.isdigit():
            return [True, redirect(f'/{enroll}/1/')]

    subject_obj_ = SubjectModel.objects \
        .filter(
        student__enrollment_number=enroll
    ).values(
        'subject__subject_name',
        'sem__sem_name'
    ) \
        .distinct()
    sem_s = []
    for i in subject_obj_:
        if not i['sem__sem_name'] in sem_s:
            sem_s.append(int(i['sem__sem_name']))

    sem_s.sort()

    sem = 6
    if sem_s:
        sem = sem_s[-1]

    # if int(check) in sem_s and int(check) != 0:
    #     sem = check
    # else:
    #     enrolls = request.session.get('userid')
    #     if enrolls:
    #         try:
    #             get_profile(enroll)
    #         except:
    #             if get_student(request).user_type == 'faculty':
    #                 messages.success(request, 'Enrollment Number Not Found.....!')
    #                 return [True, redirect(f'/students/')]
    #             else:
    #                 return [True, redirect(f'/{enrolls}/{sem}/')]
    #     else:
    #         messages.success(request, 'First Login.....!')
    #         return [True, redirect(f'/login/?next=/{enroll}/')]
    #
    #     return [True, redirect(f'/{enroll}/{sem}/')]
    #
    # return [False, sem]
    if int(check) in sem_s and int(check) != 0:
        sem = check
    else:
        try:
            get_profile(enroll)
        except:
            try:
                if get_student(request).user_type == 'faculty':
                    messages.success(request, 'Enrollment Number Not Found.....!')
                    return [True, redirect(f'/students/')]
            except:
                return [True, redirect(f'/login/?next=/{enroll}/{sem}/')]

            enroll = request.session.get('userid')
        return [True, redirect(f'/{enroll}/{sem}/')]

    return [False, sem, sem_s]


# Request For Student Profile Data | Dynamic
def student_dynamic(request, enroll, check):
    try:
        con, sem = get_sem(request, enroll, check)
    except:
        con, sem, sem_list = get_sem(request, enroll, check)
    if con:
        return sem

    access = get_user(request, 1)
    if not access:
        enroll_1 = request.session.get('userid')

        if enroll_1:
            temp_1 = get_profile(enroll_1)
            temp = get_profile(enroll)
        else:
            messages.success(request, 'First Login.....!')
            return redirect(f'/login/?next=/{enroll}/{check}/')
        if int(temp_1.batch.batch_name) != int(temp.batch.batch_name) or temp_1.branch.lower() != temp.branch.lower():
            messages.success(request, 'Select The Student Below......!')
            return redirect('/students/')

    try:
        rank = 0
        ranks = 0
        try:
            student_obj = get_profile(enroll)
            check_branch = student_obj.branch
            batch = student_obj.batch.batch_name
            if enroll.startswith('21') and int(batch) == 2021:
                f_ = 'Regular 2021'
            elif enroll.startswith('22') and int(batch) == 2021:
                f_ = 'D2D 2022'
            elif enroll.startswith('22') and int(batch) == 2022:
                f_ = 'Regular 2022'
            else:
                f_ = 'D2D 2023'
            student_obj.batch_name_1 = f_
            count_rank = get_grouped_data(check_branch, sem, batch, 3)
            for i in range(len(count_rank)):
                if int(count_rank[i]['student__enrollment_number']) == int(enroll):
                    rank = i + 1
                    break

            subject_obj = SubjectModel.objects.filter(student=student_obj.id, sem__sem_name=sem)
            subjects = {}
            subject_f = {}
            total = 0
            for k in subject_obj:
                if k.subject.subject_name in subjects:
                    if k.msc.msc_name == 1:
                        subjects[k.subject.subject_name]['Mse_1'] = k.section_A + k.section_B
                    else:
                        subjects[k.subject.subject_name]['Mse_2'] = k.section_A + k.section_B
                else:
                    if k.msc.msc_name == 1:
                        subjects[k.subject.subject_name] = {
                            'Mse_1': k.section_A + k.section_B,
                        }
                    else:
                        subjects[k.subject.subject_name] = {
                            'Mse_2': k.section_A + k.section_B,
                        }
                s = k.subject.subject_name.replace('_', '').replace('-', '')
                if s not in subject_f:
                    code_list = []
                    check_code = k.subject.subject_full_name
                    for i in check_code.split('(')[1].split(')')[0].split(','):
                        c_ = i.strip()
                        if c_:
                            code_list.append(c_)

                    final_code = ', '.join([
                                               f'<a class="text-info" href="https://s3-ap-southeast-1.amazonaws.com/gtusitecirculars/Syallbus/{code}.pdf" target="_blank">{code}</a>'
                                               for code in code_list])

                    subject_f[s] = {
                        'f_name': f'{check_code.split("(")[0]}',
                        'code': f'{final_code}'
                    }

                total += k.section_A
                total += k.section_B
            student_obj.total_mark = total

            subject_name = list(subjects.keys())
            subject_fullname = subject_f
            mse_1 = []
            mse_2 = []
            avg = []
            demo_list = []
            for i, j in subjects.items():
                if 'Mse_1' in j:
                    mse_1.append(j['Mse_1'])
                else:
                    mse_1.append(0)
                if 'Mse_2' in j:
                    mse_2.append(j['Mse_2'])
                else:
                    mse_2.append(0)
                m_1 = j['Mse_1'] if 'Mse_1' in j else 0
                m_2 = j['Mse_2'] if 'Mse_2' in j else 0
                if 'Mse_2' in j:
                    demo_list.append(i)

                val = math.ceil((m_1 + m_2) / 4)
                avg.append(val)

            if check_branch.lower() == 'aiml' and int(student_obj.batch.batch_name) == 2021:
                if 1 <= rank <= 33:
                    div = 'D1'
                elif 34 <= rank <= 66:
                    div = 'D2'
                elif 67 <= rank <= 99:
                    div = 'D3'
                else:
                    div = 'D4'

                student_obj.predicted_division = div
                if 1 <= ranks <= 33:
                    div = 'D1'
                elif 34 <= ranks <= 66:
                    div = 'D2'
                elif 67 <= ranks <= 99:
                    div = 'D3'
                else:
                    div = 'D4'
                student_obj.predicted_divisions = div
            elif check_branch.lower() == 'it':
                if 1 <= rank <= 39:
                    div = 'D1'
                else:
                    div = 'D2'

                student_obj.predicted_division = div
                if 1 <= ranks <= 39:
                    div = 'D1'
                else:
                    div = 'D2'
                student_obj.predicted_divisions = div
            elif check_branch.lower() == 'cse' and int(student_obj.batch.batch_name) == 2021:
                if 1 <= rank <= 37:
                    div = 'D1'
                else:
                    div = 'D2'

                student_obj.predicted_division = div
                if 1 <= ranks <= 37:
                    div = 'D1'
                else:
                    div = 'D2'
                student_obj.predicted_divisions = div
            elif check_branch.lower() == 'cse' and int(student_obj.batch.batch_name) == 2022:
                if 1 <= rank <= 37:
                    div = 'D1'
                elif 38 <= rank <= 74:
                    div = 'D2'
                elif 75 <= rank <= 111:
                    div = 'D3'
                elif 112 <= rank <= 147:
                    div = 'D4'
                elif 148 <= rank <= 183:
                    div = 'D5'
                else:
                    div = 'D6'
                student_obj.predicted_division = div
            elif check_branch.lower() == 'aiml' and int(student_obj.batch.batch_name) == 2022:
                if 1 <= rank <= 39:
                    div = 'D1'
                else:
                    div = 'D2'
                student_obj.predicted_division = div

        except:
            if request.session.get('type'):
                return redirect('/students/')
            else:
                return redirect(f'/{enroll}/')

        objs = {}

        c_ = 5 - len(demo_list)

        check_session = request.session.get('list_data')
        if c_ > 0:
            if check_session:
                obj, count_range = know_your_division_1(
                    check_branch,
                    check,
                    student_obj.batch.batch_name,
                    int(enroll),
                    c_,
                    demo_list,
                    request
                )
            else:
                obj, count_range = know_your_division(
                    check_branch,
                    check,
                    student_obj.batch.batch_name,
                    int(enroll),
                    c_,
                    demo_list
                )

            objs = {}
            count_obj = 0
            for i in range(len(obj)):
                status = []
                checks = count_range[i].split('-')
                divi_name = get_rank(check_branch, student_obj.batch.batch_name, int(checks[0]))
                if checks[0] == checks[1]:
                    s = checks[0]
                else:
                    s = count_range[i]
                if obj[i] > 60:
                    status = [s, f"Not Possible ({obj[i]})"]
                objs[f'{divi_name}'] = status if status else [s, obj[i]]
                try:
                    if int(f'{obj[i]}') == 0:
                        count_obj += 1
                except:
                    pass

            if count_obj == len(obj):
                objs = {}

        try:
            roll_list = div_list_dynamic(enroll, sem)
        except:
            roll_list = [student_obj.roll_no, student_obj.division]
        try:
            roll_list_1 = div_list_dynamic(enroll, int(sem) + 1)
        except:
            roll_list_1 = []

        if os.path.exists(f'{base_path_server}uploads/results/{batch}_{sem}/result_{enroll}.html'):
            ss = 'yes'
        else:
            ss = 'no'

        items = {
            'student_obj': student_obj,
            'student_data': subject_obj,
            'subjects_obj': subject_fullname,
            'hid': enroll,
            'vname': f'{enroll}',
            'home_': 'sem',
            'rank': rank,
            'sem': int(sem),
            'subject_val': subject_name,
            'mse_1': mse_1,
            'mse_2': mse_2,
            'avg': avg,
            'roll_list': roll_list,
            'roll_list_1': roll_list_1,
            'check_result': ss,
            'predicted_obj': objs,
            'count_subject': c_,
        }
        if int(request.session.get('userid')) == int(enroll):
            sid = 'perti'
        else:
            sid = 's_student'
            try:
                k, items['sem_list_1'] = sem_list.sort(), sem_list
            except:
                pass
        items['sid'] = sid
        if check_session:
            items['form'] = 'yes'

        return render(request, 'student-dashboard.html', items)
    except:
        try:
            return redirect(f'/{enroll}/1/')
        except:
            return redirect('/')


# Branch List
def branch_list():
    return ['cse', 'it', 'aiml']


# Request For Student Profile Data
def student_data(request, enroll):
    if enroll.isdigit():
        return student_dynamic(request, enroll, 0)
    elif enroll.lower() in branch_list():
        return redirect(f'/branch/{enroll}/')
    else:
        enroll = request.session.get('userid')
        if enroll:
            return redirect(f'/{enroll}/')
        else:
            messages.success(request, 'login first.....!')
            return redirect('/login/?next=/')


# Request For Student Profile Data, Branch Data
def student_branch_data(request, branch, hid):
    logger_send(request)
    branch_lists = branch_list()
    if branch.isdigit():
        start_number = request.GET.get('start_number')
        end_number = request.GET.get('end_number')
        c_1 = start_number or end_number
        c_2 = request.session.get('list_data')
        c_3 = 'None'
        if c_1 or c_2:
            if c_1:
                c_3 = 'Yes'
            elif c_2:
                c_3 = 'No'
            else:
                c_3 = 'Other'

        if c_1 or c_2:
            if c_3 == 'Yes':
                try:
                    if start_number:
                        start_number = int(start_number)
                except:
                    if start_number.isascii():
                        logger(request, request.session.get('enrollment'), f'{start_number} | Start Number Error')
                    return redirect(f'{request.path}')

                try:
                    if end_number:
                        end_number = int(end_number)
                except:
                    end_number = ''

                logger(request, request.session.get('enrollment'), f'{start_number}:{end_number} | Enter Range')

                if not start_number:
                    messages.success(request, 'Adjust Range Values For Accuracy.')
                    return redirect(f'{request.path}')

                if start_number == end_number:
                    end_number = start_number + 5

                if not end_number:
                    end_number = int(start_number)

                if start_number > end_number:
                    start_number, end_number = end_number, start_number

                s = f'{start_number}-{end_number}'.split('-')

                try:
                    count_numbers_between = int(s[1]) - int(s[0]) + 1
                except:
                    messages.success(request, 'Adjust Range Values For Accuracy.')
                    return redirect(f'{request.path}')

                if count_numbers_between > 11:
                    messages.success(request, 'Please Select Range Between 10.....!')
                    return redirect(f'{request.path}')

                get_profile_data = get_profile(branch)
                all_student = StudentDataModel.objects.filter(
                    branch=get_profile_data.branch,
                    batch=get_profile_data.batch
                )

                if start_number > len(all_student):
                    messages.success(request, f'Enter Range Below {len(all_student)}.....!')
                    return redirect(f'{request.path}')

                if end_number > len(all_student):
                    end_number = len(all_student)

                request.session['list_data'] = f'{start_number}-{end_number}'
                logger(request, request.session.get('enrollment'), f'{start_number}:{end_number} | Final Range')

                return redirect(f'{request.path}')

            elif c_3 == 'No':
                try:
                    dd = student_dynamic(request, branch, hid)
                except:
                    try:
                        del request.session['list_data']
                    except:
                        pass

                    messages.success(request, 'Adjust Range Values For Accuracy.')
                    return redirect(f'{request.path}')

                try:
                    del request.session['list_data']
                except:
                    pass

                return dd

        return student_dynamic(request, branch, hid)
    elif branch.lower() == 'branch':
        return branch_dynamic(request, hid, '0', 0)
    elif branch.lower() in branch_lists or hid.lower() in branch_lists:
        branch_name = branch if branch.lower() in branch_lists else hid
        return redirect(f'/branch/{branch_name}/')
    else:
        enroll = request.session.get('userid')
        if enroll:
            return redirect(f'/{enroll}/')
        else:
            messages.success(request, 'login first.....!')
            return redirect('/login/?next=/')


def get_div(original_list, check):
    if check == 0:
        output_list = []

        for i, n in enumerate(original_list):
            if i == len(original_list) - 1:  # Check if it's the last element in the list
                output_list.extend(range(original_list[-2] + 1, original_list[-2] + 6))
            else:
                output_list.extend(range(n - 5, n))

        return output_list
    else:
        output_a = []
        output_b = []

        start, end = map(int, check.split('-'))

        for num in original_list:
            if start <= num <= end:
                output_a.append(f'{start}-{num}')
                output_b.extend(range(start, num + 1))
                start = num + 1  # Update the start for the next range

        if start <= end:
            output_a.append(f'{start}-{end}')
            output_b.extend(range(start, end + 1))

        return output_a, output_b


def get_div_1(original_list):
    ranges = []
    start = original_list[0]
    end = original_list[0]

    for num in original_list[1:]:
        if num == end + 1:
            end = num
        else:
            ranges.append(f'{start}-{end}')
            start = num
            end = num

    ranges.append(f'{start}-{end}')
    return ranges


def get_avg(original_list, count, count_subject, check):
    if check == 0:
        start = 0
        end = 5
        final_list = []
        for j in range(count):
            total_a = 0
            for i in original_list[start:end]:
                total_a = total_a + i
            final = math.ceil((total_a / 5) / count_subject)
            final_list.append(final)
            start += 5
            end += 5

        return final_list

    else:
        final_list = []
        start = 0

        for i in range(len(check)):
            s = check[i].split('-')
            count_numbers_between = int(s[1]) - int(s[0]) + 1
            end = start + count_numbers_between

            total_a = 0
            for j in original_list[start:end]:
                total_a = total_a + j
            final = math.ceil((total_a / count_numbers_between) / count_subject)
            final_list.append(final)

            start += count_numbers_between

        return final_list


# Request For View Particular Branch Data | Dynamic
def branch_dynamic(request, branch_name, sem, batch):
    if not request.session.get('type'):
        enroll = request.session.get('userid')
        if sem.isdigit():
            sem = int(sem)
        if not type(sem) == int:
            con, sem = get_sem(request, enroll, sem)
            sem = sem.url.split('/')[-2]
        elif int(sem) == 0:
            con, sem = get_sem(request, enroll, sem)
            sem = sem.url.split('/')[-2]

    batch_temp = YearBatchModel.objects.all().first().batch_name
    if batch == 0:
        if request.session.get('type') == 'faculty':
            batch = batch_temp
            sem = SemModel.objects.all().first().sem_name
            return redirect(f'/branch/{branch_name}/{sem}/{batch}/')

        if enroll:
            get_batch = get_profile(enroll).batch.batch_name
            return redirect(f'/branch/{branch_name}/{sem}/{get_batch}/')
        else:
            return redirect(f'/branch/{branch_name}/{sem}/{batch_temp}/')

    branch = branch_name.lower()
    if branch != 'aiml' and branch != 'cse' and branch != 'it':
        messages.error(request, 'Branch Not Found.....!')
        return redirect('/branch/')

    access = get_user(request, 1)
    if not access:
        if enroll:
            temp = get_profile(enroll)
        else:
            messages.error(request, 'login first.....!')
            return redirect(f'/login/?next=/branch/{branch_name}/{sem}/{batch}/')
        if int(temp.batch.batch_name) != int(batch) or temp.branch.lower() != branch_name.lower():
            messages.error(request, 'You are not authorized to access.....!')
            return redirect(f'/branch/?keys=/branch/{branch_name}/{sem}/{batch}/')

    grouped_data, yes_no = get_grouped_data(branch, sem, batch, 1)
    if not grouped_data:
        try:
            temp_sem_1 = SubjectModel.objects.filter(student__batch__batch_name=batch).first().sem.sem_name
            if not temp_sem_1:
                temp_sem_1 = SemModel.objects.exclude(sem_name=sem).first().sem_name
            messages.error(request, 'No Data Found, Please Select Another Semester.....!')
            return redirect(f'/branch/?keys=/branch/{branch_name}/{temp_sem_1}/{batch}/')
        except:
            temp_batch = 2021
            temp_sem_1 = SemModel.objects.exclude(sem_name=sem).first().sem_name
            messages.error(request, 'No Data Found, Please Select Another Batch.....!')
            return redirect(f'/branch/?keys=/branch/{branch_name}/{temp_sem_1}/{temp_batch}/')

    for i in grouped_data:
        i['total_marks'] = i['total_mark'] / 4

    items = {
        'subjectdata_obj': grouped_data,
        'sid': f'branchs',
        'home_': f'Branch_2',
        'hid': branch.upper(),
        'main_sid': f'{branch.upper()}',
        'vname': f'{branch.upper()} sem {sem} Rank',
        'branch': branch.upper(),
        'sem': sem,
        'batch': batch,
        'check_roll': yes_no
    }
    return render(request, 'branch-show.html', items)


def know_your_division(branch, sem, batch, enroll, count_subject, subject_name_list):
    """
        grouped_data == Total Marks
        grouped_data_1 == Total Marks Without CPDP, IC
        remaining_data == Total Marks Of mse 1 and mse 2 if mse 2 is avail
    """
    grouped_data = get_grouped_data(branch, sem, batch, 1)
    grouped_data_1 = get_grouped_data(branch, sem, batch, 1, 'cpdp')

    if not subject_name_list:
        subject_name_list = ['']
    remaining_data = get_grouped_data(branch, sem, batch, 2, subject_name_list)

    cc = 1
    if not grouped_data_1:
        cc = 0
        grouped_data_1 = get_grouped_data(branch, sem, batch, 2, subject_name_list)

    div_list = get_division_list(branch, batch)
    div_list.append(len(grouped_data_1))
    main_div_list = get_div(div_list, 0)

    total_mark_enrollment = {data['student__enrollment_number']: data['total_mark']
                             for data in grouped_data[0]}

    remaining_data_ = {data['student__enrollment_number']: data['total_mark']
                       for data in remaining_data}

    for data in grouped_data_1:
        enrollment_number = data['student__enrollment_number']

        total_mark = total_mark_enrollment[enrollment_number]
        total_mark_1 = remaining_data_[enrollment_number]
        total_marks = data['total_mark']

        if cc == 0:
            total_marks = 0

        temp = int(total_mark) - int(total_mark_1) - int(total_marks)

        total_mark_enrollment.setdefault(enrollment_number, 0)
        total_mark_enrollment[enrollment_number] = (total_mark_1 * 2) + temp + int(total_marks)

    filtered_indexes = [index for index, group in enumerate(grouped_data[0]) if
                        group['student__enrollment_number'] == enroll][0]

    d = []
    for i in range(len(grouped_data_1)):
        if i + 1 in main_div_list:
            marks = total_mark_enrollment[grouped_data[0][i]['student__enrollment_number']] - \
                    grouped_data[0][filtered_indexes]['total_mark']
            d.append(marks)

    final_d = get_avg(d, len(div_list), count_subject, 0)
    main_div_list_1 = get_div_1(main_div_list)

    return final_d, main_div_list_1


def know_your_division_1(branch, sem, batch, enroll, count_subject, subject_name_list, request):
    list_data = request.session['list_data']

    grouped_data = get_grouped_data(branch, sem, batch, 1)
    grouped_data_1 = get_grouped_data(branch, sem, batch, 1, 'cpdp')

    if not subject_name_list:
        subject_name_list = ['']

    cc = 1
    if not grouped_data_1:
        cc = 0
        grouped_data_1 = get_grouped_data(branch, sem, batch, 2, subject_name_list)

    remaining_data = get_grouped_data(branch, sem, batch, 2, subject_name_list)

    div_list = get_division_list(branch, batch)
    div_list.append(len(grouped_data_1))
    div_list, main_div_list = get_div(div_list, list_data)

    total_mark_enrollment = {data['student__enrollment_number']: data['total_mark']
                             for data in grouped_data[0]}

    remaining_data_ = {data['student__enrollment_number']: data['total_mark']
                       for data in remaining_data}

    for data in grouped_data_1:
        enrollment_number = data['student__enrollment_number']

        total_mark = total_mark_enrollment[enrollment_number]
        total_mark_1 = remaining_data_[enrollment_number]
        total_marks = data['total_mark']

        if cc == 0:
            total_marks = 0

        temp = int(total_mark) - int(total_mark_1) - int(total_marks)

        total_mark_enrollment.setdefault(enrollment_number, 0)
        total_mark_enrollment[enrollment_number] = (total_mark_1 * 2) + temp + int(total_marks)

    filtered_indexes = [index for index, group in enumerate(grouped_data[0]) if
                        group['student__enrollment_number'] == enroll][0]

    d = []
    for i in range(len(grouped_data_1)):
        if i + 1 in main_div_list:
            marks = total_mark_enrollment[grouped_data[0][i]['student__enrollment_number']] - \
                    grouped_data[0][filtered_indexes]['total_mark']
            d.append(marks)

    final_d = get_avg(d, len(div_list), count_subject, div_list)

    return final_d, div_list


# Request For View Particular Branch Data
def branch_data_1(request, branch, name, sem):
    b_list = branch_list()
    if branch.lower() == 'branch':
        return branch_dynamic(request, name, sem, 0)
    elif name.lower() in b_list or sem.lower() in b_list:
        branch_name = name if name.lower() in b_list else sem
        if not sem.isdigit():
            return redirect(f'/branch/{branch_name}/')
        else:
            return redirect(f'/branch/{branch_name}/{sem}/')
    else:
        logger_send(request)
        return render(request, '404.html', {'key': 404}, status=404)


# Request For View Particular Branch Data
def branch_data_2(request, branch, name, sem, batch):
    logger_send(request)
    sem = f'{sem}'
    b_list = branch_list()
    if branch.lower() == 'branch':
        return branch_dynamic(request, name, sem, batch)
    elif name.lower() in b_list or batch.lower() in b_list:
        branch_name = name if name.lower() in b_list else batch
        if not batch.isdigit():
            return redirect(f'/branch/{branch_name}/')
        else:
            return redirect(f'/branch/{branch_name}/{batch}/')
    else:
        return render(request, '404.html', {'key': 404}, status=404)


# Request For View Particular Subject Data | Dynamic
def subject_dynamic(request, sem, branch, subject, mse, batch):
    enroll = request.session.get('userid')
    get_batch = YearBatchModel.objects.all().first().batch_name
    if int(batch) == 0:
        if enroll:
            if len(enroll) == 12:
                get_batch = get_profile(enroll).batch.batch_name
        return redirect(f'/{sem}/{branch}/{subject}/{mse}/{get_batch}/')

    access = get_user(request, 1)
    if not access:
        if enroll:
            temp = get_profile(enroll)
        else:
            messages.error(request, 'login first.....!')
            return redirect(f'/login/?next=/{sem}/{branch}/{subject}/{mse}/{get_batch}/')
        if int(temp.batch.batch_name) != int(batch) or temp.branch.lower() != branch.lower():
            messages.error(request, 'You are not authorized to access.....!')
            return redirect(f'/subject/?keys=/{sem}/{branch}/{subject}/{mse}/{batch}/')

    if subject.lower() == 'cpdp' and int(mse) == 2:
        return redirect(f'/{sem}/{branch}/{subject}/1/')
    try:
        MscNameModel.objects.get(msc_name=mse)
    except:
        messages.error(request, f'No Data Found For MSE {mse}.....!')
        return redirect(f'/{sem}/{branch}/{subject}/1/{batch}/')

    try:
        main_subject_obj = SubjectNameModel.objects.get(subject_name=subject)
    except:
        username = request.session.get('userid')
        if username:
            messages.error(request, 'No Subject Found.....!')
            return redirect(f'/subject/?keys=/{sem}/{branch}/1/{batch}/')
        else:
            messages.error(request, 'login first.....!')
            return redirect(f'/login/?next=/{sem}/{branch}/{subject}/1/')

    obj = SubjectModel.objects \
        .filter(
        msc__msc_name=mse,
        subject__subject_name=subject,
        student__branch=branch,
        sem__sem_name=sem,
        student__batch__batch_name=batch
    ) \
        .annotate(
        total_mark=F('section_A') + F('section_B')
    ) \
        .order_by('-total_mark')

    if not obj:
        if int(mse) == 2:
            messages.error(request, 'No Data Found For MSE 2.....!')
            return redirect(f'/{sem}/{branch}/{subject}/1/{batch}/')
        try:
            sem = SubjectModel.objects.filter(subject__subject_name=subject).first().sem.sem_name
            batch = SubjectModel.objects.filter(subject__subject_name=subject).first().student.batch.batch_name
            branch = SubjectModel.objects.filter(subject__subject_name=subject).first().student.branch.lower()
            messages.error(request, 'No Data Found, Please Select Different Branch.....!')
            return redirect(f'/subject/?keys=/{sem}/{branch}/1/{batch}/')
        except:
            messages.error(request, 'No Data Found, Please Select Different Type.....!')
            return redirect(f'/subject/?keys=/{sem}/{branch}/1/{batch}/')

    for i in range(len(obj)):
        try:
            obj[i].a_roll_no, p = \
                div_list_dynamic(obj[i].student.enrollment_number, int(sem))
        except:
            try:
                obj[i].a_roll_no = obj[i].student.roll_no
            except:
                pass

    if int(mse) == 1:
        kk = 'yes'
    else:
        kk = 'no'

    if branch.lower() == 'cpdp':
        final_id = f'{branch.title()} Sem {sem} Marks'
    else:
        final_id = f'{branch.title()} Sem {sem} MSE {mse}'

    key_ = f'{sem}_{branch}_{subject}'
    key = [f'{sem}', f'{branch}', f'{subject}', f'{batch}']

    code_list = []
    check_code = main_subject_obj.subject_full_name
    for i in check_code.split('(')[1].split(')')[0].split(','):
        c_ = i.strip()
        if c_:
            code_list.append(c_)

    final_code = ', '.join([
                               f'<a class="text-info" href="https://s3-ap-southeast-1.amazonaws.com/gtusitecirculars/Syallbus/{code}.pdf" target="_blank">{code}</a>'
                               for code in code_list])
    subject = subject.replace('_', '').replace('-', '')
    items = {
        'subjectdata_obj': obj,
        'branch': branch.upper(),
        'main_sid': f'{subject}'.title(),
        'sid': f'sub',
        'home_': f'Subject_1',
        'sid_': f'{key_}',
        'key': key,
        'hid': f'{final_id} | Joining Batch {batch}',
        'vname': f'{subject.upper()} - Result',
        's_msc': kk,
        'sem': sem,
        'batch': batch,
        'code_list': final_code,
        'subject_name': check_code.split('(')[0]
    }

    return render(request, 'subject-show.html', items)


# Request For View Particular Subject Data
def subject_request_1(request, sem, branch, subject, mse):
    logger_send(request)
    return subject_dynamic(request, sem, branch, subject, mse, 0)


# Request For View Particular Subject Data
def subject_request_2(request, sem, branch, subject, mse, batch):
    logger_send(request)
    return subject_dynamic(request, sem, branch, subject, mse, batch)


"""
-->                                 Student Profile, Branch, Subject View End
######################################################################################################################
"""
