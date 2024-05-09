from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import uuid


class Achievement(models.Model):
    name = models.CharField(max_length=255)
    cover_file_url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return f"Achievement: {self.name}"


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    achievements = models.ManyToManyField(
        Achievement, through="UserAchievement", blank=True
    )

    def __str__(self):
        return f"UserInfo: {self.name}"


class UserAchievement(models.Model):
    user_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user_info", "achievement")  # Ensuring uniqueness

    def __str__(self):
        return f"{self.user_info} - {self.achievement}"


class MeditationTheme(models.Model):
    name = models.CharField(max_length=255)
    cover_file_url = models.URLField()

    def __str__(self):
        return f"Meditation theme: {self.name}"


class MeditationNarrator(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"MeditationNarrator: {self.name}"


class Meditation(models.Model):
    name = models.CharField(max_length=255)
    meditation_theme = models.ForeignKey(
        MeditationTheme, on_delete=models.SET_NULL, null=True
    )
    meditation_narrator = models.ForeignKey(
        MeditationNarrator, on_delete=models.SET_NULL, null=True
    )
    audio_file_url = models.URLField()
    cover_file_url = models.URLField()

    def __str__(self):
        return f"Meditation: {self.name}"


class MeditationSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meditation = models.ForeignKey(Meditation, on_delete=models.CASCADE)
    session_start_time = models.DateTimeField(auto_now_add=True)


class MeditationGrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meditation = models.ForeignKey(Meditation, on_delete=models.CASCADE)
    grade = models.IntegerField()

    def __str__(self):
        return f"MeditationGrade from {self.user} for {self.meditation} = {self.grade}"


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
