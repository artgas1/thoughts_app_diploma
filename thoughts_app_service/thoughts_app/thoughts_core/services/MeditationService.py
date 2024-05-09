import random
from typing import List

from ..models import (
    MeditationSession,
    UserInfo,
    Meditation,
    MeditationGrade,
    MeditationTheme,
)
from ..repositories.MeditationRepository import MeditationRepository


class MeditationService:
    @staticmethod
    def end_meditation_session(
        meditation_session: MeditationSession,
    ) -> MeditationSession | None:
        return MeditationRepository.end_meditation_session(
            meditation_session=meditation_session
        )

    @staticmethod
    def get_user_meditation_session(user: UserInfo):
        return MeditationRepository.get_meditation_sessions_of_user(user)

    @staticmethod
    def get_meditations_by_meditation_theme(
        meditation_theme: MeditationTheme,
    ) -> List[Meditation]:
        return MeditationRepository.get_meditations_by_meditation_theme(
            meditation_theme=meditation_theme
        )

    @staticmethod
    def get_random_meditations(amount: int) -> List[Meditation]:
        meditations = MeditationRepository.get_all_meditations()
        if amount >= len(meditations):
            return meditations

        return random.sample(meditations, amount)

    @staticmethod
    def get_user_grades(user: UserInfo) -> List[MeditationGrade]:
        return MeditationRepository.get_meditation_grades_of_user(user=user)
