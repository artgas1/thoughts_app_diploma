from django.contrib import admin

from .models import (
    Achievement,
    MeditationSession,
    MeditationNarrator,
    MeditationGrade,
    MeditationTheme,
    Meditation,
    Chat,
    UserInfo,
)

admin.site.register(UserInfo)
admin.site.register(Achievement)
admin.site.register(MeditationTheme)
admin.site.register(MeditationSession)
admin.site.register(Meditation)
admin.site.register(Chat)
admin.site.register(MeditationNarrator)
admin.site.register(MeditationGrade)
