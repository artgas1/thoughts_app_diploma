import json
import os

import openai
from adrf.views import APIView as AsyncAPIView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import (
    Achievement,
    Chat,
    Meditation,
    MeditationGrade,
    MeditationNarrator,
    MeditationSession,
    MeditationTheme,
    UserInfo,
)
from .serializers import (
    AchievementSerializer,
    ChatSerializer,
    GetGPTAnswerRequestSerializer,
    GetGPTAnswerResponseSerializer,
    MeditationGradeSerializer,
    MeditationNarratorSerializer,
    MeditationProgressSerializer,
    MeditationSerializer,
    MeditationSessionSerializer,
    MeditationThemeSerializer,
    UserAchievementSerializer,
    UserInfoSerializer,
    UserRegistrationSerializer,
)
from .services.logger import logger
from .services.RecommendationService import RecommendationService
from .services.S3Service import S3Service
from .services.UserService import UserService


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


class UserInfoView(RetrieveUpdateAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserInfoSerializer

    def get_object(self):
        try:
            return UserInfo.objects.filter(
                user=self.request.user
            ).first()  # Adjust this depending on your related name
        except UserInfo.DoesNotExist:
            # Properly handle the case where the UserInfo does not exist
            raise Http404("No UserInfo found for this user.")


class AchievementViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = AchievementSerializer
    queryset = Achievement.objects.all()


class MeditationViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = MeditationSerializer
    queryset = Meditation.objects.all()

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'example': 'example.pdf',
                    },
                    'name': {
                        'type': 'string',
                        'example': 'Guided Meditation',
                    },
                    'meditation_theme_id': {
                        'type': 'integer',
                        'example': 1,
                    },
                    'meditation_narrator_id': {
                        'type': 'integer',
                        'example': 2,
                    },
                    'audio_file_url': {
                        'type': 'string',
                        'format': 'uri',
                        'example': 'http://example.com/audio.mp3',
                    },
                    'cover_file_url': {
                        'type': 'string',
                        'format': 'uri',
                        'example': 'http://example.com/cover.jpg',
                    },
                },
                'required': [
                    'file', 'name', 'meditation_theme_id', 
                    'meditation_narrator_id', 'audio_file_url', 
                    'cover_file_url'
                ],
            }
        },
        responses={
            200: MeditationSerializer,
            400: OpenApiTypes.OBJECT,  # Use a more specific structure if needed
            404: OpenApiTypes.OBJECT,  # Use a more specific structure if needed
        },
        examples=[
            OpenApiExample(
                "Example 400",
                value={"error": "Bad request"},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Example 404",
                value={"error": "User or Achievement not found"},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        if "file" not in request.data:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        meditation_data = {
            "name": request.data.get("name"),
            "meditation_theme_id": request.data.get("meditation_theme_id"),
            "meditation_narrator_id": request.data.get(
                "meditation_narrator_id"
            ),
            "audio_file_url": request.data.get("audio_file_url"),
            "cover_file_url": request.data.get("cover_file_url"),
        }

        serializer = MeditationSerializer(data=meditation_data)
        if serializer.is_valid():
            serializer.save()
            uploaded_file = request.data["file"]

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
            "name": instance.name,
            "meditation_theme_id": instance.meditation_theme_id,
            "meditation_narrator_id": instance.meditation_narrator_id,
            "audio_file_url": instance.audio_file_name,
            "cover_file_url": instance.cover_file_name,
        }

        response = HttpResponse(
            audio_file, content_type="application/octet-stream"
        )
        response["Content-Disposition"] = (
            'attachment; filename="audio_file.mp3"'
        )
        for key, value in response_data.items():
            response[key] = value

        return response


class MeditationThemeViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = MeditationThemeSerializer
    queryset = MeditationTheme.objects.all()


class MeditationGradeViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = MeditationGradeSerializer

    def get_queryset(self):
        return MeditationGrade.objects.filter(user_id=self.request.user)


class MeditationSessionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = MeditationSessionSerializer

    def get_queryset(self):
        return MeditationSession.objects.filter(user_id=self.request.user)


class MeditationNarratorViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = MeditationNarratorSerializer
    queryset = MeditationNarrator.objects.all()


class ManageUserAchievements(APIView):
    serializer_class = UserInfoSerializer

    @extend_schema(
        request=UserAchievementSerializer,
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
                    {"detail": "Invalid action."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user:
                user_serializer = UserInfoSerializer(user)
                return Response(
                    user_serializer.data, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Failed to update user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


async def get_all_meditations():
    """Retrieve all meditations and serialize them."""
    meditations = []
    async for meditation in Meditation.objects.all():
        meditation_data = MeditationSerializer(meditation).data
        meditations.append(meditation_data)
    return meditations


def prepare_system_message(meditations):
    """Prepare the system message for the conversation."""
    return {
        "role": "system",
        "content": f"""
Ты — виртуальный ассистент, владеющий русским языком и специализирующийся на медитациях. Твоя задача — определить проблемы и чувства пользователя, чтобы подобрать наиболее подходящую медитацию из предложенного списка. При необходимости, ты можешь задать дополнительные вопросы о чувствах пользователя, чтобы уточнить его состояние и на этой основе предложить соответствующую медитацию.

Доступные медитации:
{json.dumps(meditations, ensure_ascii=False, indent=2)}

В ответ отправь только JSON, где `message` твой ответ пользователю, а `suggested_meditations` — предлагаемые медитации с их ID и названием.
""",
    }


async def generate_chat_completion(conversation, new_message):
    client = OpenAiClientSingleton().get_client()

    meditations = await get_all_meditations()
    system_message = prepare_system_message(meditations)

    conversation.insert(0, system_message)
    conversation.append({"role": "user", "content": new_message})

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
        )
        gpt_response = response.choices[0].message.content
        logger.debug(f"GPT Response: {gpt_response}")

        json.loads(gpt_response)  # Validate JSON format

        conversation.append({"role": "assistant", "content": gpt_response})
        return conversation[1:]
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error during GPT chat completion: {e}")
        return None


class ChatBotAPIView(AsyncAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GetGPTAnswerResponseSerializer

    @extend_schema(
        request=GetGPTAnswerRequestSerializer,
        responses={
            200: GetGPTAnswerResponseSerializer,
            400: OpenApiTypes.STR,
            404: OpenApiTypes.STR,
        },
        examples=[
            OpenApiExample(
                "Example 400",
                value="Invalid response from GPT",
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Example 404",
                value="Chat not found",
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    async def post(self, request):
        serializer = GetGPTAnswerRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        new_message = serializer.validated_data.get("message")
        chat_id = serializer.validated_data.get("chat_id")

        try:
            requested_chat = await Chat.objects.aget(
                user=request.user, id=chat_id
            )
        except ObjectDoesNotExist:
            return Response("Chat not found", status=status.HTTP_404_NOT_FOUND)

        conversation = requested_chat.chat_messages
        updated_conversation = await generate_chat_completion(
            conversation, new_message
        )

        if not updated_conversation:
            return Response(
                "Invalid response from GPT", status=status.HTTP_400_BAD_REQUEST
            )

        requested_chat.chat_messages = updated_conversation
        await requested_chat.asave()

        response_data = json.loads(updated_conversation[-1].get("content"))
        response_serializer = GetGPTAnswerResponseSerializer(
            data=response_data
        )

        if response_serializer.is_valid():
            return Response(
                response_serializer.data, status=status.HTTP_200_OK
            )

        return Response(
            response_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ChatViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)


class RecommendMeditationsApiView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MeditationSerializer(many=True)

    @extend_schema(
        responses={200: MeditationSerializer(many=True), 400: "Bad request"},
    )
    def get(self, request):
        user = self.request.user

        recommended_meditations = (
            RecommendationService.recommend_meditations_for_user(user=user)
        )
        serialized_meditations = MeditationSerializer(
            recommended_meditations, many=True
        )

        return Response(serialized_meditations.data)


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={200: UserRegistrationSerializer, 400: "Bad request"},
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.instance
            UserService.create_user_info(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeditationProgressView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MeditationProgressSerializer

    @extend_schema(
        responses={
            200: MeditationProgressSerializer,
            400: "Bad request",
            500: "Internal server error",
        },
    )
    def get(self, request):
        level = UserService.get_level(user=request.user)
        if level:
            data = {
                "level_name": level.name,
                "next_level_count": level.level,
                "current_level_count": len(
                    MeditationSession.objects.filter(user_id=request.user)
                ),
            }
            serializer = MeditationProgressSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {"detail": "Failed to get progress data."},
            status=status.HTTP_400_BAD_REQUEST,
        )
