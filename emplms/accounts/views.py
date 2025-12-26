from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegisterForm, LoginForm
from django.db import transaction

def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                password = form.cleaned_data['password']
                role = form.cleaned_data['role']
                user.set_password(password)
                user.save()
                Profile.objects.filter(user=user).delete()
                Profile.objects.create(
                    user=user,
                    role=role
                )

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
    profile = Profile.objects.filter(user=request.user).first()

    if profile and profile.role == 'manager':
        from leaves.models import LeaveRequest, LeaveBalance
        pending_qs = LeaveRequest.objects.filter(status__iexact='pending').exclude(user=request.user).order_by("start_date")
        total_employees = User.objects.filter(is_active=True).count()
        approved_count = LeaveRequest.objects.filter(status__iexact='approved').count()
        pending_count = pending_qs.count()

        employees = []
        users_qs = User.objects.filter(is_active=True).order_by("first_name", "last_name", "username")
        for u in users_qs:
            prof = Profile.objects.filter(user=u).first()
            role = prof.role if prof else "employee"
            lb, _ = LeaveBalance.objects.get_or_create(user=u)
            remaining = lb.remaining()
            employees.append({
                "user": u,
                "role": role,
                "balance": lb,
                "remaining": remaining,
            })

        return render(request, 'manager_dashboard.html', {
            "pending_leaves": pending_qs,
            "total_employees": total_employees,
            "pending": pending_count,
            "approved": approved_count,
            "employees": employees,
        })

    from dashboard.views import employee_dashboard
    return employee_dashboard(request)
