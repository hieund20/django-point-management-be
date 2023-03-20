from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField
from .models import Course, Score, User, ForumPost


class CourseSerializer(ModelSerializer):    
    class Meta:
        model = Course
        fields = '__all__'


class UserSerializer(ModelSerializer):
    # courses = CourseSerializer(many=True)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user
    

class ScoreSerializer(ModelSerializer):
    def create(self, validated_data):
        obj = Score.objects.create(**validated_data)
        return obj
    
    class Meta:
        model = Score
        fields = '__all__'


class ForumPostSerializer(ModelSerializer):
    def create(self, validated_data):
        obj = ForumPost.objects.create(**validated_data)
        return obj
    
    class Meta:
        model = ForumPost
        fields = '__all__'



