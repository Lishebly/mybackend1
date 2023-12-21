# models.py

from django.db import models
from django.utils import timezone

class CustomUser(models.Model):
    avatar = models.URLField(blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    openid = models.CharField(max_length=50, unique=True, blank=True, null=True)


class Task(models.Model):
    # 任务模型
    TASK_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    title=models.TextField()
    description = models.TextField()
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    publish_time = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    ex_phone_number = models.CharField(max_length=15, blank=True)
    last_chat_time = models.DateTimeField(null=True, blank=True)  # 上一次聊天时间


class BaseMessage(models.Model):
    CREATOR = 'creator'
    ASSIGNEE = 'assignee'

    SENDER_CHOICES = [
        (CREATOR, 'Creator'),
        (ASSIGNEE, 'Assignee'),
    ]

    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# models.py


class TaskMessage(BaseMessage):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='messages')
