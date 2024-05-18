from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

admin.site.unregister(Group)

admin.site.site_header = mark_safe("<h1> AcademicHub Administration 🚀 </h1>")
admin.site.index_title = "Welcome to AcademicHub Admin Portal 🕵️"
