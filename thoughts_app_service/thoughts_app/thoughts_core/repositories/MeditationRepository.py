from datetime import datetime
from typing import List

from ..models import (
    Meditation,
    MeditationGrade,
    MeditationNarrator,
    MeditationSession,
    MeditationTheme,
    User,
    UserInfo,
)
from ..services.logger import logger


class MeditationRepository:
    @staticmethod
    def create_meditation_theme(name: str, cover_url) -> MeditationTheme:
        return MeditationTheme.objects.create(name=name, cover_url=cover_url)

    @staticmethod
    def get_meditation_theme_by_id(
        meditation_theme_id: int,
    ) -> MeditationTheme | None:
        try:
            return MeditationTheme.objects.get(pk=meditation_theme_id)
        except MeditationTheme.DoesNotExist:
            logger.error(
                f"MeditationTheme with id {meditation_theme_id} not found!"
            )
            return None

    @staticmethod
    def delete_meditation_theme(meditation_theme_id: int) -> None:
        try:
            MeditationTheme.objects.get(pk=meditation_theme_id).delete()
        except MeditationTheme.DoesNotExist:
            logger.error(
                f"MeditationTheme with id {meditation_theme_id} not found!"
            )

    @staticmethod
    def get_all_meditation_themes() -> List[MeditationTheme]:
        return MeditationTheme.objects.all()

    @staticmethod
    def create_meditation_narrator(name: str) -> MeditationNarrator:
        return MeditationNarrator.objects.create(name=name)

    @staticmethod
    def get_meditation_narrator_by_id(
        meditation_narrator_id: int,
    ) -> MeditationNarrator | None:
        try:
            return MeditationNarrator.objects.get(pk=meditation_narrator_id)
        except MeditationNarrator.DoesNotExist:
            logger.error(
                f"MeditationNarrator with id {meditation_narrator_id} not found!"
            )
            return None

    @staticmethod
    def delete_meditation_narrator_by_id(meditation_narrator_id: int) -> None:
        try:
            MeditationNarrator.objects.get(pk=meditation_narrator_id).delete()
        except MeditationNarrator.DoesNotExist:
            logger.error(
                f"MeditationNarrator with id {meditation_narrator_id} not found!"
            )

    @staticmethod
    def get_all_meditation_narrators() -> List[MeditationNarrator]:
        return MeditationNarrator.objects.all()

    @staticmethod
    def create_meditation(
        name: str,
        meditation_theme: MeditationTheme,
        meditation_narrator: MeditationNarrator,
        audio_url: str,
        cover_url: str,
    ) -> MeditationNarrator:
        return Meditation.objects.create(
            name=name,
            meditation_theme_id=meditation_theme,
            meditation_narrator=meditation_narrator,
            audio_url=audio_url,
            cover_url=cover_url,
        )

    @staticmethod
    def get_meditation_by_id(meditation__id: int) -> Meditation | None:
        try:
            return Meditation.objects.get(pk=meditation__id)
        except Meditation.DoesNotExist:
            logger.error(f"Meditation with id {meditation__id} not found!")
            return None

    @staticmethod
    def delete_meditation_by_id(meditation__id: int) -> None:
        try:
            Meditation.objects.get(pk=meditation__id).delete()
        except Meditation.DoesNotExist:
            logger.error(f"Meditation with id {meditation__id} not found!")

    @staticmethod
    def get_all_meditations() -> List[Meditation]:
        return Meditation.objects.all()

    @staticmethod
    def get_meditations_by_meditation_theme(
        meditation_theme: MeditationTheme,
    ) -> List[Meditation]:
        return Meditation.objects.filter(meditation_theme_id=meditation_theme)

    @staticmethod
    def get_meditations_by_meditation_narrator(
        meditation_narrator: MeditationNarrator,
    ) -> List[Meditation]:
        return Meditation.objects.filter(
            meditation_narrator=meditation_narrator
        )

    @staticmethod
    def create_meditation_session(
        user: UserInfo, meditation: Meditation
    ) -> MeditationSession:
        return MeditationSession.objects.create(
            user_id=user, meditation_id=meditation
        )

    @staticmethod
    def get_meditation_session_by_id(
        meditation_session_id: int,
    ) -> MeditationSession | None:
        try:
            return MeditationSession.objects.get(pk=meditation_session_id)
        except MeditationSession.DoesNotExist:
            logger.error(
                f"MeditationSession with id {meditation_session_id} not found!"
            )

    @staticmethod
    def end_meditation_session(
        meditation_session: MeditationSession,
    ) -> MeditationSession:
        meditation_session.end_session = datetime.now()
        meditation_session.save()
        return meditation_session

    @staticmethod
    def get_meditation_sessions_of_user(user: User) -> List[MeditationSession]:
        return MeditationSession.objects.filter(user=user)

    @staticmethod
    def get_meditation_sessions_of_meditation(
        meditation: Meditation,
    ) -> List[MeditationSession]:
        return MeditationSession.objects.filter(meditation_id=meditation)

    @staticmethod
    def get_all_meditation_sessions():
        return MeditationSession.objects.all()

    @staticmethod
    def create_meditation_grade(
        user: UserInfo, meditation: Meditation, grade: int
    ) -> MeditationGrade:
        return MeditationGrade.objects.create(
            user_id=user, meditation_id=meditation, grade=grade
        )

    @staticmethod
    def delete_meditation_grade(
        user: UserInfo, meditation: Meditation
    ) -> None:
        return MeditationGrade.objects.delete(user=user, meditation=meditation)

    @staticmethod
    def get_meditation_grades_of_user(user: UserInfo) -> List[MeditationGrade]:
        return MeditationGrade.objects.filter(user_id=user)

    @staticmethod
    def get_meditation_grades_of_meditation(
        meditation: Meditation,
    ) -> List[MeditationGrade]:
        return MeditationGrade.objects.filter(meditation_id=meditation)
