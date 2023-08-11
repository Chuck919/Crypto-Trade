from django.urls import path
from . import views

app_name = 'tradebots'
urlpatterns = [
    path('bots/', views.bots, name='bots'),
    path('martingale/', views.martingale, name='martingale'),
    path('smart/', views.smart, name='smart'),
    path('grid/', views.grid, name='grid'),
    path('success/', views.success, name='success'),
]