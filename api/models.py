from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import datetime

# Create your models here.


class User(AbstractUser):
    AN = "anon"
    LG = "user"
    MD = "moderator"
    AD = "admin"
    ROLE_CHOICES = {
        "anon": "Anonymous",
        "user": "User",
        "moderator": "Moderator",
        "admin": "Admin",
    }
    email = models.EmailField(
        _("email address"), blank=False, null=False, unique=True
    )
    confirmation_code = models.IntegerField(blank=False, null=False, default=0)
    role = models.CharField(
        max_length=9, choices=ROLE_CHOICES.items(), default=AN
    )
    bio = models.CharField(max_length=160, null=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True, db_index=True, verbose_name="category_slug"
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True, db_index=True, verbose_name="genre_slug"
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200, blank=False)
    year = models.IntegerField(
        default=datetime.now().year,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(datetime.now().year),
        ],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="titles_of_category",
    )
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, blank=True, related_name="titles_of_genre"
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title_id = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    score = models.IntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)]
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    pub_date = models.DateTimeField(
        verbose_name="date_publication_review",
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review_id = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        verbose_name="date_publication_comment",
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return self.text
