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
    path('profile/update/', views.update_profile, name='update_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),  # Follow URL
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),  # Unfollow URL
    path('feed/', views.feed, name='feed'),  # Feed URL
    path('notifications/', views.notifications, name='notifications'),
    path('search/', views.search, name='search'),  # Search URL
    path('explore/', views.explore, name='explore'),
    path('stories/', views.stories_view, name='stories'),
    path('messages/', views.messages_view, name='messages'),  # Messages URL
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),  # Post detail URL
    path('save/<int:post_id>/', views.save_post, name='save_post'),  # Save post URL
]