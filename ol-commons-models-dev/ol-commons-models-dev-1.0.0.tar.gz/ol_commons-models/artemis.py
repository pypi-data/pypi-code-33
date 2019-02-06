from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
base = declarative_base()


class Activity(db.Model):
    __tablename__ = 'activity'
    sq_activity_id = db.Sequence('sq_activity_id', metadata=base.metadata)
    num_activity_id = db.Column(db.Numeric, sq_activity_id, server_default=sq_activity_id.next_value(),
                                primary_key=True)
    str_act_description = db.Column(db.Text, nullable=False)
    num_registered_hours = db.Column(db.Numeric)
    num_registered_minutes = db.Column(db.Numeric)
    num_resource_id = db.Column(db.Numeric)
    num_task_id = db.Column(db.Numeric, db.ForeignKey("task.num_task_id"), nullable=False)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    dte_activitydate = db.Column(db.Date)


class Assignment(db.Model):
    __tablename__ = 'assignment'
    num_task_id = db.Column(db.Numeric, db.ForeignKey("task.num_task_id"), nullable=False, primary_key=True)
    num_prjteam_id = db.Column(db.Numeric, db.ForeignKey("project_team.num_prjteam_id"), nullable=False,
                               primary_key=True)
    str_assigment_rol = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)


class Comment(db.Model):
    __tablename__ = 'comment'

    sq_comment_id = db.Sequence('sq_comment_id', metadata=base.metadata)

    num_comment_id = db.Column(db.Numeric, sq_comment_id, server_default=sq_comment_id.next_value(), primary_key=True)
    str_comment_description = db.Column(db.Text)
    num_resource_id = db.Column(db.Numeric)
    num_task_id = db.Column(db.Numeric)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)


class Task(db.Model):
    __tablename__ = 'task'
    sq_task_id = Sequence('sq_task_id', metadata=base.metadata)
    num_task_id = db.Column(db.Numeric, sq_task_id, server_default=sq_task_id.next_value(), primary_key=True)
    str_taskname = db.Column(db.Text)
    num_time_expected = db.Column(db.Numeric)
    num_project_id = db.Column(db.Numeric, db.ForeignKey("project.num_project_id"), nullable=False)
    num_parent_id = db.Column(db.Numeric)
    dte_task_estinidate = db.Column(db.DateTime)
    dte_task_estenddate = db.Column(db.DateTime)
    dte_task_realinidate = db.Column(db.DateTime)
    dte_task_realendate = db.Column(db.DateTime)
    num_task_status = db.Column(db.Numeric)
    num_tsktype_id = db.Column(db.Numeric)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)


class Project(db.Model):
    __tablename__ = 'project'

    sq_project_id = Sequence('sq_project_id', metadata=base.metadata)
    num_project_id = db.Column(db.Numeric, sq_project_id, server_default=sq_project_id.next_value(), primary_key=True)
    str_project_cod = db.Column(db.String, nullable=False)
    str_project_name = db.Column(db.Text, nullable=False)
    str_description = db.Column(db.Text)
    str_short_description = db.Column(db.Text)
    num_cost = db.Column(db.Numeric)
    num_project_status = db.Column(db.Numeric)
    dte_initial_date = db.Column(db.DATE)
    dte_end_date = db.Column(db.DATE)
    num_prjtype_id = db.Column(db.Numeric)
    num_pchorder_id = db.Column(db.Numeric)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)


class TaskLink(db.Model):
    __tablename__ = 'task_link'
    num_tsklink_id = db.Column(db.Numeric, primary_key=True)
    num_task_idsource = db.Column(db.Numeric)
    num_task_idtarget = db.Column(db.Numeric)
    num_tsklink_status = db.Column(db.Numeric)
    str_tsklink_type = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)


class ProjectTeam(db.Model):
    __tablename__ = 'project_team'

    sq_prjteam_id = Sequence('sq_prjteam_id', metadata=base.metadata)

    num_prjteam_id = db.Column(db.Numeric, sq_prjteam_id, server_default=sq_prjteam_id.next_value(), primary_key=True)
    num_project_id = db.Column(db.Numeric, db.ForeignKey("project.num_project_id"), nullable=False)
    num_resource_id = db.Column(db.Numeric)
    num_prjteam_costperhour = db.Column(db.Numeric)
    num_prjteam_hourestimated = db.Column(db.Numeric)
    str_resource_name = db.Column(db.Text)
    str_resource_type = db.Column(db.Text)
    str_resource_rol = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    dte_modifieddate = db.Column(db.DateTime)


class ProjectWrktime(db.Model):
    __tablename__ = 'project_wrktime'
    sq_prjwrktime_id = Sequence('sq_prjwrktime_id', metadata=base.metadata)
    num_prjwrktime_id = db.Column(db.Numeric, sq_prjwrktime_id, server_default=sq_prjwrktime_id.next_value(),
                                  primary_key=True)
    num_prjwrktime_minhour = db.Column(db.Numeric)
    num_prjwrktime_maxhour = db.Column(db.Numeric)
    num_prjwrktime_status = db.Column(db.Numeric)
    num_project_id = db.Column(db.Numeric, db.ForeignKey("project.num_project_id"), nullable=False)
    num_prjwrktime_day = db.Column(db.Numeric)
