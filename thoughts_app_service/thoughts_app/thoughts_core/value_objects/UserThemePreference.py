from ..models import UserInfo, MeditationTheme


class UserThemePreference:
    def __init__(self, user: UserInfo):
        self.user = user
        self.theme_to_grades = dict()
        self.total_grades = 0

    def add_grade(self, meditation_theme: MeditationTheme, grade: int):
        self.total_grades += 1
        if meditation_theme in self.theme_to_grades:
            self.theme_to_grades[meditation_theme].append(grade)
        else:
            self.theme_to_grades[meditation_theme] = [grade]

