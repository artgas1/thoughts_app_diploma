from adrf.serializers import Serializer as AsyncSerializer
from rest_framework import serializers

from .models import (
    Achievement,
    Chat,
    Meditation,
    MeditationGrade,
    MeditationNarrator,
    MeditationSession,
    MeditationTheme,
    User,
    UserInfo,
)


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        exclude = ["user"]
        read_only_fields = ["id", "created_at", "updated_at", "chat_messages"]

    def create(self, validated_data):
        # Use the request user from the serializer context
        user = self.context["request"].user
        return Chat.objects.create(user=user, **validated_data)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ["id", "user"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class MeditationSerializer(serializers.ModelSerializer):
    # user_grade = serializers.SerializerMethodField()
    # user_sessions = serializers.SerializerMethodField()

    # def get_user_sessions(self, obj):
    #     user = self.context["request"].user
    #     sessions = MeditationSession.objects.filter(user_id=user, meditation_id=obj)
    #     return MeditationSessionSerializer(sessions, many=True).data

    # def get_user_grade(self, obj):
    #     user = self.context["request"].user
    #     grade = MeditationGrade.objects.filter(user_id=user, meditation_id=obj).first()
    #     return grade.grade if grade else None

    class Meta:
        model = Meditation
        fields = "__all__"


class GetGPTAnswerRequestSerializer(AsyncSerializer):
    message = serializers.CharField()
    chat_id = serializers.UUIDField()


class SuggestedMeditationSerializer(AsyncSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class GetGPTAnswerResponseSerializer(AsyncSerializer):
    message = serializers.CharField()
    suggested_meditations = serializers.ListField(
        child=SuggestedMeditationSerializer(), allow_empty=True
    )


class MeditationThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationTheme
        fields = "__all__"


class MeditationGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationGrade
        fields = "__all__"


class MeditationSessionSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = self.context["request"].user
        user = User.objects.get(id=user.id)
        return MeditationSession.objects.create(user=user, **validated_data)

    class Meta:
        model = MeditationSession
        exclude = ["user"]


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
        fields = ["email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"].split("@")[0],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class MeditationProgressSerializer(serializers.Serializer):
    level_name = serializers.CharField()
    next_level_count = serializers.IntegerField()
    current_level_count = serializers.IntegerField()
