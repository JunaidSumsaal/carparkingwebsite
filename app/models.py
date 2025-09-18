from django.db import models

class DetectionResult(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    occupied = models.IntegerField()
    available = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.timestamp} | Occ: {self.occupied}, Avail: {self.available}"


class Registration(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)  # store hashed passwords

    def __str__(self):
        return self.username


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest first
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
    


class UserFeedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedback"

    def __str__(self):
        return f"{self.name} ({self.email}) – {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} ({self.email}) at {self.submitted_at:%Y-%m-%d %H:%M}"        