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
from .models import Profile, Post, Follower, Notification
from .forms import ProfileUpdateForm  # Import the ProfileUpdateForm
from django.db.models import Q
import random
from django.utils import timezone
from .models import Story, Message  # Import the Message model
from .models import SavedPost  # Import the SavedPost model


@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    suggested_users = User.objects.exclude(id=request.user.id).exclude(
        id__in=request.user.profile.following_set.values_list('following__user__id', flat=True)
    )[:5]
    return render(request, 'home.html', {'posts': posts, 'suggested_users': suggested_users})

@login_required
def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user_profile).order_by('-created_at')
    # Ensure is_following is calculated correctly
    is_following = Follower.objects.filter(
        follower=request.user.profile, 
        following=user_profile.profile
    ).exists()
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
    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'home'))

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

@login_required
def update_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'update_profile.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('profile', username=user.username)  # Redirect to the profile page
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return render(request, 'logout.html')

@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(username__icontains=query) if query else []
    posts = Post.objects.filter(
        Q(caption__icontains=query) | Q(user__username__icontains(query))
    ) if query else []
    suggested_posts = Post.objects.all().order_by('-created_at')[:6] if not query else []
    return render(request, 'search.html', {
        'query': query,
        'users': users,
        'posts': posts,
        'suggested_posts': suggested_posts,
    })

@login_required
def messages_view(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        receiver = get_object_or_404(User, username=receiver_username)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        messages.success(request, 'Message sent successfully!')
        return redirect('messages')

    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')
    return render(request, 'messages.html', {'conversations': conversations})

@login_required
def explore(request):
    posts = list(Post.objects.all())
    random.shuffle(posts)
    return render(request, 'explore.html', {'posts': posts[:12]})

@login_required
def stories_view(request):
    active_stories = Story.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=1)
    ).order_by('-created_at')
    return render(request, 'stories.html', {'active_stories': active_stories})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_saved = post.saved_by.filter(user=request.user).exists()  # Check if the post is saved
    return render(request, 'post_detail.html', {'post': post, 'is_saved': is_saved})

def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    saved_post, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved_post.delete()  # Unsave if already saved
    return redirect('post_detail', post_id=post_id)
