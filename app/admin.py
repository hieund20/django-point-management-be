from django.contrib import admin
from .models import User, Course, Score, ForumPost

# Register your models here.
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Score)
admin.site.register(ForumPost)


