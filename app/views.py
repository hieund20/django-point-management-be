from django.http import HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Score, Course, User, ForumPost, ForumPostAnswer
from .serializers import ScoreSerializer, CourseSerializer, UserSerializer, ForumPostSerializer, ForumPostAnswerSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FileUploadParser
from drf_yasg.utils import swagger_auto_schema
# csv
import csv
from io import TextIOWrapper, BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from time import strftime
# pdf
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
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
        user_id = request.query_params.get('user_send_email_id')
        user = get_object_or_404(User, pk=user_id)
        subject = f'Thông báo về việc khóa điểm của sinh viên {user.last_name} {user.first_name}'
        message = f'Điểm của bạn đã bị khóa bởi Giảng viên ! Vui lòng kiểm tra điểm trên hệ thống'
        recipient_list = [user.email]
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

        return Response(data=ScoreSerializer(score).data, status=status.HTTP_200_OK)
    
    @action(methods=['put'], detail=True)
    def unlock_score(self, request, pk=None):
        score = get_object_or_404(Score, pk=pk)
        score.active = True
        score.save(update_fields=['active'])

        # send email to current user
        user_id = request.query_params.get('user_send_email_id')
        user = get_object_or_404(User, pk=user_id)
        subject = f'Thông báo về việc mở khóa điểm của sinh viên {user.last_name} {user.first_name}'
        message = f'Điểm của bạn đã được mở khóa bởi Giảng viên, Vui lòng kiểm tra điểm của mình trên hệ thống !'
        recipient_list = [user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

        return Response(data=ScoreSerializer(score).data, status=status.HTTP_200_OK)
    
            
class UserViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
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
        return Response(data=UserSerializer(u, context={'request': request}).data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False)
    def get_user_by_name(self, request, *args, **kwargs):
        first_name = request.query_params.get('first_name')
        last_name = request.query_params.get('last_name')
        course_id = request.query_params.get('course_id')

        if not course_id:
            return Response({'message': 'Thiếu ID khóa học'}, status=status.HTTP_400_BAD_REQUEST)
        if not first_name:
            first_name = ""
        if not last_name:
            last_name = ""

        class CustomPagination(PageNumberPagination):
            page_size = 5

        users = User.objects.filter(courses=course_id).filter(first_name__icontains=first_name, last_name__icontains=last_name)    
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        new_user = User.objects.create(
            first_name=data["first_name"], 
            last_name=data["last_name"],
            email=data["email"],
            username=data["username"],
            password=data["password"],
            avatar=data["avatar"])
        new_user.set_password(data['password'])
        new_user.save()
        
        course_list = data.getlist('courses')
        for course_id in course_list:
            course_obj = Course.objects.get(pk=course_id)
            new_user.courses.add(course_obj)

        serializer = UserSerializer(new_user) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        url = request.path
        id_str = url.split('/')[-2] # Get the second-to-last element of the URL
        id = int(id_str)

        data = request.data
        update_user = User.objects.get(pk=id)
        update_user.avatar = data["avatar"]
        
        course_list = data.getlist('courses')
        for course_id in course_list:
            course_obj = Course.objects.get(pk=course_id)
            update_user.courses.add(course_obj)

        update_user.save()
        serializer = UserSerializer(update_user) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CourseViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    def filter_queryset(self, queryset):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(users__id=user_id)

        return queryset
    
    @action(methods=['get'], detail=True)
    def get_member(self, request, pk):
        u = User.objects.filter(courses=pk)

        class CustomPagination(PageNumberPagination):
            page_size = 5
        
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(u, request)
        serializer = UserSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class ForumPostViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = ForumPost.objects.filter(active=True)
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(methods=['get'], detail=False)
    def get_forum_post_by_course_id(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id')
        forum = ForumPost.objects.filter(course=course_id)
        
        return Response(data=ForumPostSerializer(forum, many=True).data, status=status.HTTP_200_OK)


class ForumPostAnswerViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = ForumPostAnswer.objects.filter(active=True)
    serializer_class = ForumPostAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(methods=['get'], detail=False)
    def get_forum_post_answer_by_forum_post_id(self, request, *args, **kwargs):
        forum_post_id = request.query_params.get('forum_post_id')
        forum = ForumPostAnswer.objects.filter(forum_post=forum_post_id)
        
        return Response(data=ForumPostAnswerSerializer(forum, many=True).data, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CSVHandleView(generics.CreateAPIView, generics.RetrieveAPIView):
    parser_classes = (FileUploadParser, MultiPartParser)
    serializer_class = ScoreSerializer

    @swagger_auto_schema(operation_description='Import score list from csv file',)
    def post(self, request, *args, **kwargs):
        csv_file = request.data.get('file')
        course_id = request.query_params.get('course_id')

        if not csv_file.name.endswith('.csv'):
            return Response({'message': 'File không phải định dạng CSV'}, status=status.HTTP_400_BAD_REQUEST)    

        # read the CSV file and create instances of your model
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        # remove 5 first item in list
        decoded_file_final = decoded_file[5:]
        # remove 2 last item in list
        decoded_file_final = decoded_file_final[:2]
        reader = csv.DictReader(
            decoded_file_final, 
            fieldnames=['score1', 'score2', 'score3', 'score4', 'score5', 'midterm_score', 'final_score', 'course_id', 'user_id']
        )
        # next(reader)  # Skip read csv header
        list_score = []

        for line in reader:
            try:
                values = list(line.values()) 
                score = Score()
                score.score1 = values[0] if values[0].isdigit() else None
                score.score2 = values[1] if values[1].isdigit() else None
                score.score3  = values[2] if values[2].isdigit() else None
                score.score4 = values[3] if values[3].isdigit() else None
                score.score5 = values[4] if values[4].isdigit() else None

                if values[5].isdigit():
                    score.midterm_score = values[5] 
                else:
                    return Response({'message': 'Thiếu điểm giữa kỳ hoặc điểm giữa kỳ không phải số'}, status=status.HTTP_400_BAD_REQUEST)
                
                if values[6].isdigit():
                    score.final_score = values[6] 
                else:
                    return Response({'message': 'Thiếu điểm cuối kỳ hoặc điểm cuối kỳ không phải số'}, status=status.HTTP_400_BAD_REQUEST)
                
                if values[7].isdigit():
                    score.user = User.objects.filter(pk=values[7]).first() 
                else:
                    return Response({'message': 'Thiếu UserID hoặc UserID không phải số'}, status=status.HTTP_400_BAD_REQUEST)
                
                score.course = Course.objects.filter(pk=course_id).first()
                list_score.append(score)
            except KeyError as e:
                print(f"KeyError: {e}")
                return Response({'message': 'Có lỗi xảy ra khi Import'}, status=status.HTTP_400_BAD_REQUEST)

        # Save to database
        Score.objects.bulk_create(list_score)
        return Response({'message': 'Import thành công'}, status=status.HTTP_200_OK)   


    @swagger_auto_schema(operation_description='Export score list to csv file',)
    def get(self, request, *args, **kwargs): 
        course_id = request.query_params.get('course_id')
        headers = ['score1', 'score2', 'score3', 'score4', 'score5', 'midterm_score', 'final_score', 'user_id']
        file_name = f"scores_{strftime('%Y-%m-%d-%H-%M')}"

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

        writer = csv.writer(response)
        writer.writerow(headers)

        scores = Score.objects.filter(course_id=course_id)
        for score in scores:
            writer.writerow([
                score.score1,
                score.score2,
                score.score3,
                score.score4,
                score.score5,
                score.midterm_score,
                score.final_score,
                score.user_id,
                score.course_id
            ])

        return response
    

@method_decorator(csrf_exempt, name='dispatch')
class PDFHandleView(generics.RetrieveAPIView):
    parser_classes = (FileUploadParser, MultiPartParser)
    serializer_class = ScoreSerializer

    @swagger_auto_schema(operation_description='Import score list from csv file',)
    def get(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id')

        # Create the HttpResponse object with PDF header
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="scores_report.pdf"'

        # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()
        # Create the PDF object, using the buffer as its "file."
        c = canvas.Canvas(buffer, pagesize=landscape(letter))

        # Define the table headers
        table_headers = ['Score 1', 'Score 2', 'Score 3', 'Score 4', 'Score 5', 'Midterm Score', 'Final Score', 'Course', 'User']

        scores = Score.objects.filter(course_id=course_id)
        # Define the table data
        table_data = []
        for score in scores:
            table_data.append([
                score.score1 or '',
                score.score2 or '',
                score.score3 or '',
                score.score4 or '',
                score.score5 or '',
                score.midterm_score or '',
                score.final_score or '',
                score.course.name,
                score.user.email
            ])
        
         # Create the table and add the style
        table = Table([table_headers] + table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Add the table to the PDF
        table.wrapOn(c, inch, inch)
        table.drawOn(c, inch, inch)

        # Close the PDF object cleanly, and we're done.
        c.showPage()
        c.save()
        
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response


def index(request):
    return HttpResponse("e-Course App")