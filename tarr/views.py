from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from sedc import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail.message import EmailMessage
from django.contrib.auth.decorators import login_required

from .camara import *
from django.http import StreamingHttpResponse
from django.views.decorators import gzip


# Create your views here.

def home(request):
    return render(request, 'home.html')

def signin(request):
    if request.method =="POST":
       # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username = username):
            messages.error(request, "nombre de usuario existente ")
            return redirect ('signin')
            
        if User.objects.filter(email=email):
            messages.error(request, "email registrado")
            return redirect ('signin')
        
        if len(username)>10:
            messages.error(request, "max 10 caracteres")
            
        if pass1 != pass2:
            messages.error(request, "contraseña incorrecta")
            
        if not username.isalnum():
            messages.error(request, "usa letras y numeros")
            return redirect('signin')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        
        messages.success(request, "tu cuenta fue creada correctamente")
        
        #email
        subject = "bienvenido aqui"
        message = "hola"+ myuser.first_name + "!!\n" + "gracias por visitar,confirma tu correo en gmail para activar tu cuenta"
        from_email = settings.EMAIL_HOST_USER
        to_list = {myuser.email}
        send_mail(subject, message, from_email, to_list,fail_silently= True)
        
        #email confimacion
        
        current_site = get_current_site(request)
        email_subject = "confirma tu gmail"
        message2 = render_to_string('email_confitmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('login')
        
    return render(request, 'signin.html')

#@login_required
def info(request):
    return render(request, 'info.html')

@login_required
def signout(request):
    logout(request)
    messages.success(request, "saliste exitosamente")
    return redirect('home')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'info',{'fname': fname})
        else:
            messages.error(request, "Error")
            return redirect('info')
        
    return render(request, 'cam.html')
     
#@login_required
def cam(request):
    return render(request, 'cam.html')

def activate(request,uidb64, token):
    try:
        uid= force_str(urlsafe_base64_encode(uidb64))
        myuser= User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active= True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'actvation_failed.html')
    
@gzip.gzip_page
def livefe(request):
    try:
         cam = VideoCamera()
         return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad!
        pass


def index(request, *args, **kwargs):
    return render(request, 'cam.html')