from django.contrib import admin
from .models import User, Category, Genre, Title


# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
