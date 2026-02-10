from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ad")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Mövzu")
    message = models.TextField(verbose_name="Mesaj")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name="Oxunub")

    def __str__(self):
        return f"{self.name} - {self.subject}"