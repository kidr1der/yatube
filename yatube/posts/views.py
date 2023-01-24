from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required
from Users.forms import PostForm, CommentForm



def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        'page': page,
        'group': group,
        'paginator': paginator
    })


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date')
    # following = Follow.objects.filter(author=profile, user=request.user)
    following = request.user.is_authenticated \
                and profile.following.filter(user=request.user).exists()
    paginator = Paginator(posts, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением

    return render(request, 'profile.html', {'paginator': paginator, 'page': page, 'profile': profile,
                                            'posts': posts, 'following': following})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date')
    post = get_object_or_404(Post, pk=post_id, author=profile)
    form = CommentForm()
    items = post.comments.all()
    return render(request, 'post.html', {'profile': profile, 'post': post,
                                         'posts': posts, 'form': form, 'items': items})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('post', username=username, post_id=post_id)



@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    title = 'Редактирование поста'
    button = 'Сохранить'
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)

    # добавим в form свойство files
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(request, 'post_edit.html', {'form': form, 'post': post, 'title': title,
                                              'button': button, 'username': username})


@login_required
def new_post(request):
    title = 'Создать пост'
    button = 'Сохранить'
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form, 'title': title, 'button': button})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form, 'title': title, 'button': button})


@login_required
def follow_index(request):
    user_follows = User.objects.get(pk=request.user.id).follower.values_list('author')
    post_list = Post.objects.filter(author__in=user_follows).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "follow.html", {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect("profile", username=username)
    following = get_object_or_404(User, username=username)
    already_follows = Follow.objects.filter(
        user=request.user,
        author=following
    ).exists()
    if not already_follows:
        Follow.objects.create(user=request.user, author=following)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(Follow, user=request.user, author=following)
    follower.delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)