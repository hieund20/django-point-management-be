from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField
from .models import Course, Score, User, ForumPost, ForumPostAnswer


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class UserSerializer(ModelSerializer):
    courses = CourseSerializer(many=True)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }

    def create(self, validated_data):
        print("validated_data", validated_data)
        courses_data = validated_data['courses'] # Remove courses from validated_data
        print("courses_data", courses_data)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if courses_data:
            courses = []
            for course_data in courses_data:
                course, _ = Course.objects.get_or_create(**course_data)
                courses.append(course)
            user.courses.add(*courses)

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


class ForumPostAnswerSerializer(ModelSerializer):
    def create(self, validated_data):
        obj = ForumPostAnswer.objects.create(**validated_data)
        return obj

    class Meta:
        model = ForumPostAnswer
        fields = '__all__'
