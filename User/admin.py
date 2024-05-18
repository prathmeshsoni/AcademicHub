from django.contrib import admin

from User.forms import RedirectModelForm
from User.models import *

admin.site.register(SendMailModel)
admin.site.register(DevelopedByModel)
admin.site.register(DevelopedGalleryModel)

admin.site.register(Profile)
admin.site.register(AccessModel)

admin.site.register(ActualRollNoModel)

admin.site.register(StudentDataModel)
admin.site.register(FacultyDataModel)

admin.site.register(YearBatchModel)
admin.site.register(BranchNameModel)
admin.site.register(SemModel)
admin.site.register(SubjectNameModel)
admin.site.register(MscNameModel)
admin.site.register(SubjectModel)

admin.site.register(PdfDetailsModel)

admin.site.register(ContactModel)

admin.site.register(ConfessionModel)
admin.site.register(ConfessionCommentModel)
admin.site.register(ConfessionLikeModel)


class RedirectModelFormAdmin(admin.ModelAdmin):
    form = RedirectModelForm


admin.site.register(RedirectModel, RedirectModelFormAdmin)
