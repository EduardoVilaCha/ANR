# A model is the single, definitive source of information about your data.
# It contains the essential fields and behaviors of the data you’re storing.
# Generally, each model maps to a single database table.

# from tinymce.models import HTMLField
from tinymce.models import HTMLField
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils.text import slugify

User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey("Post", related_name="comments", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = RichTextField(blank=True, null=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    # slug field !!!maybe change

    # comment_count = models.IntegerField(default = 0)
    # view_count = models.IntegerField(default = 0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    categories = models.ManyToManyField(Category)
    featured = models.BooleanField()
    previous_post = models.ForeignKey(
        "self",
        related_name="previous",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    next_post = models.ForeignKey(
        "self", related_name="next", on_delete=models.SET_NULL, blank=True, null=True
    )

    _metadata = {
        "title": "name",
        "description": "abstract",
        "image": "get_meta_image",
    }

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"id": self.id, "slug": self.slug})

    def get_update_url(self):
        return reverse("post-update", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("post-delete", kwargs={"id": self.id})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def get_comments(self):
        return self.comments.all().order_by("-timestamp")

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()

    @property
    def convert_in_meta(self):
        title = (self.title)[0:50]
        overview = (self.overview)[0:100]
        description = title + str(overview)
        return description
