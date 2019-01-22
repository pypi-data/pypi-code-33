# Generated by Django 2.1 on 2018-10-06 22:53

import ambition_subject.managers
import ambition_subject.models.subject_requisition
from django.db import migrations, models
import django.db.models.deletion
import edc_identifier.managers
import edc_visit_tracking.managers


class Migration(migrations.Migration):

    dependencies = [
        ('edc_action_item', '0011_auto_20181009_2236'),
        ('ambition_subject', '0020_auto_20180906_0750'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='bloodresult',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='education',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='educationhoh',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='followup',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='lumbarpuncturecsf',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='medicalexpenses',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='medicalexpensestwo',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='microbiology',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='patienthistory',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='pkpdcrf',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='radiology',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='subjectreconsent',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_identifier.managers.SubjectIdentifierManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='subjectrequisition',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', ambition_subject.models.subject_requisition.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='week16',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='week2',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='week4',
            managers=[
                ('on_site', ambition_subject.managers.CurrentSiteManager()),
                ('objects', edc_visit_tracking.managers.CrfModelManager()),
            ],
        ),
        migrations.RenameField(
            model_name='bloodresult',
            old_name='parent_reference_identifier',
            new_name='parent_action_identifier',
        ),
        migrations.RenameField(
            model_name='bloodresult',
            old_name='related_reference_identifier',
            new_name='related_action_identifier',
        ),
        migrations.RenameField(
            model_name='historicalbloodresult',
            old_name='parent_reference_identifier',
            new_name='parent_action_identifier',
        ),
        migrations.RenameField(
            model_name='historicalbloodresult',
            old_name='related_reference_identifier',
            new_name='related_action_identifier',
        ),
        migrations.RenameField(
            model_name='historicalsubjectreconsent',
            old_name='parent_reference_identifier',
            new_name='parent_action_identifier',
        ),
        migrations.RenameField(
            model_name='historicalsubjectreconsent',
            old_name='related_reference_identifier',
            new_name='related_action_identifier',
        ),
        migrations.RenameField(
            model_name='subjectreconsent',
            old_name='parent_reference_identifier',
            new_name='parent_action_identifier',
        ),
        migrations.RenameField(
            model_name='subjectreconsent',
            old_name='related_reference_identifier',
            new_name='related_action_identifier',
        ),
        migrations.AddField(
            model_name='bloodresult',
            name='action_item',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to='edc_action_item.ActionItem'),
        ),
        migrations.AddField(
            model_name='historicalbloodresult',
            name='action_item',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='edc_action_item.ActionItem'),
        ),
        migrations.AddField(
            model_name='historicalsubjectreconsent',
            name='action_item',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='edc_action_item.ActionItem'),
        ),
        migrations.AddField(
            model_name='subjectreconsent',
            name='action_item',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to='edc_action_item.ActionItem'),
        ),
        migrations.AlterField(
            model_name='bloodresult',
            name='action_identifier',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalbloodresult',
            name='action_identifier',
            field=models.CharField(null=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='historicalsubjectreconsent',
            name='action_identifier',
            field=models.CharField(null=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='subjectreconsent',
            name='action_identifier',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
