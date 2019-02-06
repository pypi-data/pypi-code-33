import os
from . import PGPString
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
base = declarative_base()


class Company(db.Model):
    __tablename__ = 'company'
    sq_company_id = Sequence('sq_company_id', metadata=base.metadata)

    num_company_id = db.Column(db.Numeric, sq_company_id, server_default=sq_company_id.next_value(), primary_key=True)
    str_company_name = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    num_company_parent_id = db.Column(db.Numeric)  # , db.ForeignKey("person.num_person_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    str_abbreviation = db.Column(db.Text)
    str_domain = db.Column(db.Text)


class PersonSkill(db.Model):
    __tablename__ = 'person_skill'
    sq_personskill_id = Sequence('sq_personskill_id', metadata=base.metadata)

    num_person_skill_id = db.Column(db.Numeric, sq_personskill_id, server_default=sq_personskill_id.next_value(),
                                    primary_key=True)
    str_skill_type = db.Column(db.Text)
    str_skill_level = db.Column(db.Text)
    str_skill_des = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class PersonReference(db.Model):
    __tablename__ = 'person_reference'
    sq_personreference_id = Sequence('sq_personreference_id', metadata=base.metadata)

    num_per_ref_id = db.Column(db.Numeric, sq_personreference_id, server_default=sq_personreference_id.next_value(),
                               primary_key=True)
    str_per_ref_name = db.Column(db.Text)
    str_dad_last_name = db.Column(db.Text)
    str_mom_last_name = db.Column(db.Text)
    str_per_ref_level = db.Column(db.Text)
    str_per_ref_company = db.Column(db.Text)
    str_per_ref_email = db.Column(db.Text)
    str_per_ref_phone = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class PersonProExperience(db.Model):
    __tablename__ = 'person_pro_experience'
    sq_personproexp_id = Sequence('sq_personproexp_id', metadata=base.metadata)

    num_pro_experience_id = db.Column(db.Numeric, sq_personproexp_id, server_default=sq_personproexp_id.next_value(),
                                      primary_key=True)
    str_pro_experience_company = db.Column(db.Text)
    dte_startdate = db.Column(db.DateTime)
    dte_enddate = db.Column(db.DateTime)
    str_pro_experience_charge = db.Column(db.Text)
    str_pro_experience_des = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class PersonEducationCerti(db.Model):
    __tablename__ = 'person_education_certi'
    sq_personeducerti_id = Sequence('sq_personeducerti_id', metadata=base.metadata)

    num_educ_certi_id = db.Column(db.Numeric, sq_personeducerti_id, server_default=sq_personeducerti_id.next_value(),
                                  primary_key=True)
    str_year = db.Column(db.Text)
    str_month = db.Column(db.Text)
    str_educ_certi_name = db.Column(db.Text)
    str_institute = db.Column(db.Text)
    str_educ_certi_des = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class PersonEducation(db.Model):
    __tablename__ = 'person_education'
    sq_personedu_id = Sequence('sq_personedu_id', metadata=base.metadata)

    num_person_education_id = db.Column(db.Numeric, sq_personedu_id, server_default=sq_personedu_id.next_value(),
                                        primary_key=True)
    str_grade_academic = db.Column(db.Text)
    str_institution = db.Column(db.Text)
    str_start_date_educ = db.Column(db.Text)
    str_state_academic = db.Column(db.Text)
    str_end_date_educ = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class EmployeeContract(db.Model):
    __tablename__ = 'employee_contract'
    sq_contract_id = Sequence('sq_contract_id', metadata=base.metadata)

    num_contract_id = db.Column(db.Numeric, sq_contract_id, server_default=sq_contract_id.next_value(),
                                primary_key=True)
    num_employee_id = db.Column(db.Numeric, db.ForeignKey("employee.num_employee_id"), nullable=False)
    str_contract_salary = db.Column(PGPString(os.environ.get('PASS_FOR_ENCRYPT'), length=1000))
    str_contract_salaryperday = db.Column(PGPString(os.environ.get('PASS_FOR_ENCRYPT'), length=1000))
    str_contract_status = db.Column(db.Text)
    dte_contract_begindate = db.Column(db.TIMESTAMP)
    dte_contract_enddate = db.Column(db.TIMESTAMP)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)


class District(db.Model):
    __tablename__ = 'district'

    sq_district_id = Sequence('sq_district _id', metadata=base.metadata)

    str_district_id = db.Column(db.Text, primary_key=True)
    str_district_name = db.Column(db.Text)
    str_district_des = db.Column(db.Text)
    str_province_id = db.Column(db.Text, db.ForeignKey("province.str_province_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)


class Province(db.Model):
    __tablename__ = 'province'

    sq_province_id = Sequence('sq_province_id', metadata=base.metadata)

    str_province_id = db.Column(db.Text, primary_key=True)
    str_province_name = db.Column(db.Text)
    str_province_des = db.Column(db.Text)
    str_region_id = db.Column(db.Text, db.ForeignKey("region.str_region_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)


class Region(db.Model):
    __tablename__ = 'region'

    sq_region_id = Sequence('sq_region_id', metadata=base.metadata)

    str_region_id = db.Column(db.Text, primary_key=True)
    str_region_name = db.Column(db.Text)
    str_region_des = db.Column(db.Text)
    str_country_id = db.Column(db.Text, db.ForeignKey("country.str_country_id"), nullable=False)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)


class Country(db.Model):
    __tablename__ = 'country'

    sq_country_id = Sequence('sq_country_id', metadata=base.metadata)

    str_country_id = db.Column(db.Text, primary_key=True)
    str_country_name = db.Column(db.Text)
    str_country_des = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)


class PersonAddress(db.Model):
    __tablename__ = 'person_address'
    sq_personaddress_id = Sequence('sq_personaddress_id', metadata=base.metadata)

    num_person_address_id = db.Column(db.Numeric, sq_personaddress_id, server_default=sq_personaddress_id.next_value(),
                                      primary_key=True)
    str_district_id = db.Column(db.Text, db.ForeignKey("district.str_district_id"), nullable=False)
    str_decrip_address = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)


class PersonPhone(db.Model):
    __tablename__ = 'person_phone'
    sq_personphone_id = Sequence('sq_personphone_id', metadata=base.metadata)

    num_person_phone_id = db.Column(db.Numeric, sq_personphone_id, server_default=sq_personphone_id.next_value(),
                                    primary_key=True)
    str_number_phone = db.Column(db.Text)
    str_type_phone = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)


class PersonEmail(db.Model):
    __tablename__ = 'person_email'
    sq_personemail_id = Sequence('sq_personemail_id', metadata=base.metadata)
    num_person_email_id = db.Column(db.Numeric, sq_personemail_id, server_default=sq_personemail_id.next_value(),
                                    primary_key=True)
    str_person_email_des = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)


class PersonDocument(db.Model):
    __tablename__ = 'person_document'
    sq_persondocum_id = Sequence('sq_persondocum_id', metadata=base.metadata)

    num_person_document_id = db.Column(db.Numeric, sq_persondocum_id, server_default=sq_persondocum_id.next_value(),
                                       primary_key=True)
    str_doc_type_id = db.Column(db.Text)
    str_num_document = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)
    chr_status = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)


class WorkLicence(db.Model):
    __tablename__ = 'work_licence'
    sq_work_licence_id = Sequence('sq_work_licence_id', metadata=base.metadata)

    num_work_licence_id = db.Column(db.Numeric, sq_work_licence_id, server_default=sq_work_licence_id.next_value(),
                                    primary_key=True)
    num_employee_id = db.Column(db.Text, db.ForeignKey('employee.num_employee_id'), nullable=False)
    str_description = db.Column(db.Text)
    dte_start_date = db.Column(db.TIMESTAMP)
    dte_end_date = db.Column(db.TIMESTAMP)
    str_type_incident = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    str_modifiedby = db.Column(db.Text)
    str_process_status = db.Column(db.Text)
    num_hours = db.Column(db.Numeric)
    str_url_file = db.Column(db.Text)


class Employee(db.Model):
    __tablename__ = 'employee'
    sq_employee_id = Sequence('sq_employee_id', metadata=base.metadata)

    num_employee_id = db.Column(db.Numeric, primary_key=True)
    str_employee_id = db.Column(db.Text)
    num_person_id = db.Column(db.Numeric, db.ForeignKey("person.num_person_id"), nullable=False)
    str_url_cv_english = db.Column(db.Text)
    str_url_cv_spanish = db.Column(db.Text)
    str_charge = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    chr_status = db.Column(db.Text)
    num_company_id = db.Column(db.Numeric, db.ForeignKey("company.num_company_id"), nullable=False)
    str_employee_email = db.Column(db.Text)


class EmployeeEvaluation(db.Model):
    __tablename__ = 'employee_evaluation'

    sq_evaluation_id = Sequence('sq_ evaluation_id', metadata=base.metadata)

    num_eval_id = db.Column(db.Numeric, primary_key=True)
    str_evaluation_year = db.Column(db.String, nullable=False)
    str_evaluation_month = db.Column(db.String, nullable=False)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)
    dte_modifiedby = db.Column(db.TIMESTAMP)


class EvalQuestion(db.Model):
    __tablename__ = 'eval_question'
    sq_question_id = Sequence('sq_question_id', metadata=base.metadata)

    num_question_id = db.Column(db.Numeric, sq_question_id, server_default=sq_question_id.next_value(),
                                primary_key=True)
    str_name = db.Column(db.String)
    chr_status = db.Column(db.Text)
    num_type_id = db.Column(db.Numeric)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    str_modifiedby = db.Column(db.Text)


class ClientContact(db.Model):
    __tablename__ = 'client_contact'
    sq_contact_client_id = Sequence('sq_contact_client_id', metadata=base.metadata)
    num_client_contact_id = db.Column(db.Numeric, sq_contact_client_id,
                                      server_default=sq_contact_client_id.next_value(), primary_key=True)
    num_person_id = db.Column(db.Numeric, db.ForeignKey('person.num_person_id'), nullable=False)
    num_client_id = db.Column(db.Numeric, db.ForeignKey('client.num_client_id'), nullable=False)


class Client(db.Model):
    __tablename__ = 'client'
    sq_client_id = Sequence('sq_client_id', metadata=base.metadata)
    num_client_id = db.Column(db.Numeric, primary_key=True)
    num_company_id = db.Column(db.Numeric, db.ForeignKey('company.num_company_id'), nullable=False)
    str_billing_code = db.Column(db.Text)
    str_client_name = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    str_client_abbr = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    dte_modifieddate = db.Column(db.DateTime)


class Answer(db.Model):
    __tablename__ = 'eval_answer'
    sq_answer_id = Sequence('sq_answer_id', metadata=base.metadata)
    num_answer_id = db.Column(db.Numeric, sq_answer_id, server_default=sq_answer_id.next_value(), primary_key=True)
    num_score_evaluation = db.Column(db.Numeric)
    num_question_id = db.Column(db.Numeric)
    num_supervision_id = db.Column(db.Numeric)
    str_createby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Workcenter(db.Model):
    __tablename__ = 'workcenter'
    sq_workcenter_id = Sequence('sq_workcenter_id', metadata=base.metadata)

    num_workcenter_id = db.Column(db.Numeric, sq_workcenter_id, server_default=sq_workcenter_id.next_value(),
                                  primary_key=True)
    num_company_id = db.Column(db.Numeric, db.ForeignKey('company.num_company_id'))
    str_region_id = db.Column(db.Text, db.ForeignKey('region.str_region_id'))
    str_latitude = db.Column(db.Text)
    str_longitude = db.Column(db.Text)
    str_workcenter_name = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    str_entry_hour = db.Column(db.Text)
    str_exit_hour = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.Text)


class Assistance(db.Model):
    __tablename__ = 'employee_assistance'
    sq_assistance_id = Sequence('sq_assistance_id', metadata=base.metadata)

    num_emp_assistance_id = db.Column(db.Numeric, sq_assistance_id, server_default=sq_assistance_id.next_value(),
                                      primary_key=True)
    num_employee_id = db.Column(db.Text, db.ForeignKey("employee.num_employee_id"), nullable=False)
    dte_starttime_assistance = db.Column(db.DateTime)
    dte_finishtime_assistance = db.Column(db.DateTime)
    str_workcenter_id = db.Column(db.Text, db.ForeignKey("workcenter.str_workcenter_id"), nullable=False)
    str_workcenter_starttime = db.Column(db.Text)
    chr_status = db.Column(db.CHAR)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.DateTime)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.DateTime)


class Person(db.Model):
    __tablename__ = 'person'
    sq_person_id = Sequence('sq_person_id', metadata=base.metadata)

    num_person_id = db.Column(db.Numeric, sq_person_id, server_default=sq_person_id.next_value(),
                              primary_key=True)
    str_person_name = db.Column(db.Text)
    str_last_name_dad = db.Column(db.Text)
    str_last_name_mom = db.Column(db.Text)
    dte_birthdate = db.Column(db.Date)
    str_person_sex = db.Column(db.Text)
    str_civil_status = db.Column(db.Text)
    str_photo = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    str_birthplace = db.Column(db.Text)
    str_nationality = db.Column(db.Text)
    str_linkedin = db.Column(db.Text)
    str_attribute = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.TIMESTAMP)


class Accesspoint(db.Model):
    __tablename__ = 'workcenter_accesspoint'
    sq_work_accesspoint_id = Sequence('sq_work_accesspoint_id', metadata=base.metadata)

    num_work_accesspoint_id = db.Column(db.Numeric, sq_work_accesspoint_id,
                                        server_default=sq_work_accesspoint_id.next_value(), primary_key=True)
    num_workcenter_id = db.Column(db.Numeric, db.ForeignKey('workcenter.num_workcenter_id'), nullable=False)
    str_work_accesspoint_des = db.Column(db.Text)
    str_mac_point = db.Column(db.Text)
    str_workcenter_id = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.Text)
    str_modifiedby = db.Column(db.Text)
    dte_modifieddate = db.Column(db.Text)


class Supervision(db.Model):
    __tablename__ = 'eval_supervision'
    sq_supervision_id = Sequence('sq_supervision_id', metadata=base.metadata)
    num_person_super_id = db.Column(db.Text, db.ForeignKey("person.num_person_id"), nullable=False)
    num_employee_eval_id = db.Column(db.Text, db.ForeignKey("employee.num_employee_id"), nullable=False)
    num_total_score = db.Column(db.Numeric)
    str_comment = db.Column(db.Text)
    chr_status = db.Column(db.Text)
    str_createdby = db.Column(db.Text)
    dte_createddate = db.Column(db.TIMESTAMP)
    dte_modifieddate = db.Column(db.TIMESTAMP)
    str_modifiedby = db.Column(db.Text)
    num_eval_id = db.Column(db.Numeric, db.ForeignKey("employee_evaluation.num_eval_id"), nullable=False)
    num_supervision_id = db.Column(db.Numeric, sq_supervision_id, server_default=sq_supervision_id.next_value(),
                                   primary_key=True)
