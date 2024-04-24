from typing import List

from django.contrib.auth.models import User

from ..models import UserInfo
from ..services.logger import logger


class UserRepository:
    @staticmethod
    def get_user_by_id(user_id: int) -> UserInfo | None:
        try:
            return UserInfo.objects.get(pk=user_id)
        except UserInfo.DoesNotExist:
            logger.error(f"User with id {user_id} not found!")
            return None

    @staticmethod
    def create_user(user: User, name: str, phone_number: str) -> UserInfo:
        return UserInfo.objects.create(user=user, name=name, phone_number=phone_number)

    @staticmethod
    def delete_user_by_id(user_id: int) -> None:
        try:
            UserInfo.objects.get(pk=user_id).delete()
        except UserInfo.DoesNotExist:
            logger.error(f"User with id {user_id} not found!")

    @staticmethod
    def get_all_users() -> List[UserInfo]:
        return UserInfo.objects.all()

    @staticmethod
    def update_user_name(user: UserInfo, name: str) -> UserInfo:
        user.name = name
        user.save()
        return user

    @staticmethod
    def update_user_phone_number(user: UserInfo, phone_number: str) -> UserInfo:
        user.phone_number = phone_number
        user.save()
        return user
