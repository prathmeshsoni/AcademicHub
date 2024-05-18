from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models

from django.db.models.signals import post_migrate
from django.dispatch import receiver

User = get_user_model()


class RedirectModel(models.Model):
    url = models.CharField(max_length=500, default='')
    send_message = models.CharField(max_length=500, null=True, blank=True, default='')
    redirect_to = models.CharField(max_length=500, null=True, blank=True, default='')
    html_page = models.CharField(max_length=500, null=True, blank=True, default='')
    html_code = models.TextField(max_length=500000, null=True, blank=True, default='')
    change_redirect = models.BooleanField(default=False, null=True, blank=True)
    template_name = models.BooleanField(default=False, null=True, blank=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        if self.redirect_to and self.change_redirect:
            text = f'{self.url} => {self.redirect_to} <= {self.url}'
        elif self.redirect_to:
            text = f'{self.url} => {self.redirect_to}'
        elif self.html_page:
            text = f'{self.url} => {self.html_page}'
        elif self.template_name:
            text = f'{self.url} | Get Templete Name'
        else:
            text = f'{self.url} => Dynamic Code'

        if self.deleted:
            text += " || NOT ACTIVE"

        return str(f'{text}')


class DevelopedByModel(models.Model):
    name = models.TextField(max_length=100)
    short_name = models.TextField(max_length=100)
    email = models.TextField(max_length=100)
    linkedin = models.TextField(max_length=100)
    instagram = models.TextField(max_length=100)
    image = models.ImageField(upload_to='developer/', blank=True, null=True)
    image_link = models.CharField(max_length=1000, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f'{self.name}'


class DevelopedGalleryModel(models.Model):
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    style = models.CharField(max_length=1000, default='')
    is_deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f'{self.image}'


class FacultyDataModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    contact = models.BigIntegerField(blank=True, null=True)
    image_link = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to='faculty/', blank=True, null=True)
    faculty_type = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f'{self.name}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="profile")
    name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    password = models.CharField(max_length=100, null=True)
    branch = models.CharField(max_length=100, null=True, default='aiml')
    user_type = models.CharField(max_length=100, null=True, default='student')
    image_link = models.CharField(max_length=1000, blank=True, null=True)
    auth_token = models.CharField(max_length=100, null=True)
    is_verified = models.BooleanField(default=False, null=True)
    is_delete = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        names = " ".join(f"{self.name}".split(' ')[0:2])
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        if not self.is_verified:
            return f'{time} | {names} - {self.email} - {self.username} - {self.is_verified} {self.user}'
        else:
            return f'{time} | {names} - {self.email} - {self.username} {self.user}'


class AccessModel(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    access = models.CharField(max_length=100, null=True, default='no')

    def __str__(self):
        return f'{self.user.name} - {self.user.email} - {self.user.username} '  # {self.access}


class SubjectNameModel(models.Model):
    subject_name = models.CharField(max_length=100, default='')
    subject_full_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return str(f'{self.subject_name} - {self.subject_full_name}')


class MscNameModel(models.Model):
    msc_name = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.msc_name)


class BranchNameModel(models.Model):
    branch_name = models.TextField(max_length=50, default='')

    def __str__(self):
        return str(self.branch_name)


class SemModel(models.Model):
    sem_name = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.sem_name)


class YearBatchModel(models.Model):
    batch_name = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.batch_name)


class StudentDataModel(models.Model):
    enrollment_number = models.BigIntegerField()
    name = models.TextField(max_length=50)
    branch = models.TextField(max_length=50)
    batch = models.ForeignKey(YearBatchModel, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.BigIntegerField(default=0)

    division = models.TextField(max_length=100)
    roll_no = models.BigIntegerField(default=0)
    total_mark = models.BigIntegerField()

    def __str__(self):
        return str(f'{self.enrollment_number} {self.name} {self.batch}')

    @property
    def total_mark_divided_by_4(self):
        return self.total_mark / 4


class ActualRollNoModel(models.Model):
    roll_no = models.BigIntegerField(default=0)
    division = models.CharField(max_length=100, default='')
    sem = models.ForeignKey(SemModel, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(StudentDataModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(f'{self.sem} | {self.roll_no} - {self.division}')


class SubjectModel(models.Model):
    student = models.ForeignKey(StudentDataModel, on_delete=models.CASCADE, default='')
    section_A = models.BigIntegerField(default=0)
    section_B = models.BigIntegerField(default=0)
    msc = models.ForeignKey(MscNameModel, on_delete=models.CASCADE, default='')
    sem = models.ForeignKey(SemModel, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(SubjectNameModel, on_delete=models.CASCADE, default='')

    def save(self, *args, **kwargs):
        if not self.sem:
            try:
                sem_obj = SemModel.objects.get(sem_name=self.semester)
            except SemModel.DoesNotExist:
                sem_obj = SemModel.objects.create(sem_name=self.semester)
                sem_obj.save()
            self.sem = sem_obj

        super().save(*args, **kwargs)

    @property
    def total_mark_(self):
        return self.section_A + self.section_B

    def __str__(self):
        return str(f'{self.student.enrollment_number} {self.subject} {self.msc}')


class PdfDetailsModel(models.Model):
    pdf_file = models.FileField(upload_to='pdf/', blank=True, null=True)

    def __str__(self):
        return str(self.pdf_file)


class ContactModel(models.Model):
    name = models.TextField(max_length=100)
    email = models.TextField(max_length=100)
    msg = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        return f'{time} |  {self.name} {self.email}'


class ConfessionModel(models.Model):
    msg = models.TextField(max_length=1000)
    status = models.BooleanField(default=False, null=True, blank=True)
    likes = models.BigIntegerField(default=0, null=True, blank=True)
    comments = models.BigIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        return f'{time} | {self.msg}'


class ConfessionCommentModel(models.Model):
    msg = models.TextField(max_length=1000)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, default='', null=True, blank=True,
                                related_name='student_confession_comment')
    confession = models.ForeignKey(ConfessionModel, on_delete=models.CASCADE, default='', null=True, blank=True,
                                   related_name='confession_comment')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        return f'{time} | {self.msg} | {self.confession.id}'


class ConfessionLikeModel(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, default='', null=True, blank=True,
                                related_name='student_confession_like')
    confession = models.ForeignKey(ConfessionModel, on_delete=models.CASCADE, default='', null=True, blank=True,
                                   related_name='confession_like')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deleted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        time = (self.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%b/%y %I:%M %p")
        return f'{time} | {self.deleted} | {self.confession.id}'


class SendMailModel(models.Model):
    server_start = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f'{self.server_start}'
