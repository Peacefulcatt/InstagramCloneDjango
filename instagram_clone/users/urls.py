from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('create_post/', views.create_post, name='create_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),  # Like URL
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),  # Comment URL
    path('profile/<str:username>/', views.profile, name='profile'),  # Profile URL
    path('follow/<str:username>/', views.follow_user, name='follow_user'),  # Follow URL
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),  # Unfollow URL
    path('feed/', views.feed, name='feed'),  # Feed URL
    path('notifications/', views.notifications, name='notifications'),
]