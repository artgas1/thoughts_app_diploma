from typing import List

from math import floor

from .MeditationService import MeditationService
from .logger import logger
from ..models import UserInfo, Meditation
from ..value_objects.UserThemePreference import UserThemePreference

AMOUNT_OF_MEDITATIONS_TO_RECOMMEND = 10


class RecommendationService:
    @staticmethod
    def recommend_meditations_for_user(user: UserInfo) -> List[Meditation]:
        user_session = MeditationService.get_user_meditation_session(user=user)
        if len(user_session) < 5:
            logger.info(f"Not enough sessions for recommendation for user {user}")
            return MeditationService.get_random_meditations(amount=10)

        meditation_theme_to_amount_of_meditations = (
            RecommendationService.analyze_user_grades(user=user)
        )
        if not meditation_theme_to_amount_of_meditations:
            logger.info(f"Not enough grades for recommendation for user {user}")
            return MeditationService.get_random_meditations(amount=10)

        recommended_meditations = []
        for (
            meditation_theme,
            amount_of_meditations,
        ) in meditation_theme_to_amount_of_meditations:
            recommended_meditations += (
                MeditationService.get_meditations_by_meditation_theme(
                    meditation_theme=meditation_theme
                )
            )
        logger.info(f"recommended_meditations: {recommended_meditations}")
        return recommended_meditations

    @staticmethod
    def analyze_user_grades(user: UserInfo) -> List[tuple] | None:
        user_theme_preference = UserThemePreference(user=user)
        user_grades = MeditationService.get_user_grades(user=user)
        for user_grade in user_grades:
            meditation_theme = user_grade.meditation_id.meditation_theme_id
            user_theme_preference.add_grade(
                meditation_theme=meditation_theme, grade=user_grade.grade
            )

        logger.info(f"User total grades: {user_theme_preference.total_grades}")
        if user_theme_preference.total_grades < 5:
            return None

        meditation_theme_grade = RecommendationService.get_result_of_analysis(
            user_theme_preference
        )

        # Фильтруем темы с рейтингом ниже 4
        meditation_theme_grade_filtered = [
            (theme, rating) for theme, rating in meditation_theme_grade if rating >= 4.0
        ]

        # Вычисляем пропорциональное количество медитаций для каждой темы
        meditations_per_theme = [
            floor(
                AMOUNT_OF_MEDITATIONS_TO_RECOMMEND
                * rating
                / sum(rating for _, rating in meditation_theme_grade_filtered)
            )
            for _, rating in meditation_theme_grade_filtered
        ]

        meditation_name_to_amount_of_meditations = []
        for i in range(len(meditation_theme_grade_filtered)):
            meditation_name_to_amount_of_meditations.append(
                (meditation_theme_grade_filtered[i][0], meditations_per_theme[i])
            )

        logger.info(
            f"meditation_name_to_amount_of_meditations: {meditation_name_to_amount_of_meditations}"
        )
        return meditation_name_to_amount_of_meditations

    @staticmethod
    def get_result_of_analysis(
        user_theme_preference: UserThemePreference,
    ) -> List[tuple]:
        meditation_theme_grade = []
        for theme in user_theme_preference.theme_to_grades.keys():
            meditation_theme_grade.append(
                (
                    theme,
                    sum(user_theme_preference.theme_to_grades[theme])
                    / len(user_theme_preference.theme_to_grades[theme]),
                )
            )

        return meditation_theme_grade
