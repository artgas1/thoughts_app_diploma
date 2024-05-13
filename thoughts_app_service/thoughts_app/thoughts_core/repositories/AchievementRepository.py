from typing import List

from ..models import Achievement, UserInfo
from ..services.logger import logger


class AchievementRepository:
    @staticmethod
    def create_achievement(
        name: str, cover_url: str, description: str
    ) -> Achievement:
        return Achievement.objects.create(
            name=name, cover_url=cover_url, description=description
        )

    @staticmethod
    def get_achievement_by_id(achievement_id: int) -> Achievement | None:
        try:
            return Achievement.objects.get(pk=achievement_id)
        except Achievement.DoesNotExist:
            logger.error(f"Achievement with id {achievement_id} not found!")
            return None

    @staticmethod
    def get_user_achievements(user: UserInfo) -> List[Achievement]:
        return user.achievements.all()

    @staticmethod
    def add_achievement_to_user(
        user: UserInfo, achievement: Achievement
    ) -> UserInfo:
        user.achievements.add(achievement)
        user.save()
        return user

    @staticmethod
    def delete_achievement_from_user(
        user: UserInfo, achievement: Achievement
    ) -> UserInfo:
        user.achievements.remove(achievement)
        user.save()
        return user
