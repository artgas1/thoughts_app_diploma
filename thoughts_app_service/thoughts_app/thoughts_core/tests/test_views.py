import json
import logging
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from thoughts_core.models import Chat
from thoughts_core.views import (
    generate_chat_completion,
    get_all_meditations,
    prepare_system_message,
)

from ..models import (
    Meditation,
    MeditationNarrator,
    MeditationSession,
    MeditationTheme,
    ProgressLevel,
)

# Create your tests here.


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )

    def tearDown(self):
        self.user.delete()

    def test_user_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "testuser1@mail.ru", "password": "testpassword123"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_invalid_data(self):
        logging.getLogger("django.request").setLevel(logging.ERROR)
        response = self.client.post(
            "/api/auth/register/",
            {"email": "testuser1", "password": "123"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_user_login(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "testuser", "password": "testpassword123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_data(self):
        logging.getLogger("django.request").setLevel(logging.ERROR)
        response = self.client.post(
            "/api/auth/token/",
            {"username": "testuser", "password": "testpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_jwt_refresh(self):
        token = RefreshToken.for_user(self.user)
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": str(token)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_user_using_jwt(self):
        token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )
        response = self.client.get("/api/meditation/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ChatViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        self.chat_data = {"chat_messages": []}
        self.client.force_authenticate(user=self.user)
        self.another_user = User.objects.create_user(
            username="anotheruser", password="testpassword123"
        )

    def tearDown(self):
        self.user.delete()
        self.another_user.delete()

    def test_create_chat(self):
        response = self.client.post(
            "/api/chat/", self.chat_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(Chat.objects.get().user, self.user)

    def test_retrieve_chats(self):
        Chat.objects.create(
            user=self.user,
            chat_messages=[
                {
                    "id": "id_user",
                    "created_at": "2024-05-11T00:26:37.021Z",
                    "updated_at": "2024-05-11T00:26:37.021Z",
                    "chat_messages": {},
                }
            ],
        )
        Chat.objects.create(
            user=self.another_user,
            chat_messages=[
                {
                    "id": "id_another_user",
                    "created_at": "2024-05-11T00:26:37.021Z",
                    "updated_at": "2024-05-11T00:26:37.021Z",
                    "chat_messages": {},
                }
            ],
        )
        response = self.client.get("/api/chat/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 1
        )  # Checks if user retrieves only their chats

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)  # No user authenticated
        response = self.client.get("/api/chat/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MeditationProgressViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        self.meditations = (
            Meditation.objects.create()
        )  # Now the Meditation model is defined
        self.meditations_sessions = MeditationSession.objects.bulk_create(
            [
                MeditationSession(
                    user=self.user, meditation=Meditation.objects.first()
                )
                for _ in range(3)
            ]
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("meditation_progress")

        # Mock data
        self.level = ProgressLevel(name="Beginner", level=5)
        self.sessions = [
            MeditationSession(user=self.user) for _ in range(3)
        ]  # Assuming this matches your model definition

    def tearDown(self):
        self.user.delete()
        self.meditations.delete()
        for session in self.meditations_sessions:
            session.delete()

    @patch(
        "thoughts_core.services.UserService.UserService.get_level"
    )  # Correct the path as necessary
    def test_get_meditation_progress_success(self, mock_get_level):
        mock_get_level.return_value = self.level
        response = self.client.get(self.url)
        expected_data = {
            "level_name": "Beginner",
            "next_level_count": 5,
            "current_level_count": 3,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    @patch("thoughts_core.services.UserService.UserService.get_level")
    def test_get_meditation_progress_no_level_found(self, mock_get_level):
        mock_get_level.return_value = None
        response = self.client.get(self.url)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"detail": "Failed to get progress data."}
        )

    def test_authentication_required(self):
        self.client.force_authenticate(user=None)  # No user authenticated
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RecommendMeditationsApiViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        self.url = "/api/meditation/recommend_meditations/"  # Update with the actual URL
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.user.delete()

    @patch(
        "thoughts_core.services.RecommendationService.RecommendationService.recommend_meditations_for_user"
    )
    def test_recommend_meditations(self, mock_recommend_service):
        # Create instances of themes and narrators
        theme = MeditationTheme.objects.create(
            name="Relaxation", cover_file_url="http://example.com/theme.jpg"
        )
        narrator = MeditationNarrator.objects.create(name="John Doe")

        # Create two real meditation instances
        meditation1 = Meditation.objects.create(
            name="Zen Meditation",
            meditation_theme=theme,
            meditation_narrator=narrator,
            audio_file_url="http://audio.com/zen.mp3",
            cover_file_url="http://image.com/zen.jpg",
        )
        meditation2 = Meditation.objects.create(
            name="Mindfulness",
            meditation_theme=theme,
            meditation_narrator=narrator,
            audio_file_url="http://audio.com/mindfulness.mp3",
            cover_file_url="http://image.com/mindfulness.jpg",
        )

        # Return these instances from the mocked service
        mock_recommend_service.return_value = [meditation1, meditation2]

        # Make GET request to the API
        response = self.client.get(self.url)

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure serializers work as expected
        self.assertTrue("Zen Meditation" in response.content.decode())
        self.assertTrue("Mindfulness" in response.content.decode())

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UtilityFunctionTests(unittest.IsolatedAsyncioTestCase):

    @patch("thoughts_core.views.Meditation.objects.all")
    @patch("thoughts_core.views.MeditationSerializer")
    async def test_get_all_meditations(
        self, mock_serializer, mock_meditation_objects_all
    ):
        # Setup mock data
        mock_meditation = MagicMock()
        mock_meditation_objects_all.return_value = self._async_iter(
            [mock_meditation]
        )
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = {"id": 1, "title": "Meditation 1"}

        # Call the function
        result = await get_all_meditations()

        # Assertions
        self.assertEqual(result, [{"id": 1, "title": "Meditation 1"}])
        mock_meditation_objects_all.assert_called_once()
        mock_serializer.assert_called_once_with(mock_meditation)

    def test_prepare_system_message(self):
        meditations = [{"id": 1, "title": "Meditation 1"}]
        expected_message_content = f"""
Ты — виртуальный ассистент, владеющий русским языком и специализирующийся на медитациях. Твоя задача — определить проблемы и чувства пользователя, чтобы подобрать наиболее подходящую медитацию из предложенного списка. При необходимости, ты можешь задать дополнительные вопросы о чувствах пользователя, чтобы уточнить его состояние и на этой основе предложить соответствующую медитацию.

Доступные медитации:
{json.dumps(meditations, ensure_ascii=False, indent=2)}

В ответ отправь только JSON, где `message` твой ответ пользователю, а `suggested_meditations` — предлагаемые медитации с их ID и названием.
"""
        expected_result = {
            "role": "system",
            "content": expected_message_content,
        }

        # Call the function
        result = prepare_system_message(meditations)

        # Assertions
        self.assertEqual(result, expected_result)

    def _async_iter(self, items):
        async def async_generator():
            for item in items:
                yield item

        return async_generator()


class GenerateChatCompletionTests(unittest.IsolatedAsyncioTestCase):

    @patch("thoughts_core.views.OpenAiClientSingleton")
    @patch("thoughts_core.views.get_all_meditations", new_callable=AsyncMock)
    @patch("thoughts_core.views.prepare_system_message")
    async def test_generate_chat_completion_valid(
        self,
        mock_prepare_system_message,
        mock_get_all_meditations,
        mock_openai_client,
    ):
        mock_get_all_meditations.return_value = [
            {"id": 1, "title": "Meditation 1"}
        ]
        mock_prepare_system_message.return_value = {
            "role": "system",
            "content": "system message content",
        }

        mock_create = AsyncMock()
        mock_create.return_value.choices = [AsyncMock()]
        mock_create.return_value.choices[0].message.content = (
            '{"message": "Hello", "suggested_meditations": [{"id": 1, "title": "Meditation 1"}]}'
        )
        mock_openai_client.return_value.get_client.return_value.chat.completions.create = (
            mock_create
        )

        conversation = []
        new_message = "Hello"
        updated_conversation = await generate_chat_completion(
            conversation, new_message
        )

        self.assertIsNotNone(updated_conversation)
        self.assertEqual(updated_conversation[-1]["role"], "assistant")
        self.assertIn("content", updated_conversation[-1])

    @patch("thoughts_core.views.OpenAiClientSingleton")
    @patch("thoughts_core.views.get_all_meditations", new_callable=AsyncMock)
    @patch("thoughts_core.views.prepare_system_message")
    async def test_generate_chat_completion_invalid_json(
        self,
        mock_prepare_system_message,
        mock_get_all_meditations,
        mock_openai_client,
    ):
        mock_get_all_meditations.return_value = [
            {"id": 1, "title": "Meditation 1"}
        ]
        mock_prepare_system_message.return_value = {
            "role": "system",
            "content": "system message content",
        }

        mock_create = AsyncMock()
        mock_create.return_value.choices = [AsyncMock()]
        mock_create.return_value.choices[0].message.content = "invalid json"
        mock_openai_client.return_value.get_client.return_value.chat.completions.create = (
            mock_create
        )

        conversation = []
        new_message = "Hello"
        updated_conversation = await generate_chat_completion(
            conversation, new_message
        )

        self.assertIsNone(updated_conversation)

    @patch("thoughts_core.views.OpenAiClientSingleton")
    @patch("thoughts_core.views.get_all_meditations", new_callable=AsyncMock)
    @patch("thoughts_core.views.prepare_system_message")
    async def test_generate_chat_completion_api_error(
        self,
        mock_prepare_system_message,
        mock_get_all_meditations,
        mock_openai_client,
    ):
        mock_get_all_meditations.return_value = [
            {"id": 1, "title": "Meditation 1"}
        ]
        mock_prepare_system_message.return_value = {
            "role": "system",
            "content": "system message content",
        }

        mock_create = AsyncMock()
        mock_create.side_effect = Exception("API error")
        mock_openai_client.return_value.get_client.return_value.chat.completions.create = (
            mock_create
        )

        conversation = []
        new_message = "Hello"
        updated_conversation = await generate_chat_completion(
            conversation, new_message
        )

        self.assertIsNone(updated_conversation)


class ChatBotAPIViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.chat = Chat.objects.create(user=self.user, chat_messages=[])
        self.url = "/api/chatbot/"  # Update this to match your actual URL pattern name

    @patch(
        "thoughts_core.views.generate_chat_completion", new_callable=AsyncMock
    )
    def test_valid_request(self, mock_generate_chat_completion):
        response_content = {
            "message": "Привет! Вот рекомендованные медитации",
            "suggested_meditations": [{"id": 0, "name": "Meditation 1"}],
        }
        mock_generate_chat_completion.return_value = [
            {"content": json.dumps(response_content)}
        ]
        data = {"message": "Hello", "chat_id": self.chat.id}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, response_content)

    def test_invalid_request_data(self):
        data = {"message": "", "chat_id": self.chat.id}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chat_not_found(self):
        data = {"message": "Hello", "chat_id": 999}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, "Chat not found")

    @patch(
        "thoughts_core.views.generate_chat_completion", new_callable=AsyncMock
    )
    def test_invalid_gpt_response(self, mock_generate_chat_completion):
        mock_generate_chat_completion.return_value = None
        data = {"message": "Hello", "chat_id": self.chat.id}

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Invalid response from GPT")

    @patch(
        "thoughts_core.views.generate_chat_completion", new_callable=AsyncMock
    )
    def test_invalid_response_serializer(self, mock_generate_chat_completion):
        # Mock the generate_chat_completion to return a valid conversation
        response_content = {
            "message": "Invalid response",
        }
        mock_generate_chat_completion.return_value = [
            {"role": "assistant", "content": json.dumps(response_content)}
        ]

        data = {"message": "Hello", "chat_id": self.chat.id}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "ErrorDetail", str(response.data)
        )  # Check if the response contains errors
