from django.http import HttpResponse
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import openai
import os
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services.MeditationService import MeditationService
from .services.RecommendationService import RecommendationService
from .services.S3Service import S3Service
from .services.UserService import UserService

from .models import (
    Achievement,
    Chat,
    MeditationNarrator,
    Meditation,
    MeditationTheme,
    MeditationGrade,
    MeditationSession,
    UserInfo,
)
from .serializers import (
    AchievementSerializer,
    ChatSerializer,
    GetReplySerializerRequest,
    MeditationNarratorSerializer,
    UserAchievementSerializer,
    UserInfoSerializer,
    MeditationSerializer,
    MeditationThemeSerializer,
    MeditationGradeSerializer,
    MeditationSessionSerializer,
    UserRegistrationSerializer
)

from adrf.views import APIView as AsyncAPIView
from rest_framework.views import APIView

from .services.logger import logger


class OpenAiClientSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAiClientSingleton, cls).__new__(cls)
            cls._instance.client = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        return cls._instance

    def get_client(self):
        return self.client


class UserInfoViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = UserInfoSerializer
    queryset = UserInfo.objects.all()

    def get_queryset(self):
        return UserInfo.objects.filter(user=self.request.user)


class AchievementViewSet(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    queryset = Achievement.objects.all()


class MeditationViewSet(viewsets.ModelViewSet):
    serializer_class = MeditationSerializer
    queryset = Meditation.objects.all()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'meditation_theme_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'meditation_narrator_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'cover_file_name': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        consumes=['multipart/form-data'],
        responses={
            200: MeditationSerializer,
            400: "Bad request",
            404: "User or Achievement not found",
        },
    )
    def create(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        meditation_data = {
            'name': request.data.get('name'),
            'meditation_theme_id': request.data.get('meditation_theme_id'),
            'meditation_narrator_id': request.data.get('meditation_narrator_id'),
            'audio_file_name': "default_file_name",
            'cover_file_name': request.data.get('cover_file_name'),
        }

        serializer = MeditationSerializer(data=meditation_data)
        if serializer.is_valid():
            serializer.save()
            uploaded_file = request.data['file']

            new_file_name = str(serializer.instance.id) + "_meditation"
            uploaded_file.name = new_file_name
            S3Service.upload_file(upload_file=uploaded_file)
            serializer.instance.audio_file_name = new_file_name
            serializer.instance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        audio_file = S3Service.get_file(key=instance.audio_file_name)

        response_data = {
            'name': instance.name,
            'meditation_theme_id': instance.meditation_theme_id,
            'meditation_narrator_id': instance.meditation_narrator_id,
            'audio_file_name': instance.audio_file_name,
            'cover_file_name': instance.cover_file_name,
        }

        response = HttpResponse(audio_file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="audio_file.mp3"'
        for key, value in response_data.items():
            response[key] = value

        return response


class MeditationThemeViewSet(viewsets.ModelViewSet):
    serializer_class = MeditationThemeSerializer
    queryset = MeditationTheme.objects.all()


class MeditationGradeViewSet(viewsets.ModelViewSet):
    serializer_class = MeditationGradeSerializer
    queryset = MeditationGrade.objects.all()


class MeditationSessionViewSet(viewsets.ModelViewSet):
    serializer_class = MeditationSessionSerializer
    queryset = MeditationSession.objects.all()

    @action(detail=True, methods=["post"], url_path="end")
    def end_session(self, request):
        meditation_session = self.get_object()
        MeditationService.end_meditation_session(meditation_session=meditation_session)
        serializer = self.get_serializer(meditation_session)
        return Response(serializer.data)


class MeditationNarratorViewSet(viewsets.ModelViewSet):
    serializer_class = MeditationNarratorSerializer
    queryset = MeditationNarrator.objects.all()


class ManageUserAchievements(APIView):
    @swagger_auto_schema(
        request_body=UserAchievementSerializer,
        responses={
            200: UserInfoSerializer,
            400: "Bad request",
            404: "User or Achievement not found",
        },
    )
    def post(self, request, action, *args, **kwargs):
        serializer = UserAchievementSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data.get("user_id")
            achievement_id = serializer.validated_data.get("achievement_id")
            if action == "add":
                user = UserService.add_achievement_to_user(
                    user_id=user_id, achievement_id=achievement_id
                )
            elif action == "remove":
                user = UserService.remove_achievement_from_user(
                    user_id=user_id, achievement_id=achievement_id
                )
            else:
                return Response(
                    {"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
                )
            if user:
                user_serializer = UserInfoSerializer(user)
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": "Failed to update user."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


async def generate_chat_completion(conversation, new_message):
    client = OpenAiClientSingleton().get_client()
    conversation.insert(
        0,
        {
            "role": "system",
            "content": """You are a helpful assistant. 
            You have to understand user problem and his feelings and recommend him meditation from list below. 
            You can also ask user about his feelings and recommend him meditation based on his feelings. 
            Write in russian.
            Meditations: 'медитация для сна', 'медитация для пробуждения', 'медитация для снятия тревоги', 'медитация для снятия стресса',
            'медитация для снятия депрессии', 'медитация для снятия паники', 'медитация для снятия страха',
            'медитация для снятия боли', 'медитация для снятия гнева', 'медитация для снятия раздражения', 'медитация для снятия одиночества',
            'медитация для снятия страха перед смертью', 'медитация для снятия страха перед болезнью', 'медитация для снятия страха перед неудачей',
            'медитация для снятия страха перед критикой', 'медитация для снятия страха перед общением', 'медитация для снятия страха перед людьми',
            'медитация для снятия страха перед животными', 'медитация для снятия страха перед темнотой', 'медитация для снятия страха перед высотой'
            """,
        },
    )
    conversation.append({"role": "user", "content": new_message})

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )

    conversation.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )

    return conversation[1:]


class ChatBotAPIView(AsyncAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetReplySerializerRequest

    @swagger_auto_schema(
        request_body=GetReplySerializerRequest,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Response message",
            ),
            400: "Bad request",
            404: "Chat not found",
        },
    )
    async def post(self, request):
        serializer = GetReplySerializerRequest(data=request.data)
        if serializer.is_valid():
            new_message = serializer.validated_data.get("message")
            chat_id = serializer.validated_data.get("chat_id")
            try:
                requested_chat = await Chat.objects.aget(user=request.user, id=chat_id)
            except ObjectDoesNotExist:
                return Response("Chat not found", status=status.HTTP_404_NOT_FOUND)
            conversation = requested_chat.chat_messages
            updated_conversation = await generate_chat_completion(
                conversation, new_message
            )
            requested_chat.chat_messages = updated_conversation
            await requested_chat.asave()
            return Response(
                updated_conversation[-1].get("content"), status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)


class RecommendMeditationsApiView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: MeditationSerializer(many=True),
            400: "Bad request"
        },
    )
    def get(self, request):
        user = self.request.user

        recommended_meditations = RecommendationService.recommend_meditations_for_user(user=user.userinfo)
        serialized_meditations = MeditationSerializer(recommended_meditations, many=True)

        return Response(serialized_meditations.data)


class UserRegistrationView(APIView):

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            200: UserRegistrationSerializer,
            400: "Bad request"
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.instance
            UserService.create_user_info(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
