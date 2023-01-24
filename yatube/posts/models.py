from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    rules = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="posts", blank=True, null=True
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Comment(models.Model):
    text = models.TextField(max_length=300, help_text="Текст коммента")
    created = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", help_text="Автор коммента")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", help_text="Добавь коммент",
                             blank=True, null=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'user: {self.user.username} author: {self.author.username}'
