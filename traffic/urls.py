from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.index, name='index'),
    path('predict/', views.predict, name='predict'),
    path('simulate/', views.simulate, name='simulate'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('api/add-favorite/', views.add_favorite, name='add_favorite'),
    path('api/user-data/', views.get_user_data, name='get_user_data'),
    path('api/predict-trend/', views.predict_trend, name='predict_trend'),
    path('api/delete-favorite/<int:fav_id>/', views.delete_favorite, name='delete_favorite'),
    # Pasword Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='traffic/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='traffic/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='traffic/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='traffic/password_reset_complete.html'), name='password_reset_complete'),
]
