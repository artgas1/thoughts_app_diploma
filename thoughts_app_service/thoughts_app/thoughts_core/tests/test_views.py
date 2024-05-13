from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from ..models import UserInfo
from unittest.mock import patch
from ..models import (
    MeditationTheme,
    MeditationNarrator,
    ProgressLevel,
    MeditationSession,
    Meditation,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from asgiref.sync import sync_to_async
from unittest.mock import patch, AsyncMock
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from thoughts_core.models import Chat
import logging
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import async_to_sync


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
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
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
        response = self.client.post("/api/chat/", self.chat_data, format="json")
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
                MeditationSession(user=self.user, meditation=Meditation.objects.first())
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
        self.assertEqual(response.data, {"detail": "Failed to get progress data."})

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
        self.url = (
            "/api/meditation/recommend_meditations/"  # Update with the actual URL
        )
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
