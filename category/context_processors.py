import os
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import Template, Context

from User.models import SubjectModel, RedirectModel, StudentDataModel, Profile
from User.views import get_user
from .models import CategoryModel

BASEURL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def count_student():
    try:
        student_obj = StudentDataModel.objects.all()
        profile_obj = Profile.objects.all()
        count = (len(profile_obj) * 100) / (len(student_obj))
        count = round(count, 2)
        return count, len(profile_obj)
    except:
        return 0, 0


def show_register_user(request):
    count, count_number = count_student()
    return {
        'count_number': count_number
    }


def dynamic_result_dict(temp_list, check):
    if check == 0:
        final_list = []
        for i in temp_list:
            final_list.append({
                'batch': i['student__batch__batch_name'],
                'semester': i['sem__sem_name'],
                'branch': i['student__branch'].lower(),
                'subject': i['subject__subject_name'].lower().replace('-', '').replace('_', ''),
                'subject_f': i['subject__subject_full_name'].split('(')[0],
            })
        return final_list
    else:
        result_dict = {}
        for subject in temp_list:
            batch = subject['batch']
            semester = subject['semester']
            branch = subject['branch']
            subject_name = subject['subject']
            subject_f = subject['subject_f']
            check = subject['Access']

            if batch not in result_dict:
                result_dict[batch] = {}

            if semester not in result_dict[batch]:
                result_dict[batch][semester] = {}

            if branch not in result_dict[batch][semester]:
                result_dict[batch][semester][branch] = []

            result_dict[batch][semester][branch].append(
                {
                    'subject_name': subject_name,
                    'subject_f': subject_f,
                    'Access': f'{check}'
                }
            )

        result_dict_1 = {}
        for year, months in result_dict.items():
            result_dict_1[year] = {}

            for month, subjects in months.items():
                result_dict_1[year][month] = {}

                for department, subject_list in subjects.items():
                    temp_count = len(
                        [item['Access'] for item in subject_list if item['Access'] == 'True'])
                    main_access = "True" if temp_count > 0 else "False"
                    final = {
                        'Main_access': main_access,
                        'list': subject_list
                    }

                    result_dict_1[year][month][department] = final

        return result_dict_1


def subcategory_processor(request):
    categories_with_sub = {}
    categories = CategoryModel.objects.prefetch_related(
        'sub').filter(deleted=False)

    for category in categories:
        # Using category instance as key and list of subcategories as value
        categories_with_sub[category] = list(
            category.sub.filter(deleted=False))

    return {'subcategories': categories_with_sub}


def subject_processor(request):
    username = request.session.get('userid')
    if not username and not request.path == '/subject/':
        return {}

    all_sub = []
    results = SubjectModel.objects.filter(student__enrollment_number=username). \
        values('student__branch', 'student__batch__batch_name', 'subject__subject_name',
               'subject__subject_full_name', 'sem__sem_name').distinct()
    results = list(results)
    all_sub += results
    s = []
    unique_sem = [s.append(sem['sem__sem_name'])
                  for sem in list(results) if sem['sem__sem_name'] not in s]
    k, unique_sem = s.sort(), s

    if not request.path == '/subject/':
        return {
            'sem_list': unique_sem,
        }

    all_sub_1 = []
    results = SubjectModel.objects.all(). \
        values('student__branch', 'student__batch__batch_name', 'subject__subject_name',
               'subject__subject_full_name', 'sem__sem_name').distinct()
    results = list(results)
    all_sub_1 += results

    final_list = dynamic_result_dict(all_sub, 0)
    final_list_1 = dynamic_result_dict(all_sub_1, 0)

    list_1 = [{**item, 'Access': 'False'}
              for item in final_list_1 if item not in final_list]
    list_2 = [{**item, 'Access': 'True'} for item in final_list]

    temp = list_1 + list_2
    temp.sort(key=lambda x: (x['semester'], x['branch']))
    obj_1 = dynamic_result_dict(temp, 1)
    final_obj = dict(sorted(obj_1.items()))

    return {
        'subject_obj': final_obj,
        'sem_list': unique_sem,
    }


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET.get('key'):
            return redirect(request.path)

        paths = request.path.lower()

        try:
            redirect_obj = RedirectModel.objects.get(url=paths, deleted=False)

            if redirect_obj.send_message:
                messages.success(request, redirect_obj.send_message)

            if redirect_obj.redirect_to and redirect_obj.change_redirect:
                return self._render_target(request, redirect_obj.redirect_to)

            elif redirect_obj.redirect_to:
                return redirect(redirect_obj.redirect_to)

            elif redirect_obj.html_page:
                return render(request, redirect_obj.html_page)

            elif redirect_obj.html_code:
                try:
                    # Create a Template object
                    template = Template(redirect_obj.html_code)

                    # Create a Context object with the necessary context variables (e.g., request.session.email)
                    context = Context({'request': request})

                    # Render the template with the context
                    rendered_html = template.render(context)

                    return render(request, "html_page.html", {"html_code": rendered_html})
                except Exception as e:
                    return HttpResponse(redirect_obj.html_code)

            elif redirect_obj.template_name:
                try:
                    try:
                        reason_phrase = self.get_response(
                            request).reason_phrase
                    except Exception as e:
                        reason_phrase = f"Not Found {e}"
                    temp = f"""
                        <h1>
                            Template Name = {reason_phrase}
                        </h1>
                        <br>
                        
                    """
                    try:
                        path = f'{BASEURL}/templates/{reason_phrase}'
                        with open(path, 'r') as f:
                            html = f.read()

                        temp += html
                    except:
                        pass
                    return render(request, "html_page.html", {"html_code": temp},
                                  content_type="text/plain; charset=utf-8")

                except Exception as e:
                    return HttpResponse(redirect_obj.html_code)

            else:
                if not redirect_obj.send_message:
                    return render(request, '404.html', {'key': '307'})
        except:
            pass

        if request.path != '/admin/' and request.path != '/admin/login/':
            return self.get_response(request)

        if StudentDataModel.objects.all().__len__() == 0:
            return self.get_response(request)

        if request.session.get('userid'):
            check = get_user(request, 0)
            if request.user.is_superuser:
                return self.get_response(request)
            else:
                if check:
                    return redirect('/admin_side/')
                else:
                    messages.success(
                        request, 'Denied entry! You took a Wrong Turn.....!')
                    return redirect(f"/{request.session.get('enrollment')}/")
        else:
            messages.success(request, 'First You Need to Login')
            return redirect(f'/login?next={request.path}')

    def _render_target(self, request, target_url):
        from django.urls import resolve

        try:
            resolver_match = resolve(target_url)
            view_func = resolver_match.func
            return view_func(request, *resolver_match.args, **resolver_match.kwargs)
        except Exception as e:
            return render(request, "html_page.html", {"html_code": f"{e}"})
