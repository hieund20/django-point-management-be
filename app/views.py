from django.http import HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Score, Course, User
from .serializers import ScoreSerializer, CourseSerializer, UserSerializer
from django.shortcuts import get_object_or_404

# Create your views here.
class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.filter(active=True)
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        score = request.data 
        course = get_object_or_404(Course, pk=score['course_id'])
        user = get_object_or_404(User, pk=score['user_id'])
        data = {
            "midterm_score": score['midterm_score'],
            "final_score": score['final_score'],
            "score1": score['score1'],
            "score2": score['score2'],
            "score3": score['score3'],
            "score4": score['score4'],
            "score5": score['score5'],
            "course": course.pk,
            "user": user.pk,
        }
        _serializer = self.serializer_class(data=data)
        if _serializer.is_valid():
            _serializer.save()
            return Response(data=_serializer.data, status=status.HTTP_201_CREATED) 
        else:
            return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    

class UserViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(methods=['get'], detail=True)
    def get_courses(self, request, pk):
        c = Course.objects.filter(users=pk)
        return Response(data=CourseSerializer(c, many=True).data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False)
    def get_scores_of_course(self, request, *args, **kwargs):
        user_id = request.user.id
        course_id = request.query_params.get('course_id')
        s = Score.objects.filter(course=course_id).filter(user=user_id).first()
        return Response(data=ScoreSerializer(s).data, status=status.HTTP_200_OK)
    
    # def get_permissions(self):
    #     if self.action == 'retrieve':
    #         return [permissions.IsAuthenticated()]
        
    #     return [permissions.AllowAny()]

class CourseViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(methods=['get'], detail=True)
    def get_students(self, request, pk):
        u = User.objects.filter(courses=pk)
        return Response(data=UserSerializer(u, many=True).data, status=status.HTTP_200_OK)
    

def index(request):
    return HttpResponse("e-Course App")