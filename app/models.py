from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
            

class Course (BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    # avatar = models.ImageField
    className = models.CharField(max_length=255, unique=False, null=True)    
    courses = models.ManyToManyField(Course, related_name="users")
    # is_superuser = models.BooleanField(default=False, editable=False)
    pass


class Score (BaseModel):
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    midterm_score = models.FloatField()
    final_score = models.FloatField()
    score1 = models.FloatField(null=True, blank=True, default=None)
    score2 = models.FloatField(null=True, blank=True, default=None)
    score3 = models.FloatField(null=True, blank=True, default=None)
    score4 = models.FloatField(null=True, blank=True, default=None)
    score5 = models.FloatField(null=True, blank=True, default=None)

    def __str__(self):
        return 'midterm_score={0}, final_score={1}'.format(self.midterm_score, self.final_score)


class ForumPost (BaseModel):
    title = models.CharField(max_length=255, unique=True)
    body = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.title