from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.login_view, name='login'),
    path('register/', account_views.register_view, name='register'),
    path('logout/', account_views.logout_view, name='logout'),
    path('accounts/login/', account_views.login_view),
    path('dashboard/', account_views.dashboard, name='dashboard'),
    path('leaves/', include(('leaves.urls', 'leaves'), namespace='leaves')),
]
