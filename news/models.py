from django.db import models
from django.conf import settings
from django.utils import timezone


class NewsEvent(models.Model):
    EVENT_TYPES = [
        ('news', 'News'),
        ('event', 'Event'),
        ('holiday', 'Holiday'),
        ('exam', 'Exam Timetable'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    event_date = models.DateField(null=True, blank=True)

    # Image upload for banners
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)

    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_news'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For exam countdown
    countdown_days = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def days_until(self):
        if self.event_date:
            delta = self.event_date - timezone.now().date()
            return delta.days
        return None

    class Meta:
        ordering = ['-created_at']