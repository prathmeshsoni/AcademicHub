from django.shortcuts import render

from User.views import logger_send
from .models import SubCategoryModel, SubCategoryTextModel


def index(request, path):
    path = request.path.replace('/c/', '')
    logger_send(request)

    try:
        subcat = SubCategoryModel.objects.get(link=f"/{path}")
        sub_category = SubCategoryTextModel.objects.filter(sub=subcat, deleted=False)

        items = {
            'sid': f'{subcat.category.sid}',
            'vname': f'{subcat.vname.lower()}',
            'home_': f'{subcat.home.lower()}',
            'subcat': subcat,
            'sub_category': sub_category
        }
        return render(request, 'category-view.html', items)
    except Exception as e:
        logger_send(request, f"Category Not Found: {request.path}")
        return render(request, '404.html', {'key': 404})
