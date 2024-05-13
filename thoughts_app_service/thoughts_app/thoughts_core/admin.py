from django.contrib import admin

from .models import (
    Achievement,
    Chat,
    Meditation,
    MeditationGrade,
    MeditationNarrator,
    MeditationSession,
    MeditationTheme,
    ProgressLevel,
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
admin.site.register(ProgressLevel)
