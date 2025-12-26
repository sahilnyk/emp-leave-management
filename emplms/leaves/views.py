from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest, LeaveBalance
from .forms import LeaveForm
from django.contrib import messages
from django.utils import timezone
from datetime import date


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

    # compute days safely
    days = _days_inclusive(leave.start_date, leave.end_date)
    if days <= 0:
        messages.error(request, "Invalid leave dates.")
        return redirect("leaves:pending_requests")

    # mark approved
    comment = request.POST.get("comment", "").strip()
    leave.status = "approved"
    leave.manager = request.user
    if comment:
        leave.manager_comment = comment
    leave.save()

    # Recompute authoritative used counts from approved LeaveRequest records
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

    # Recompute authoritative used counts from approved LeaveRequest records (rollback if needed)
    used = LeaveRequest.user_used_counts(leave.user)
    lb, _ = LeaveBalance.objects.get_or_create(user=leave.user)
    lb.sick_used = used.get('sick', 0)
    lb.casual_used = used.get('casual', 0)
    lb.other_used = used.get('other', 0)
    lb.save()

    messages.success(request, f"Rejected {leave.user.get_full_name() or leave.user.username}.")
    return redirect("leaves:pending_requests")
