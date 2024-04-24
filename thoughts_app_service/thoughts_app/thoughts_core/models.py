from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
import uuid


class Achievement(models.Model):
    name = models.CharField(max_length=255)
    cover_file_name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f'Achievement: {self.name}'


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    achievements = models.ManyToManyField(Achievement, blank=True)

    def __str__(self):
        return f'UserInfo: {self.name}'


class MeditationTheme(models.Model):
    name = models.CharField(max_length=255)
    cover_file_name = models.CharField(max_length=255)

    def __str__(self):
        return f'Meditation theme: {self.name}'


class MeditationNarrator(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'MeditationNarrator: {self.name}'


class Meditation(models.Model):
    name = models.CharField(max_length=255)
    meditation_theme_id = models.ForeignKey(
        to=MeditationTheme, on_delete=models.SET_NULL, null=True
    )
    meditation_narrator_id = models.ForeignKey(
        to=MeditationNarrator, on_delete=models.SET_NULL, null=True
    )
    audio_file_name = models.CharField(max_length=255)
    cover_file_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Meditation: {self.name}"


class MeditationSession(models.Model):
    user_id = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    meditation_id = models.ForeignKey(to=Meditation, on_delete=models.CASCADE)
    session_start_time = models.DateTimeField(auto_now_add=True)
    end_session = models.DateTimeField(null=True)


class MeditationGrade(models.Model):
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    meditation_id = models.ForeignKey(to=Meditation, on_delete=models.CASCADE)
    grade = models.IntegerField()

    def __str__(self):
        return f'MeditationGrade from {self.user_id} for {self.meditation_id} = {self.grade}'


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
