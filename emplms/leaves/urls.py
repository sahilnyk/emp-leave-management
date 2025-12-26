from django.urls import path
from . import views

app_name = "leaves"

urlpatterns = [
    path('apply/', views.apply_leave, name="apply_leave"),
    path('my/', views.my_leaves, name="my_leaves"),
    path('pending/', views.pending_requests, name="pending_requests"),
    path('approve/<int:id>/', views.approve_leave, name="approve_leave"),
    path('reject/<int:id>/', views.reject_leave, name="reject_leave"),
    path('calendar/', views.leave_calendar, name="leave_calendar"),
]
