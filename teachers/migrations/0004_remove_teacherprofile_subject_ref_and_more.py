from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0003_alter_graderecord_unique_together_and_more'),
        ('teachers', '0003_teacherprofile_subject_ref'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacherprofile',
            name='subject',
        ),
        migrations.RenameField(
            model_name='teacherprofile',
            old_name='subject_ref',
            new_name='subject',
        ),
        migrations.AlterField(
            model_name='teacherprofile',
            name='subject',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='teacher_profiles',
                to='academics.subject',
            ),
        ),
    ]
