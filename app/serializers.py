from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField
from .models import Course, Score, User, ForumPost, ForumPostAnswer


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class UserSerializer(ModelSerializer):
    courses = CourseSerializer(many=True, required=False)
    avatar_url = SerializerMethodField(source='avatar')

    def get_avatar_url(self, user):
        if user.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % user.avatar.name) if request else ''

    class Meta:
        model = User
        fields = ['id', 'username', 'password',
                'first_name', 'last_name', 'is_active', 'courses', 'is_staff',
                'is_superuser', 'email', 'email',  'avatar', 'avatar_url']
        extra_kwargs = {
            'avatar': {'write_only': True},
            'password': {'write_only': True}
        }


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
