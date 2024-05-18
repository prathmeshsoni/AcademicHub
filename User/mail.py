import os
import smtplib
import subprocess
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(email, first_name, username, site_url, password, check, names=None):
    base_path_server = f'{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))}//'

    to_email = settings.EMAIL_HOST_USER
    to_password = settings.EMAIL_HOST_PASSWORD

    if not names:
        names = 'Username is not set'

    path = f'{base_path_server}templates/mail/mail.html'
    if check == 'forgot':
        path = f'{base_path_server}templates/mail/forgot.html'

    elif check == 'change_password':
        path = f'{base_path_server}templates/mail/change.html'

    elif check == 'special' or check == 'special_1':
        path = f'{base_path_server}templates/mail/special.html'

    elif check == 'reminder':
        path = f'{base_path_server}templates/mail/reminder.html'

    with open(path, 'r') as f:
        html = f.read()

    html = html. \
        replace('{firstname_val}', f'<b>{first_name}</b>'). \
        replace('{username_val}', username). \
        replace('{email_val}', email). \
        replace('{password_val}', password). \
        replace('{siteurl_val}', site_url). \
        replace('{name_val_main}', names)

    if check == 'special':
        html = html. \
            replace('{s_msg}', 'Thank You For Registration !') \
            .replace('{hi_mssg_1}', 'Beautifully Misbehaving, Your Presence adds a Touch of Magic, '). \
            replace('{hi_msg}', 'Welcome, ')
    elif check == 'special_1':
        html = html. \
            replace('{s_msg}', 'Password now changed for some Security Reasons!'). \
            replace('{hi_mssg_1}', ','). \
            replace('{hi_msg}', 'Heyy')

    msg = MIMEMultipart('alternative')
    if check == 'change_password':
        msg['Subject'] = f'Password Changed - CSE-AIML'
    if check == 'forgot':
        msg['Subject'] = f'Forgot Password - CSE-AIML'
    elif check == 'special_1':
        msg['Subject'] = f'Password alert - CSE-AIML'
    else:
        msg['Subject'] = f'Welcome To CSE-AIML'

    msg['Message-ID'] = 'Welcome'
    msg['From'] = f'Support Team'
    msg['To'] = email

    part2 = MIMEText(html, 'html')
    msg.attach(part2)

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(f'{to_email}', f'{to_password}')
    mail.sendmail(f'{to_email}', email, msg.as_string())
    mail.quit()


def server_start():
    from_email = 'sendmail.testingphase@gmail.com'
    to_email = 'info@cse-aiml.live'

    message = f"""The Django Server Has Started From AcademicHub : 
    \n Username :{get_git_username()}, 
    \n{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}!"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Server Start!'
    msg['Message-ID'] = 'Welcome'
    msg['From'] = 'message'
    msg['To'] = f"{to_email}"
    msg.attach(MIMEText(message, 'plain'))

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(f"{from_email}", 'vsgwgbcgungdzbcp')
    mail.sendmail(f"{from_email}", f"{to_email}", msg.as_string())
    mail.quit()


def get_git_username():
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'user.name'],
            capture_output=True,
            text=True,
            check=True
        )
        git_username = result.stdout.strip()
        return git_username
    except:
        return ''
