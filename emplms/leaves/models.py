from django.db import models
from django.contrib.auth.models import User
from datetime import date


class LeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_balance = models.IntegerField(default=18)
    sick_used = models.IntegerField(default=0)
    casual_used = models.IntegerField(default=0)
    other_used = models.IntegerField(default=0)

    def remaining(self):
        return self.total_balance - (self.sick_used + self.casual_used + self.other_used)

    def __str__(self):
        return f"{self.user.username} Balance"


class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('other', 'Other Leave'),
    )

    STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES)

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    manager = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_leaves",
        help_text="Manager who approved/rejected this leave"
    )
    manager_comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type}"
    def days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @classmethod
    def user_used_counts(cls, user):
        approved = cls.objects.filter(user=user, status__iexact='approved')
        totals = {'sick': 0, 'casual': 0, 'other': 0}
        for lr in approved:
            d = lr.days()
            if lr.leave_type in totals:
                totals[lr.leave_type] += max(0, d)
        return totals
