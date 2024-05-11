from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from ..models import UserInfo
from unittest.mock import patch
from ..models import MeditationTheme, MeditationNarrator
from django.core.files.uploadedfile import SimpleUploadedFile
from asgiref.sync import sync_to_async
from unittest.mock import patch, AsyncMock
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from thoughts_core.models import Chat
import logging


# class UserInfoViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="testuser", password="12345")
#         self.user_info = UserInfo.objects.create(
#             user=self.user, additional_data="test data"
#         )
#         self.client.login(username="testuser", password="12345")

#     def test_user_info_retrieval(self):
#         url = reverse(
#             "userinfo-detail", args=[self.user_info.pk]
#         )  # Adjust the URL name as needed
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("additional_data", response.json())

#     def test_user_info_not_found(self):
#         self.client.logout()
#         another_user = User.objects.create_user(
#             username="anotheruser", password="54321"
#         )
#         self.client.login(username="anotheruser", password="54321")
#         url = reverse(
#             "userinfo-detail", args=[self.user_info.pk]
#         )  # Adjust the URL name as needed
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# class MeditationViewSetTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="testuser", password="12345")
#         self.theme = MeditationTheme.objects.create(name="Relaxation")
#         self.narrator = MeditationNarrator.objects.create(name="John Doe")
#         self.client.login(username="testuser", password="12345")
#         self.token = RefreshToken.for_user(self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

#     @patch("path.to.S3Service.upload_file")
#     def test_create_meditation(self, mock_upload_file):
#         url = reverse("meditation-list")  # Adjust the URL name as needed
#         data = {
#             "name": "Test Meditation",
#             "meditation_theme_id": self.theme.pk,
#             "meditation_narrator_id": self.narrator.pk,
#             "cover_file_name": "test_cover.jpg",
#             "file": SimpleUploadedFile(
#                 "test.mp3", b"file_content", content_type="audio/mp3"
#             ),
#         }
#         response = self.client.post(url, data, format="multipart")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         mock_upload_file.assert_called_once()


# class ChatBotAPIViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="testuser", password="12345")
#         self.token = RefreshToken.for_user(self.user)
#         self.client = APIClient()
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

#     @patch("thoughts_core.views.OpenAiClientSingleton.get_client")
#     async def test_chat_bot_response(self, mock_get_client):
#         mock_client = AsyncMock()
#         mock_get_client.return_value = mock_client
#         mock_client.chat.completions.create.return_value = {
#             "choices": [
#                 {
#                     "message": {
#                         "content": '{"message": "Hi!", "suggested_meditations": []}'
#                     }
#                 }
#             ]
#         }

#         url = reverse("chatbot")  # Adjust the URL name as needed
#         data = {"message": "Hello!", "chat_id": 1}
#         response = await sync_to_async(self.client.post)(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("Hi!", response.content.decode())


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
