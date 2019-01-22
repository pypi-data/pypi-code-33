# Generated by Django 2.1.2 on 2018-11-12 21:39

import _socket
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_revision.revision_field
import edc_base.model_validators.date
import edc_base.utils
import edc_model_fields.fields.hostname_modification_field
import edc_model_fields.fields.other_charfield
import edc_model_fields.fields.userfield
import edc_model_fields.fields.uuid_auto_field
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ambition_lists', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ambition_prn', '0013_auto_20181108_0353'),
    ]

    operations = [
        migrations.CreateModel(
            name='AmphotericinMissedDoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('day_missed', models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2'), (3, 'Day 3'), (4, 'Day 4'), (5, 'Day 5'), (6, 'Day 6'), (7, 'Day 7'), (8, 'Day 8'), (9, 'Day 9'), (10, 'Day 10'), (11, 'Day 11'), (12, 'Day 12'), (13, 'Day 13'), (14, 'Day 14')], verbose_name='Day missed:')),
                ('missed_reason', models.CharField(blank=True, choices=[('toxicity', 'Toxicity'), ('missed', 'Missed'), ('refused', 'Refused'), ('not_required', 'Not required according to protocol'), ('OTHER', 'Other')], max_length=25, verbose_name='Reason:')),
                ('missed_reason_other', edc_model_fields.fields.other_charfield.OtherCharField(blank=True, max_length=35, null=True, verbose_name='If Other, specify ...')),
            ],
            options={
                'verbose_name_plural': 'Amphotericin Missed Doses',
            },
        ),
        migrations.CreateModel(
            name='FluconazoleMissedDoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('day_missed', models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2'), (3, 'Day 3'), (4, 'Day 4'), (5, 'Day 5'), (6, 'Day 6'), (7, 'Day 7'), (8, 'Day 8'), (9, 'Day 9'), (10, 'Day 10'), (11, 'Day 11'), (12, 'Day 12'), (13, 'Day 13'), (14, 'Day 14')], verbose_name='Day missed:')),
                ('missed_reason', models.CharField(blank=True, choices=[('toxicity', 'Toxicity'), ('missed', 'Missed'), ('refused', 'Refused'), ('not_required', 'Not required according to protocol'), ('OTHER', 'Other')], max_length=25, verbose_name='Reason:')),
                ('missed_reason_other', edc_model_fields.fields.other_charfield.OtherCharField(blank=True, max_length=35, null=True, verbose_name='If Other, specify ...')),
            ],
            options={
                'verbose_name_plural': 'Fluconazole Missed Doses',
            },
        ),
        migrations.CreateModel(
            name='FlucytosineMissedDoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('day_missed', models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2'), (3, 'Day 3'), (4, 'Day 4'), (5, 'Day 5'), (6, 'Day 6'), (7, 'Day 7'), (8, 'Day 8'), (9, 'Day 9'), (10, 'Day 10'), (11, 'Day 11'), (12, 'Day 12'), (13, 'Day 13'), (14, 'Day 14')], verbose_name='Day missed:')),
                ('missed_reason', models.CharField(blank=True, choices=[('toxicity', 'Toxicity'), ('missed', 'Missed'), ('refused', 'Refused'), ('not_required', 'Not required according to protocol'), ('OTHER', 'Other')], max_length=25, verbose_name='Reason:')),
                ('missed_reason_other', edc_model_fields.fields.other_charfield.OtherCharField(blank=True, max_length=35, null=True, verbose_name='If Other, specify ...')),
                ('doses_missed', models.IntegerField(choices=[(1, '1 Dose'), (2, '2 Doses'), (3, '3 Doses'), (4, '4 Doses')], verbose_name='Doses missed:')),
            ],
            options={
                'verbose_name_plural': 'Flucytosine Missed Doses',
            },
        ),
        migrations.CreateModel(
            name='HistoricalAmphotericinMissedDoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, db_index=True, editable=False, help_text='System auto field. UUID primary key.')),
                ('day_missed', models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2'), (3, 'Day 3'), (4, 'Day 4'), (5, 'Day 5'), (6, 'Day 6'), (7, 'Day 7'), (8, 'Day 8'), (9, 'Day 9'), (10, 'Day 10'), (11, 'Day 11'), (12, 'Day 12'), (13, 'Day 13'), (14, 'Day 14')], verbose_name='Day missed:')),
                ('missed_reason', models.CharField(blank=True, choices=[('toxicity', 'Toxicity'), ('missed', 'Missed'), ('refused', 'Refused'), ('not_required', 'Not required according to protocol'), ('OTHER', 'Other')], max_length=25, verbose_name='Reason:')),
                ('missed_reason_other', edc_model_fields.fields.other_charfield.OtherCharField(blank=True, max_length=35, null=True, verbose_name='If Other, specify ...')),
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical amphotericin missed doses',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalFluconazoleMissedDoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, db_index=True, editable=False, help_text='System auto field. UUID primary key.')),
                ('day_missed', models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2'), (3, 'Day 3'), (4, 'Day 4'), (5, 'Day 5'), (6, 'Day 6'), (7, 'Day 7'), (8, 'Day 8'), (9, 'Day 9'), (10, 'Day 10'), (11, 'Day 11'), (12, 'Day 12'), (13, 'Day 13'), (14, 'Day 14')], verbose_name='Day missed:')),
                ('missed_reason', models.CharField(blank=True, choices=[('toxicity', 'Toxicity'), ('missed', 'Missed'), ('refused', 'Refused'), ('not_required', 'Not required according to protocol'), ('OTHER', 'Other')], max_length=25, verbose_name='Reason:')),
                ('missed_reason_other', edc_model_fields.fields.other_charfield.OtherCharField(blank=True, max_length=35, null=True, verbose_name='If Other, specify ...')),
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical fluconazole missed doses',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalFlucytosineMissedDoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, db_index=True, editable=False, help_text='System auto field. UUID primary key.')),
                ('day_missed', models.IntegerField(choices=[(1, 'Day 1'), (2, 'Day 2'), (3, 'Day 3'), (4, 'Day 4'), (5, 'Day 5'), (6, 'Day 6'), (7, 'Day 7'), (8, 'Day 8'), (9, 'Day 9'), (10, 'Day 10'), (11, 'Day 11'), (12, 'Day 12'), (13, 'Day 13'), (14, 'Day 14')], verbose_name='Day missed:')),
                ('missed_reason', models.CharField(blank=True, choices=[('toxicity', 'Toxicity'), ('missed', 'Missed'), ('refused', 'Refused'), ('not_required', 'Not required according to protocol'), ('OTHER', 'Other')], max_length=25, verbose_name='Reason:')),
                ('missed_reason_other', edc_model_fields.fields.other_charfield.OtherCharField(blank=True, max_length=35, null=True, verbose_name='If Other, specify ...')),
                ('doses_missed', models.IntegerField(choices=[(1, '1 Dose'), (2, '2 Doses'), (3, '3 Doses'), (4, '4 Doses')], verbose_name='Doses missed:')),
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical flucytosine missed doses',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSignificantDiagnoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, db_index=True, editable=False, help_text='System auto field. UUID primary key.')),
                ('possible_diagnoses', models.CharField(blank=True, choices=[('pulmonary_tb', 'Pulmonary TB'), ('extra_pulmonary_tb', 'Extra-pulmonary TB'), ('kaposi_sarcoma', 'Kaposi-sarcoma'), ('malaria', 'Malaria'), ('bacteraemia', 'Bacteraemia'), ('pneumonia', 'Pneumonia'), ('diarrhoeal_wasting', 'Diarrhoeal wasting'), ('OTHER', 'Other')], max_length=25, null=True, verbose_name='Significant diagnoses:')),
                ('dx_date', models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Date of diagnosis:')),
                ('dx_other', models.CharField(blank=True, max_length=50, null=True, verbose_name='If other, please specify:')),
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Significant Diagnosis',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='SignificantDiagnoses',
            fields=[
                ('created', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('modified', models.DateTimeField(blank=True, default=edc_base.utils.get_utcnow)),
                ('user_created', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user created')),
                ('user_modified', edc_model_fields.fields.userfield.UserField(blank=True, help_text='Updated by admin.save_model', max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(blank=True, default=_socket.gethostname, help_text='System field. (modified on create only)', max_length=60)),
                ('hostname_modified', edc_model_fields.fields.hostname_modification_field.HostnameModificationField(blank=True, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('device_created', models.CharField(blank=True, max_length=10)),
                ('device_modified', models.CharField(blank=True, max_length=10)),
                ('id', edc_model_fields.fields.uuid_auto_field.UUIDAutoField(blank=True, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('possible_diagnoses', models.CharField(blank=True, choices=[('pulmonary_tb', 'Pulmonary TB'), ('extra_pulmonary_tb', 'Extra-pulmonary TB'), ('kaposi_sarcoma', 'Kaposi-sarcoma'), ('malaria', 'Malaria'), ('bacteraemia', 'Bacteraemia'), ('pneumonia', 'Pneumonia'), ('diarrhoeal_wasting', 'Diarrhoeal wasting'), ('OTHER', 'Other')], max_length=25, null=True, verbose_name='Significant diagnoses:')),
                ('dx_date', models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Date of diagnosis:')),
                ('dx_other', models.CharField(blank=True, max_length=50, null=True, verbose_name='If other, please specify:')),
            ],
            options={
                'verbose_name': 'Significant Diagnosis',
                'verbose_name_plural': 'Significant Diagnoses',
            },
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='ambi_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ambisome treatment duration:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='ambi_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Ambisome start date:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='ambi_stop_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Ambisome end date:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='ampho_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Amphotericin B treatment duration'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='ampho_end_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Amphotericin B end date: '),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='ampho_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Amphotericin B start date: '),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='antibiotic_other',
            field=models.TextField(blank=True, null=True, verbose_name='If other antibiotics, please specify:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='drug_intervention_other',
            field=models.TextField(blank=True, null=True, verbose_name='If other, please specify:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='flucon_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Fluconazole treatment duration:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='flucon_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Fluconazole start date:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='flucon_stop_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Fluconazole end date:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='flucy_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Flucytosine treatment duration:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='flucy_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Flucytosine start date:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='flucy_stop_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Flucytosine end date:'),
        ),
        migrations.AddField(
            model_name='historicalstudyterminationconclusion',
            name='medicine_other',
            field=models.TextField(blank=True, null=True, verbose_name='If other, please specify:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='ambi_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Ambisome treatment duration:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='ambi_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Ambisome start date:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='ambi_stop_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Ambisome end date:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='ampho_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Amphotericin B treatment duration'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='ampho_end_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Amphotericin B end date: '),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='ampho_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Amphotericin B start date: '),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='antibiotic',
            field=models.ManyToManyField(blank=True, to='ambition_lists.Antibiotic', verbose_name='Were any of the following antibiotics given?'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='antibiotic_other',
            field=models.TextField(blank=True, null=True, verbose_name='If other antibiotics, please specify:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='drug_intervention',
            field=models.ManyToManyField(to='ambition_lists.OtherDrug', verbose_name='Other drugs/interventions given during first 14 days'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='drug_intervention_other',
            field=models.TextField(blank=True, null=True, verbose_name='If other, please specify:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='flucon_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Fluconazole treatment duration:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='flucon_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Fluconazole start date:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='flucon_stop_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Fluconazole end date:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='flucy_duration',
            field=models.IntegerField(blank=True, null=True, verbose_name='Flucytosine treatment duration:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='flucy_start_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Flucytosine start date:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='flucy_stop_date',
            field=models.DateField(blank=True, null=True, validators=[edc_base.model_validators.date.date_not_future], verbose_name='Flucytosine end date:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='medicine_other',
            field=models.TextField(blank=True, null=True, verbose_name='If other, please specify:'),
        ),
        migrations.AddField(
            model_name='studyterminationconclusion',
            name='medicines',
            field=models.ManyToManyField(to='ambition_lists.Day14Medication', verbose_name='Medicines on study termination day:'),
        ),
        migrations.AddField(
            model_name='significantdiagnoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='historicalsignificantdiagnoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='historicalflucytosinemisseddoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='historicalfluconazolemisseddoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='historicalamphotericinmisseddoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='flucytosinemisseddoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='fluconazolemisseddoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AddField(
            model_name='amphotericinmisseddoses',
            name='study_termination_conclusion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ambition_prn.StudyTerminationConclusion'),
        ),
        migrations.AlterUniqueTogether(
            name='significantdiagnoses',
            unique_together={('study_termination_conclusion', 'possible_diagnoses', 'dx_date', 'dx_other')},
        ),
        migrations.AlterUniqueTogether(
            name='flucytosinemisseddoses',
            unique_together={('study_termination_conclusion', 'day_missed')},
        ),
        migrations.AlterUniqueTogether(
            name='fluconazolemisseddoses',
            unique_together={('study_termination_conclusion', 'day_missed')},
        ),
        migrations.AlterUniqueTogether(
            name='amphotericinmisseddoses',
            unique_together={('study_termination_conclusion', 'day_missed')},
        ),
    ]
