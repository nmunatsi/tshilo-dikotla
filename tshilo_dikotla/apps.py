from datetime import datetime
from td_dashboard.patterns import subject_identifier

from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import gettz
from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.core.checks import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate
from edc_base.apps import AppConfig as BaseEdcBaseAppConfig
from edc_constants.constants import FAILED_ELIGIBILITY
from edc_device.apps import AppConfig as BaseEdcDeviceAppConfig
from edc_device.constants import CENTRAL_SERVER
from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
from edc_identifier.apps import AppConfig as BaseEdcIdentifierAppConfig
from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig
from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig
from edc_timepoint.apps import AppConfig as BaseEdcTimepointAppConfig
from edc_timepoint.timepoint import Timepoint
from edc_timepoint.timepoint_collection import TimepointCollection

from edc_appointment.appointment_config import AppointmentConfig
from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
from edc_appointment.constants import COMPLETE_APPT
from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, LOST_VISIT, \
    COMPLETED_PROTOCOL_VISIT, MISSED_VISIT

from .sites import fqdn, td_site
from .system_checks import td_check

style = color_style()


def post_migrate_update_sites(sender=None, **kwargs):
    from edc_base.sites.utils import add_or_update_django_sites
    add_or_update_django_sites(
        apps=django_apps, sites=td_site, fqdn=fqdn)


class AppConfig(DjangoAppConfig):
    name = 'tshilo_dikotla'

    def ready(self):
        post_migrate.connect(post_migrate_update_sites, sender=self)
        register(td_check)


class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
    configurations = [
        AppointmentConfig(
            model='edc_appointment.appointment',
            related_visit_model='td_maternal.maternalvisit',
            appt_type='clinic'),
        AppointmentConfig(
            model='td_infant.appointment',
            related_visit_model='td_infant.infantvisit',
            appt_type='clinic')]


class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
    protocol = 'BHP085'
    protocol_name = 'Tshilo Dikotla'
    protocol_number = '085'
    protocol_title = ''
    study_open_datetime = datetime(
        2016, 4, 1, 0, 0, 0, tzinfo=gettz('UTC'))
    study_close_datetime = datetime(
        2020, 12, 1, 0, 0, 0, tzinfo=gettz('UTC'))


class EdcBaseAppConfig(BaseEdcBaseAppConfig):
    project_name = 'Tshilo Dikotla'
    institution = 'Botswana-Harvard AIDS Institute'


class EdcDeviceAppConfig(BaseEdcDeviceAppConfig):
    device_role = CENTRAL_SERVER
    device_id = '99'


class EdcIdentifierAppConfig(BaseEdcIdentifierAppConfig):
    identifier_prefix = '085'


class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
    visit_models = {
        'td_maternal': ('maternal_visit', 'td_maternal.maternalvisit'),
        'td_infant': ('infant_visit', 'td_infant.infantvisit'), }


class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
    country = 'botswana'
    definitions = {
        '7-day clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                             slots=[100, 100, 100, 100, 100, 100, 100]),
        '5-day clinic': dict(days=[MO, TU, WE, TH, FR],
                             slots=[100, 100, 100, 100, 100])}


class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):
    reason_field = {
        'td_maternal.maternalvisit': 'reason',
        'td_infant.infantvisit': 'reason'}
    create_on_reasons = [SCHEDULED, UNSCHEDULED, COMPLETED_PROTOCOL_VISIT]
    delete_on_reasons = [LOST_VISIT, FAILED_ELIGIBILITY, MISSED_VISIT]


class EdcTimepointAppConfig(BaseEdcTimepointAppConfig):
    timepoints = TimepointCollection(
        timepoints=[
            Timepoint(
                model='edc_appointment.appointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='edc_appointment.historicalappointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='td_infant.appointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='td_infant.historicalappointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT)
        ])
