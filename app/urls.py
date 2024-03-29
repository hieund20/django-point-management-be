from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('score', views.ScoreViewSet, basename='score')
router.register('course', views.CourseViewSet, basename='course')
router.register('user', views.UserViewSet, basename='user')
router.register('forumPost', views.ForumPostViewSet, basename='forumPost')
router.register('forumPostAnswer', views.ForumPostAnswerViewSet, basename='forumPostAnswer')

urlpatterns = [
    path('', include(router.urls)),
    path('csv-handle/score/', views.CSVHandleView.as_view(), name='csv_handle'),
    path('pdf-handle/score/', views.PDFHandleView.as_view(), name='pdf_handle'),
]
