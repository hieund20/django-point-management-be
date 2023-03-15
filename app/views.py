from django.http import HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Score, Course, User
from .serializers import ScoreSerializer, CourseSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema
# csv
import csv
from io import TextIOWrapper
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# email
from django.core.mail import send_mail
from django.conf import settings

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
            "is_draft": score['is_draft'],
            "course": course.pk,
            "user": user.pk,
        }
        _serializer = self.serializer_class(data=data)
        if _serializer.is_valid():
            _serializer.save()
            return Response(data=_serializer.data, status=status.HTTP_201_CREATED) 
        else:
            return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    def update(self, request, pk=None):
        score = get_object_or_404(Score, pk=pk)
        score.is_draft = True
        score.save()
        return Response(data=self.serializer_class(score).data, status=status.HTTP_200_OK)
        
    @action(methods=['get'], detail=False)
    def get_score_by_user_and_course(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        course_id = request.query_params.get('course_id')
        s = Score.objects.filter(course=course_id).filter(user=user_id).first()
        return Response(data=ScoreSerializer(s).data, status=status.HTTP_200_OK)
    
    @action(methods=['put'], detail=True)
    def lock_score(self, request, pk=None):
        score = get_object_or_404(Score, pk=pk)
        score.active = False
        score.save(update_fields=['active'])

        # send email to current user
        user = request.user
        subject = f'Thông báo về việc khóa điểm của sinh viên {user.last_name} {user.first_name}'
        message = f'Điểm của bạn đã bị khóa bởi Giảng viên !'
        recipient_list = [user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

        return Response(data=ScoreSerializer(score).data, status=status.HTTP_200_OK)
    
    @action(methods=['put'], detail=True)
    def unlock_score(self, request, pk=None):
        score = get_object_or_404(Score, pk=pk)
        score.active = True
        score.save(update_fields=['active'])

        # send email to current user
        user = request.user
        subject = f'Thông báo về việc mở khóa điểm của sinh viên {user.last_name} {user.first_name}'
        message = f'Điểm của bạn đã được mở khóa bởi Giảng viên, hãy kiểm tra điểm của mình trên hệ thống !'
        recipient_list = [user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

        return Response(data=ScoreSerializer(score).data, status=status.HTTP_200_OK)
    
            
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
    
    @action(methods=['get'], detail=False)
    def get_user_by_name(self, request, *args, **kwargs):
        first_name = request.query_params.get('first_name')
        last_name = request.query_params.get('last_name')
        if not first_name or not last_name:
            return Response({'message': 'Hãy nhập Họ và Tên người dùng'}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CourseViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(methods=['get'], detail=True)
    def get_member(self, request, pk):
        u = User.objects.filter(courses=pk)
        return Response(data=UserSerializer(u, many=True).data, status=status.HTTP_200_OK)
    
@method_decorator(csrf_exempt, name='dispatch')
class CSVHandleView(generics.CreateAPIView):
    parser_classes = (FileUploadParser, MultiPartParser)

    @swagger_auto_schema(operation_description='Upload file...',)
    def post(self, request, *args, **kwargs):
        csv_file = request.data.get('file')

        if not csv_file.name.endswith('.csv'):
            return Response({'message': 'File không phải định dạng CSV'}, status=status.HTTP_400_BAD_REQUEST)    

        # read the CSV file and create instances of your model
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        print('decoded_file 1', decoded_file)
        print('decoded_file', decoded_file[5:])
        reader = csv.DictReader(
            decoded_file[5:], 
            fieldnames=['score1', 'score2', 'score3', 'score4', 'score5', 'midterm_score', 'final_score', 'course_id', 'user_id']
        )
        print('reader', reader)
        next(reader)  # Skip read csv header
        print('reader 2', reader)

        #still have error
        for line in reader:
            try:
                values = list(line.values()) 
                score = Score()
                score.score1 = values[0]  
                score.score2 = values[1] 
                score.score3  = values[2] 
                score.score4 = values[3] 
                score.score5 = values[4]
                score.midterm_score = values[5]
                score.final_score = values[6]
                score.user = User.objects.filter(pk=values[7]).first() 
                score.course = Course.objects.filter(pk=values[8]).first()
                # Save to database
                Score.objects.create(**score)
            except KeyError as e:
                print(f"KeyError: {e}")
                return Response({'message': 'Có lỗi xảy ra khi Import'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Import thành công'}, status=status.HTTP_200_OK)    
    

def index(request):
    return HttpResponse("e-Course App")