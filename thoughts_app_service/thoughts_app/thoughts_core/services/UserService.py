from .logger import logger
from ..models import User, UserInfo
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
