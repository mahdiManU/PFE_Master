"""
Make Diagram.file required.

Earlier migrations (0007-0010) declared the field optional (null=True, blank=True);
models.py later became required without a migration. All existing diagrams
already have a file, so no default value is needed.
"""
from django.db import migrations, models
import myapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_rename_project_id_diagram_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diagram',
            name='file',
            field=models.FileField(upload_to=myapp.models.diagram_directory_path),
        ),
    ]