from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest, LeaveBalance
from .forms import LeaveForm
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
import calendar

@login_required
def apply_leave(request):
    if request.method == "POST":
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            messages.success(request, "Leave request submitted successfully")
            return redirect("leaves:my_leaves")
    else:
        form = LeaveForm()
    return render(request, "apply_leave.html", {"form": form})

@login_required
def my_leaves(request):
    leaves = LeaveRequest.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_leave.html", {"leaves": leaves})

@login_required
def pending_requests(request):
    pending = LeaveRequest.objects.filter(status__iexact="pending").order_by("start_date")
    return render(request, "pending_requests.html", {"leaves": pending})

def _days_inclusive(start_date, end_date):
    return (end_date - start_date).days + 1

def _ensure_balance(user):
    lb, created = LeaveBalance.objects.get_or_create(user=user)
    return lb

@login_required
def approve_leave(request, id):
    leave = get_object_or_404(LeaveRequest, id=id)
    if request.method != "POST":
        return redirect("leaves:pending_requests")
    if leave.user == request.user:
        messages.error(request, "You cannot approve your own leave.")
        return redirect("leaves:pending_requests")
    prev_status = leave.status
    if prev_status.lower() == "approved":
        messages.info(request, "This leave is already approved.")
        return redirect("leaves:pending_requests")
    days = _days_inclusive(leave.start_date, leave.end_date)
    if days <= 0:
        messages.error(request, "Invalid leave dates.")
        return redirect("leaves:pending_requests")
    comment = request.POST.get("comment", "").strip()
    leave.status = "approved"
    leave.manager = request.user
    if comment:
        leave.manager_comment = comment
    leave.save()
    used = LeaveRequest.user_used_counts(leave.user)
    lb, _ = LeaveBalance.objects.get_or_create(user=leave.user)
    lb.sick_used = used.get('sick', 0)
    lb.casual_used = used.get('casual', 0)
    lb.other_used = used.get('other', 0)
    lb.save()
    messages.success(request, f"Approved {leave.user.get_full_name() or leave.user.username} ({days} day(s)).")
    return redirect("leaves:pending_requests")

@login_required
def reject_leave(request, id):
    leave = get_object_or_404(LeaveRequest, id=id)
    if request.method != "POST":
        return redirect("leaves:pending_requests")
    if leave.user == request.user:
        messages.error(request, "You cannot reject your own leave.")
        return redirect("leaves:pending_requests")
    prev_status = leave.status
    if prev_status.lower() == "rejected":
        messages.info(request, "This leave is already rejected.")
        return redirect("leaves:pending_requests")
    comment = request.POST.get("comment", "").strip()
    leave.status = "rejected"
    leave.manager = request.user
    leave.manager_comment = comment
    leave.save()
    used = LeaveRequest.user_used_counts(leave.user)
    lb, _ = LeaveBalance.objects.get_or_create(user=leave.user)
    lb.sick_used = used.get('sick', 0)
    lb.casual_used = used.get('casual', 0)
    lb.other_used = used.get('other', 0)
    lb.save()
    messages.success(request, f"Rejected {leave.user.get_full_name() or leave.user.username}.")
    return redirect("leaves:pending_requests")

@login_required
def leave_calendar(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    approved_leaves = LeaveRequest.objects.filter(
        status__iexact='approved',
        start_date__lte=last_day,
        end_date__gte=first_day
    ).select_related('user')
    
    leave_map = {}
    for leave in approved_leaves:
        current = max(leave.start_date, first_day)
        end = min(leave.end_date, last_day)
        while current <= end:
            if current not in leave_map:
                leave_map[current] = []
            leave_map[current].append({
                'user': leave.user.get_full_name() or leave.user.username,
                'type': leave.get_leave_type_display()
            })
            current += timedelta(days=1)
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render(request, 'leave_calendar.html', {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': month_name,
        'leave_map': leave_map,
        'today': today,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    })