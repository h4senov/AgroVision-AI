from django.db import models

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Başlıq")
    slug = models.SlugField(unique=True, verbose_name="Link (Slug)")
    image = models.ImageField(upload_to='news/', verbose_name="Şəkil")
    content = models.TextField(verbose_name="Məzmun")
    is_published = models.BooleanField(default=True, verbose_name="Dərc edilib")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xəbər"
        verbose_name_plural = "Xəbərlər"
        ordering = ['-created_at']

    def __str__(self):
        return self.title