from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name="Vəzifə")
    department = models.CharField(max_length=100, verbose_name="Şöbə")
    location = models.CharField(max_length=100, default="Bakı ofisi", verbose_name="Məkan")
    description = models.TextField(verbose_name="Təsvir")
    is_active = models.BooleanField(default=True, verbose_name="Aktivdir")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Vakansiya"
        verbose_name_plural = "Vakansiyalar"


class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    cover_letter = models.TextField(blank=True)
    cv = models.FileField(upload_to='cvs/')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} — {self.vacancy.title}"
