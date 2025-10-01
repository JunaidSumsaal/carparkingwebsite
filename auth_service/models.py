from django.db import models

class Registration(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)  # 🔒 better: hashed password

    def __str__(self):
        return self.username
