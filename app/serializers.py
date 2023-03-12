from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField
from .models import Course, Score, User


class CourseSerializer(ModelSerializer):    
    class Meta:
        model = Course
        fields = ['id', 'name', 'created_date', 'updated_date']


class UserSerializer(ModelSerializer):
    # courses = CourseSerializer(many=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'email', 'is_staff', 'is_superuser', 'className', 'date_joined']
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



