from leaves.models import LeaveBalance, LeaveRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def employee_dashboard(request):
    balance = LeaveBalance.objects.get(user=request.user)

    recent_leaves = LeaveRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')[:6]

    total_used = balance.sick_used + balance.casual_used + balance.other_used
    remaining = balance.total_balance - total_used

    return render(request, "employee_dashboard.html", {
        "balance": balance,
        "leaves": recent_leaves,
        "total_used": total_used,
        "remaining": remaining
    })
