from .logger import logger
from ..models import User, UserInfo, MeditationSession, ProgressLevel
from ..repositories.UserRepository import UserRepository
from ..repositories.AchievementRepository import AchievementRepository


class UserService:
    @staticmethod
    def create_user_info(
        user: User, name: str = "", phone_number: str = ""
    ) -> UserInfo:
        return UserRepository.create_user(
            user=user, name=name, phone_number=phone_number
        )

    @staticmethod
    def get_user_by_id(user_id: int) -> UserInfo | None:
        return UserRepository.get_user_by_id(user_id=user_id)

    @staticmethod
    def add_achievement_to_user(user_id: int, achievement_id: int) -> User | None:
        user = UserRepository.get_user_by_id(user_id=user_id)
        achievement = AchievementRepository.get_achievement_by_id(
            achievement_id=achievement_id
        )
        if user and achievement:
            AchievementRepository.add_achievement_to_user(
                user=user, achievement=achievement
            )
            return user
        return None

    @staticmethod
    def remove_achievement_from_user(user_id: int, achievement_id: int) -> User | None:
        user = UserRepository.get_user_by_id(user_id=user_id)
        achievement = AchievementRepository.get_achievement_by_id(
            achievement_id=achievement_id
        )
        logger.info(f"User {user}, achievement {achievement}")
        if user and achievement:
            AchievementRepository.delete_achievement_from_user(
                user=user, achievement=achievement
            )
            return user
        return None

    @staticmethod
    def get_level(user: User) -> ProgressLevel:
        sessions_count = len(MeditationSession.objects.filter(user_id=user))
        progress_levels = ProgressLevel.objects.all().order_by("level")
        for i in range(len(progress_levels)):
            if sessions_count < progress_levels[i].level:
                return progress_levels[i]
        return progress_levels.last() if progress_levels else None
    
    # @swagger_serializer_method(serializer_or_field=openapi.Schema(type=openapi.TYPE_NUMBER))
    def get_progress_to_next_level(user: User) -> float:
        sessions_count = len(MeditationSession.objects.filter(user_id=user))
        progress_levels = ProgressLevel.objects.all().order_by("level")
        for i in range(len(progress_levels)):
            if sessions_count < progress_levels[i].level:
                return sessions_count / progress_levels[i].level
        return 1 if progress_levels else None