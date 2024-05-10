from django.urls import include, path
from rest_framework import routers
from .views import (
    ChatBotAPIView,
    ChatViewSet,
    AchievementViewSet,
    MeditationViewSet,
    MeditationThemeViewSet,
    MeditationGradeViewSet,
    MeditationSessionViewSet,
    MeditationNarratorViewSet,
    ManageUserAchievements,
    RecommendMeditationsApiView,
    UserRegistrationView,
    UserInfoView,
    MeditationProgressView,
)

router = routers.SimpleRouter()

router.register(r"chat", ChatViewSet, basename="chat")

router.register(r"achievement", AchievementViewSet, basename="achievement")
router.register(r"meditation", MeditationViewSet, basename="meditation")
router.register(
    r"meditation_theme", MeditationThemeViewSet, basename="meditation_theme"
)
router.register(
    r"meditation_grade", MeditationGradeViewSet, basename="meditation_grade"
)
router.register(
    r"meditation_session", MeditationSessionViewSet, basename="meditation_session"
)
router.register(
    r"meditation_narrator", MeditationNarratorViewSet, basename="meditation_narrator"
)

urlpatterns = [
    path(
        "achievement/add_achievement_to_user/",
        ManageUserAchievements.as_view(),
        {"action": "add"},
        name="add_achievement_to_user",
    ),
    path(
        "achievement/remove_achievement_from_user/",
        ManageUserAchievements.as_view(),
        {"action": "remove"},
        name="remove_achievement_from_user",
    ),
    path(
        "meditation/recomendate_meditations/",
        RecommendMeditationsApiView.as_view(),
        name="recomendate_meditations",
    ),
    path("", include(router.urls)),
    path("chatbot/", ChatBotAPIView.as_view(), name="chatbot"),
    path("auth/register/", UserRegistrationView.as_view(), name="user_registration"),
    path("user_info/", UserInfoView.as_view(), name="user_info"),
    path("meditation_progress/", MeditationProgressView.as_view(), name="meditation_progress"),
]
