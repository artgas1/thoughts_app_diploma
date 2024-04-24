from rest_framework import serializers
from .models import (
    Achievement,
    Meditation,
    MeditationGrade,
    MeditationNarrator,
    MeditationSession,
    MeditationTheme,
    User,
    Chat,
    UserInfo,
)
from adrf.serializers import Serializer as AsyncSerializer


class GetReplySerializerRequest(AsyncSerializer):
    message = serializers.CharField()
    chat_id = serializers.UUIDField()


class ChatSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    chat_messages = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        user = self.context["request"].user
        user = User.objects.get(id=user.id)
        return Chat.objects.create(user=user, **validated_data)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class MeditationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meditation
        fields = "__all__"


class MeditationThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationTheme
        fields = "__all__"


class MeditationGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationGrade
        fields = "__all__"


class MeditationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationSession
        fields = "__all__"


class MeditationNarratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationNarrator
        fields = "__all__"


class UserAchievementSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    achievement_id = serializers.IntegerField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'].split('@')[0],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
