from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_farm_name_alter_customuser_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('farmer', '👨‍🌾 Fermer'),
                    ('expert', '👨‍🔬 Mütəxəssis'),
                    ('guest', '👋 Qonaq'),
                    ('admin', '👨‍💼 Admin'),
                ],
                default='guest',
                verbose_name='Rol'
            ),
        ),
    ]
