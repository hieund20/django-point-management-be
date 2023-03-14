from django.http import HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Score, Course, User
from .serializers import ScoreSerializer, CourseSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema
#csv
import csv
from io import TextIOWrapper


# Create your views here.
class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.filter(active=True)
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FileUploadParser]
    
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
        
    @action(methods=['get'], detail=False)
    def get_score_by_user_and_course(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        course_id = request.query_params.get('course_id')
        s = Score.objects.filter(course=course_id).filter(user=user_id).first()
        return Response(data=ScoreSerializer(s).data, status=status.HTTP_200_OK)
            
class UserViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView, generics.CreateAPIView):
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
    
    @action(methods=['get'], detail=False)
    def get_current_user(self, request, *args, **kwargs):
        user_id = request.user.id
        u = User.objects.filter(id=user_id).first()
        return Response(data=UserSerializer(u).data, status=status.HTTP_200_OK)

class CourseViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(methods=['get'], detail=True)
    def get_member(self, request, pk):
        u = User.objects.filter(courses=pk)
        return Response(data=UserSerializer(u, many=True).data, status=status.HTTP_200_OK)
    
class CSVHandleView(generics.CreateAPIView):
    parser_classes = (FileUploadParser, MultiPartParser)

    @swagger_auto_schema(operation_description='Upload file...',)
    def post(self, request, *args, **kwargs):
        if 'file' in request.FILES:
            # Handling csv file before save to database
            form_data = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
            csv_file = csv.reader(form_data)
            next(csv_file)  # Skip read csv header

            scores_list = []

            for line in csv_file:
                score = Score()
                score.score1 = line[0] if line[0] != None else None
                score.score2 = line[1] if line[1] != None else None
                score.score3  = line[2] if line[2] != None else None
                score.score4 = line[3] if line[3] != None else None
                score.score5 = line[4] if line[4] != None else None
                score.midterm_score = line[5]
                score.final_score = line[6]
                score.user = line[7]
                score.course = line[8]
                scores_list.append(score)

            # Save to database
            Score.objects.bulk_create(scores_list)
            return Response({'message': 'Import thành công'}, status=status.HTTP_200_OK)    
    

def index(request):
    return HttpResponse("e-Course App")