from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegisterForm, LoginForm

def register_view(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            user.set_password(password)
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            login(request, user)
            return redirect('dashboard')

        return render(request,'register.html',{"form":form,"form_errors":"Invalid input"})

    return render(request,'register.html',{'form':form})


def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request,user)
                return redirect('dashboard')

            return render(request,'login.html',{"form":form,"form_errors":"Invalid credentials"})

    return render(request,'login.html',{'form':form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.role == 'employee':
        return render(request,'employee_dashboard.html')

    if profile.role == 'manager':
        return render(request,'manager_dashboard.html')

    return render(request,'employee_dashboard.html')
