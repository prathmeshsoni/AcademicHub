from django import forms

from User.models import *


class PdfDetails_Form(forms.ModelForm):
    class Meta:
        model = PdfDetailsModel
        fields = '__all__'


class RedirectModelForm(forms.ModelForm):
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'placeholder': '/example/'}),
        required=True
    )

    send_message = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'placeholder': 'Welcome Message'}),
        required=False
    )

    redirect_to = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'placeholder': '/demo/ or https://example.com'}),
        required=False
    )

    html_page = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'placeholder': 'index.html'}),
        required=False
    )

    class Meta:
        model = RedirectModel
        fields = '__all__'
        widgets = {
            'html_code': forms.Textarea(attrs={'class': 'vLargeTextField', 'placeholder': '<h1> Hello World! </h1>'}),
            'template_name': forms.CheckboxInput(attrs={}),
            'deleted': forms.CheckboxInput(attrs={}),
        }
