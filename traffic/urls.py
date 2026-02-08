from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('simulate/', views.simulate, name='simulate'),
    path('predict/', views.predict, name='predict'),
]
