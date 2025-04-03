# filepath: c:\OneDrive\Desktop\insta_clone\users\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Import the User model
from django.contrib.auth import logout
from django.contrib import messages
from .models import Post
from .forms import PostForm
from django.http import JsonResponse
from .models import Like
from .models import Comment
from .models import Profile, Post, Follower,Notification


def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})

@login_required
def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user_profile).order_by('-created_at')
    is_following = Follower.objects.filter(follower=request.user.profile, following=user_profile.profile).exists()
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'posts': posts,
        'is_following': is_following,  # Pass this to the template
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    profile_to_follow = user_to_follow.profile
    follower_profile = request.user.profile

    if not Follower.objects.filter(follower=follower_profile, following=profile_to_follow).exists():
        Follower.objects.create(follower=follower_profile, following=profile_to_follow)
        # Create a notification for the followed user
        Notification.objects.create(
            sender=request.user,
            receiver=user_to_follow,
            notification_type='follow'
        )

    return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    profile_to_unfollow = user_to_unfollow.profile
    follower_profile = request.user.profile

    # Remove the relationship if it exists
    Follower.objects.filter(follower=follower_profile, following=profile_to_unfollow).delete()

    return redirect('profile', username=username)

@login_required
def feed(request):
    # Get the profiles the logged-in user is following
    following_profiles = Follower.objects.filter(follower=request.user.profile).values_list('following', flat=True)
    
    # Get posts from users whose profiles are in the following list
    posts = Post.objects.filter(user__profile__id__in=following_profiles).order_by('-created_at')
    
    return render(request, 'feed.html', {'posts': posts})

@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        content = request.POST.get('content')
        Comment.objects.create(user=request.user, post=post, content=content)
        # Create a notification for the post owner
        if post.user != request.user:
            Notification.objects.create(
                sender=request.user,
                receiver=post.user,
                notification_type='comment',
                post=post
            )
        return redirect('home')

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Unlike if the user already liked the post
        liked = False
    else:
        liked = True
        # Create a notification for the post owner
        if post.user != request.user:
            Notification.objects.create(
                sender=request.user,
                receiver=post.user,
                notification_type='like',
                post=post
            )
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  # Associate the post with the logged-in user
            post.save()
            return redirect('home')  # Redirect to the home page after creating the post
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def notifications(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return render(request, 'logout.html')