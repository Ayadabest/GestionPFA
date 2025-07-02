from django.db import migrations

def update_admin_role(apps, schema_editor):
    User = apps.get_model('users', 'User')
    admin = User.objects.get(username='aya')
    admin.role = 'admin'
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_studentprofile_phone_alter_studentprofile_department_and_more'),
    ]

    operations = [
        migrations.RunPython(update_admin_role),
    ] 