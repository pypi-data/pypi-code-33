# ===================================================================================================
#                           _  __     _ _
#                          | |/ /__ _| | |_ _  _ _ _ __ _
#                          | ' </ _` | |  _| || | '_/ _` |
#                          |_|\_\__,_|_|\__|\_,_|_| \__,_|
#
# This file is part of the Kaltura Collaborative Media Suite which allows users
# to do with audio, video, and animation what Wiki platfroms allow them to do with
# text.
#
# Copyright (C) 2006-2019  Kaltura Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http:#www.gnu.org/licenses/>.
#
# @ignore
# ===================================================================================================
# @package Kaltura
# @subpackage Client
from __future__ import absolute_import

from ..Base import (
    getXmlNodeBool,
    getXmlNodeFloat,
    getXmlNodeInt,
    getXmlNodeText,
    KalturaClientPlugin,
    KalturaEnumsFactory,
    KalturaObjectBase,
    KalturaObjectFactory,
    KalturaParams,
    KalturaServiceBase,
)

API_VERSION = '4.7.84.18306'

########## enums ##########
# @package Kaltura
# @subpackage Client
class KalturaAdsPolicy(object):
    NO_ADS = "NO_ADS"
    KEEP_ADS = "KEEP_ADS"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAggregationCountOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAnnouncementOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAnnouncementRecipientsType(object):
    ALL = "All"
    LOGGEDIN = "LoggedIn"
    GUESTS = "Guests"
    OTHER = "Other"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAnnouncementStatus(object):
    NOTSENT = "NotSent"
    SENDING = "Sending"
    SENT = "Sent"
    ABORTED = "Aborted"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAppTokenHashType(object):
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    SHA512 = "SHA512"
    MD5 = "MD5"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAssetCommentOrderBy(object):
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAssetHistoryOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAssetOrderBy(object):
    RELEVANCY_DESC = "RELEVANCY_DESC"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    VIEWS_DESC = "VIEWS_DESC"
    RATINGS_DESC = "RATINGS_DESC"
    VOTES_DESC = "VOTES_DESC"
    START_DATE_DESC = "START_DATE_DESC"
    START_DATE_ASC = "START_DATE_ASC"
    LIKES_DESC = "LIKES_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAssetReferenceType(object):
    MEDIA = "media"
    EPG_INTERNAL = "epg_internal"
    EPG_EXTERNAL = "epg_external"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAssetReminderOrderBy(object):
    RELEVANCY_DESC = "RELEVANCY_DESC"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    VIEWS_DESC = "VIEWS_DESC"
    RATINGS_DESC = "RATINGS_DESC"
    VOTES_DESC = "VOTES_DESC"
    START_DATE_DESC = "START_DATE_DESC"
    START_DATE_ASC = "START_DATE_ASC"
    LIKES_DESC = "LIKES_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaAssetType(object):
    MEDIA = "media"
    RECORDING = "recording"
    EPG = "epg"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaBillingAction(object):
    UNKNOWN = "unknown"
    PURCHASE = "purchase"
    RENEW_PAYMENT = "renew_payment"
    RENEW_CANCELED_SUBSCRIPTION = "renew_canceled_subscription"
    CANCEL_SUBSCRIPTION_ORDER = "cancel_subscription_order"
    SUBSCRIPTION_DATE_CHANGED = "subscription_date_changed"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaBillingItemsType(object):
    UNKNOWN = "unknown"
    PPV = "ppv"
    SUBSCRIPTION = "subscription"
    PRE_PAID = "pre_paid"
    PRE_PAID_EXPIRED = "pre_paid_expired"
    COLLECTION = "collection"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaBillingPriceType(object):
    FULLPERIOD = "FullPeriod"
    PARTIALPERIOD = "PartialPeriod"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaBookmarkActionType(object):
    HIT = "HIT"
    PLAY = "PLAY"
    STOP = "STOP"
    PAUSE = "PAUSE"
    FIRST_PLAY = "FIRST_PLAY"
    SWOOSH = "SWOOSH"
    FULL_SCREEN = "FULL_SCREEN"
    SEND_TO_FRIEND = "SEND_TO_FRIEND"
    LOAD = "LOAD"
    FULL_SCREEN_EXIT = "FULL_SCREEN_EXIT"
    FINISH = "FINISH"
    ERROR = "ERROR"
    BITRATE_CHANGE = "BITRATE_CHANGE"
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaBookmarkOrderBy(object):
    POSITION_ASC = "POSITION_ASC"
    POSITION_DESC = "POSITION_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaBundleType(object):
    SUBSCRIPTION = "subscription"
    COLLECTION = "collection"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaChannelEnrichment(object):
    CLIENTLOCATION = "ClientLocation"
    USERID = "UserId"
    HOUSEHOLDID = "HouseholdId"
    DEVICEID = "DeviceId"
    DEVICETYPE = "DeviceType"
    UTCOFFSET = "UTCOffset"
    LANGUAGE = "Language"
    NPVRSUPPORT = "NPVRSupport"
    CATCHUP = "Catchup"
    PARENTAL = "Parental"
    DTTREGION = "DTTRegion"
    ATHOME = "AtHome"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaCollectionOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaCompensationType(object):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupDeviceOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupTagOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaConfigurationsOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaContextType(object):
    NONE = "none"
    RECORDING = "recording"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaCountryOrderBy(object):
    NAME_ASC = "NAME_ASC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaCouponGroupType(object):
    COUPON = "COUPON"
    GIFT_CARD = "GIFT_CARD"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaCouponStatus(object):
    VALID = "VALID"
    NOT_EXISTS = "NOT_EXISTS"
    ALREADY_USED = "ALREADY_USED"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaCurrencyOrderBy(object):
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    CODE_ASC = "CODE_ASC"
    CODE_DESC = "CODE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaDeviceStatus(object):
    PENDING = "PENDING"
    ACTIVATED = "ACTIVATED"
    NOT_ACTIVATED = "NOT_ACTIVATED"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaDrmSchemeName(object):
    PLAYREADY_CENC = "PLAYREADY_CENC"
    WIDEVINE_CENC = "WIDEVINE_CENC"
    FAIRPLAY = "FAIRPLAY"
    WIDEVINE = "WIDEVINE"
    PLAYREADY = "PLAYREADY"
    CUSTOM_DRM = "CUSTOM_DRM"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaEngagementOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaEngagementType(object):
    CHURN = "Churn"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaEntitlementOrderBy(object):
    PURCHASE_DATE_ASC = "PURCHASE_DATE_ASC"
    PURCHASE_DATE_DESC = "PURCHASE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaEntityReferenceBy(object):
    USER = "user"
    HOUSEHOLD = "household"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaExportDataType(object):
    VOD = "vod"
    EPG = "epg"
    USERS = "users"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaExportTaskOrderBy(object):
    CREATE_DATE_ASC = "CREATE_DATE_ASC"
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaExportType(object):
    FULL = "full"
    INCREMENTAL = "incremental"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaFavoriteOrderBy(object):
    CREATE_DATE_ASC = "CREATE_DATE_ASC"
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaFollowTvSeriesOrderBy(object):
    START_DATE_DESC = "START_DATE_DESC"
    START_DATE_ASC = "START_DATE_ASC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaGroupByField(object):
    MEDIA_TYPE_ID = "media_type_id"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdDeviceOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdFrequencyType(object):
    DEVICES = "devices"
    USERS = "users"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentGatewaySelectedBy(object):
    NONE = "none"
    ACCOUNT = "account"
    HOUSEHOLD = "household"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdRestriction(object):
    NOT_RESTRICTED = "not_restricted"
    USER_MASTER_RESTRICTED = "user_master_restricted"
    DEVICE_MASTER_RESTRICTED = "device_master_restricted"
    DEVICE_USER_MASTER_RESTRICTED = "device_user_master_restricted"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdState(object):
    OK = "ok"
    CREATED_WITHOUT_NPVR_ACCOUNT = "created_without_npvr_account"
    SUSPENDED = "suspended"
    NO_USERS_IN_HOUSEHOLD = "no_users_in_household"
    PENDING = "pending"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdSuspensionState(object):
    NOT_SUSPENDED = "NOT_SUSPENDED"
    SUSPENDED = "SUSPENDED"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdUserOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaHouseholdUserStatus(object):
    OK = "OK"
    PENDING = "PENDING"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaInboxMessageOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaInboxMessageStatus(object):
    UNREAD = "Unread"
    READ = "Read"
    DELETED = "Deleted"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaInboxMessageType(object):
    SYSTEMANNOUNCEMENT = "SystemAnnouncement"
    FOLLOWED = "Followed"
    ENGAGEMENT = "Engagement"
    INTEREST = "Interest"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaLanguageOrderBy(object):
    SYSTEM_NAME_ASC = "SYSTEM_NAME_ASC"
    SYSTEM_NAME_DESC = "SYSTEM_NAME_DESC"
    CODE_ASC = "CODE_ASC"
    CODE_DESC = "CODE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaMessageTemplateType(object):
    SERIES = "Series"
    REMINDER = "Reminder"
    CHURN = "Churn"
    SERIESREMINDER = "SeriesReminder"
    INTERESTVOD = "InterestVod"
    INTERESTEPG = "InterestEPG"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaMetaFieldName(object):
    NONE = "NONE"
    SERIES_ID = "SERIES_ID"
    SEASON_NUMBER = "SEASON_NUMBER"
    EPISODE_NUMBER = "EPISODE_NUMBER"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaMetaOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaMetaTagOrderBy(object):
    META_ASC = "META_ASC"
    META_DESC = "META_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaMetaType(object):
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    STRING_ARRAY = "STRING_ARRAY"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaNotificationType(object):
    ANNOUNCEMENT = "announcement"
    SYSTEM = "system"
    REMINDER = "Reminder"
    SERIES_REMINDER = "series_reminder"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaOTTUserOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaParentalRuleOrderBy(object):
    PARTNER_SORT_VALUE = "PARTNER_SORT_VALUE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaParentalRuleType(object):
    ALL = "ALL"
    MOVIES = "MOVIES"
    TV_SERIES = "TV_SERIES"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPartnerConfigurationType(object):
    DEFAULTPAYMENTGATEWAY = "DefaultPaymentGateway"
    ENABLEPAYMENTGATEWAYSELECTION = "EnablePaymentGatewaySelection"
    OSSADAPTER = "OSSAdapter"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPaymentMethodProfileOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPaymentMethodType(object):
    UNKNOWN = "unknown"
    CREDIT_CARD = "credit_card"
    SMS = "sms"
    PAY_PAL = "pay_pal"
    DEBIT_CARD = "debit_card"
    IDEAL = "ideal"
    INCASO = "incaso"
    GIFT = "gift"
    VISA = "visa"
    MASTER_CARD = "master_card"
    IN_APP = "in_app"
    M1 = "m1"
    CHANGE_SUBSCRIPTION = "change_subscription"
    OFFLINE = "offline"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPersonalFeedOrderBy(object):
    RELEVANCY_DESC = "RELEVANCY_DESC"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    VIEWS_DESC = "VIEWS_DESC"
    RATINGS_DESC = "RATINGS_DESC"
    VOTES_DESC = "VOTES_DESC"
    START_DATE_DESC = "START_DATE_DESC"
    START_DATE_ASC = "START_DATE_ASC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPinType(object):
    PURCHASE = "purchase"
    PARENTAL = "parental"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPlatform(object):
    ANDROID = "Android"
    IOS = "iOS"
    WINDOWSPHONE = "WindowsPhone"
    BLACKBERRY = "Blackberry"
    STB = "STB"
    CTV = "CTV"
    OTHER = "Other"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPlaybackContextType(object):
    TRAILER = "TRAILER"
    CATCHUP = "CATCHUP"
    START_OVER = "START_OVER"
    PLAYBACK = "PLAYBACK"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPositionOwner(object):
    HOUSEHOLD = "household"
    USER = "user"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPriceDetailsOrderBy(object):
    NAME_ASC = "NAME_ASC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPricePlanOrderBy(object):
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaProductPriceOrderBy(object):
    PRODUCT_ID_ASC = "PRODUCT_ID_ASC"
    PRODUCT_ID_DESC = "PRODUCT_ID_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaProtectionPolicy(object):
    EXTENDINGRECORDINGLIFETIME = "ExtendingRecordingLifetime"
    LIMITEDBYRECORDINGLIFETIME = "LimitedByRecordingLifetime"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPurchaseSettingsType(object):
    BLOCK = "block"
    ASK = "ask"
    ALLOW = "allow"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaPurchaseStatus(object):
    PPV_PURCHASED = "ppv_purchased"
    FREE = "free"
    FOR_PURCHASE_SUBSCRIPTION_ONLY = "for_purchase_subscription_only"
    SUBSCRIPTION_PURCHASED = "subscription_purchased"
    FOR_PURCHASE = "for_purchase"
    SUBSCRIPTION_PURCHASED_WRONG_CURRENCY = "subscription_purchased_wrong_currency"
    PRE_PAID_PURCHASED = "pre_paid_purchased"
    GEO_COMMERCE_BLOCKED = "geo_commerce_blocked"
    ENTITLED_TO_PREVIEW_MODULE = "entitled_to_preview_module"
    FIRST_DEVICE_LIMITATION = "first_device_limitation"
    COLLECTION_PURCHASED = "collection_purchased"
    USER_SUSPENDED = "user_suspended"
    NOT_FOR_PURCHASE = "not_for_purchase"
    INVALID_CURRENCY = "invalid_currency"
    CURRENCY_NOT_DEFINED_ON_PRICE_CODE = "currency_not_defined_on_price_code"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaQuotaOveragePolicy(object):
    STOPATQUOTA = "StopAtQuota"
    FIFOAUTODELETE = "FIFOAutoDelete"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRecordingContextOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRecordingOrderBy(object):
    TITLE_ASC = "TITLE_ASC"
    TITLE_DESC = "TITLE_DESC"
    START_DATE_ASC = "START_DATE_ASC"
    START_DATE_DESC = "START_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRecordingStatus(object):
    SCHEDULED = "SCHEDULED"
    RECORDING = "RECORDING"
    RECORDED = "RECORDED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    DELETED = "DELETED"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRecordingType(object):
    SINGLE = "SINGLE"
    SEASON = "SEASON"
    SERIES = "SERIES"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRegionOrderBy(object):
    CREATE_DATE_ASC = "CREATE_DATE_ASC"
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaReminderType(object):
    ASSET = "ASSET"
    SERIES = "SERIES"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaReportOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRuleActionType(object):
    BLOCK = "BLOCK"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRuleLevel(object):
    INVALID = "invalid"
    USER = "user"
    HOUSEHOLD = "household"
    ACCOUNT = "account"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaRuleType(object):
    PARENTAL = "parental"
    GEO = "geo"
    USER_TYPE = "user_type"
    DEVICE = "device"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaScheduledRecordingAssetType(object):
    SINGLE = "single"
    SERIES = "series"
    ALL = "all"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSearchHistoryOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSeriesRecordingOrderBy(object):
    START_DATE_ASC = "START_DATE_ASC"
    START_DATE_DESC = "START_DATE_DESC"
    ID_ASC = "ID_ASC"
    ID_DESC = "ID_DESC"
    SERIES_ID_ASC = "SERIES_ID_ASC"
    SERIES_ID_DESC = "SERIES_ID_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSeriesReminderOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialActionOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialActionPrivacy(object):
    ALLOW = "ALLOW"
    DONT_ALLOW = "DONT_ALLOW"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialActionType(object):
    LIKE = "LIKE"
    WATCH = "WATCH"
    RATE = "RATE"
    SHARE = "SHARE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialCommentOrderBy(object):
    CREATE_DATE_ASC = "CREATE_DATE_ASC"
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialFriendActivityOrderBy(object):
    NONE = "NONE"
    UPDATE_DATE_DESC = "UPDATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialNetwork(object):
    FACEBOOK = "facebook"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialPlatform(object):
    IN_APP = "IN_APP"
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialPrivacy(object):
    UNKNOWN = "UNKNOWN"
    EVERYONE = "EVERYONE"
    ALL_FRIENDS = "ALL_FRIENDS"
    FRIENDS_OF_FRIENDS = "FRIENDS_OF_FRIENDS"
    SELF = "SELF"
    CUSTOM = "CUSTOM"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSocialStatus(object):
    ERROR = "error"
    OK = "ok"
    USER_DOES_NOT_EXIST = "user_does_not_exist"
    NO_USER_SOCIAL_SETTINGS_FOUND = "no_user_social_settings_found"
    ASSET_ALREADY_LIKED = "asset_already_liked"
    NOT_ALLOWED = "not_allowed"
    INVALID_PARAMETERS = "invalid_parameters"
    NO_FACEBOOK_ACTION = "no_facebook_action"
    ASSET_ALREADY_RATED = "asset_already_rated"
    ASSET_DOSE_NOT_EXISTS = "asset_dose_not_exists"
    INVALID_PLATFORM_REQUEST = "invalid_platform_request"
    INVALID_ACCESS_TOKEN = "invalid_access_token"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaStreamType(object):
    CATCHUP = "catchup"
    START_OVER = "start_over"
    TRICK_PLAY = "trick_play"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSubscriptionDependencyType(object):
    NOTAPPLICABLE = "NOTAPPLICABLE"
    BASE = "BASE"
    ADDON = "ADDON"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSubscriptionOrderBy(object):
    START_DATE_ASC = "START_DATE_ASC"
    START_DATE_DESC = "START_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSetOrderBy(object):
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSetType(object):
    SWITCH = "SWITCH"
    DEPENDENCY = "DEPENDENCY"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaTopicAutomaticIssueNotification(object):
    INHERIT = "Inherit"
    YES = "Yes"
    NO = "No"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaTopicOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaTransactionAdapterStatus(object):
    OK = "OK"
    PENDING = "PENDING"
    FAILED = "FAILED"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaTransactionHistoryOrderBy(object):
    CREATE_DATE_ASC = "CREATE_DATE_ASC"
    CREATE_DATE_DESC = "CREATE_DATE_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaTransactionType(object):
    PPV = "ppv"
    SUBSCRIPTION = "subscription"
    COLLECTION = "collection"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaUserAssetRuleOrderBy(object):
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaUserAssetsListItemType(object):
    ALL = "all"
    MEDIA = "media"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaUserAssetsListType(object):
    ALL = "all"
    WATCH = "watch"
    PURCHASE = "purchase"
    LIBRARY = "library"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaUserRoleOrderBy(object):
    NONE = "NONE"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaUserState(object):
    OK = "ok"
    USER_WITH_NO_HOUSEHOLD = "user_with_no_household"
    USER_CREATED_WITH_NO_ROLE = "user_created_with_no_role"
    USER_NOT_ACTIVATED = "user_not_activated"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

# @package Kaltura
# @subpackage Client
class KalturaWatchStatus(object):
    PROGRESS = "progress"
    DONE = "done"
    ALL = "all"

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

########## classes ##########
# @package Kaltura
# @subpackage Client
class KalturaListResponse(KalturaObjectBase):
    """Base list wrapper"""

    def __init__(self,
            totalCount=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Total items
        # @var int
        self.totalCount = totalCount


    PROPERTY_LOADERS = {
        'totalCount': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaListResponse")
        kparams.addIntIfDefined("totalCount", self.totalCount)
        return kparams

    def getTotalCount(self):
        return self.totalCount

    def setTotalCount(self, newTotalCount):
        self.totalCount = newTotalCount


# @package Kaltura
# @subpackage Client
class KalturaApiExceptionArg(KalturaObjectBase):
    def __init__(self,
            name=NotImplemented,
            value=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Argument name
        # @var string
        self.name = name

        # Argument value
        # @var string
        self.value = value


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'value': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaApiExceptionArg.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaApiExceptionArg")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("value", self.value)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaSocialComment(KalturaObjectBase):
    def __init__(self,
            header=NotImplemented,
            text=NotImplemented,
            createDate=NotImplemented,
            writer=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Comment header
        # @var string
        self.header = header

        # Comment body
        # @var string
        self.text = text

        # Comment creation date
        # @var int
        self.createDate = createDate

        # The writer of the comment
        # @var string
        self.writer = writer


    PROPERTY_LOADERS = {
        'header': getXmlNodeText, 
        'text': getXmlNodeText, 
        'createDate': getXmlNodeInt, 
        'writer': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialComment.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSocialComment")
        kparams.addStringIfDefined("header", self.header)
        kparams.addStringIfDefined("text", self.text)
        kparams.addIntIfDefined("createDate", self.createDate)
        kparams.addStringIfDefined("writer", self.writer)
        return kparams

    def getHeader(self):
        return self.header

    def setHeader(self, newHeader):
        self.header = newHeader

    def getText(self):
        return self.text

    def setText(self, newText):
        self.text = newText

    def getCreateDate(self):
        return self.createDate

    def setCreateDate(self, newCreateDate):
        self.createDate = newCreateDate

    def getWriter(self):
        return self.writer

    def setWriter(self, newWriter):
        self.writer = newWriter


# @package Kaltura
# @subpackage Client
class KalturaSocialCommentListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Social comments list
        # @var array of KalturaSocialComment
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSocialComment'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialCommentListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSocialCommentListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaSocialNetworkComment(KalturaSocialComment):
    def __init__(self,
            header=NotImplemented,
            text=NotImplemented,
            createDate=NotImplemented,
            writer=NotImplemented,
            likeCounter=NotImplemented,
            authorImageUrl=NotImplemented):
        KalturaSocialComment.__init__(self,
            header,
            text,
            createDate,
            writer)

        # Number of likes
        # @var string
        self.likeCounter = likeCounter

        # The URL of the profile picture of the author of the comment
        # @var string
        self.authorImageUrl = authorImageUrl


    PROPERTY_LOADERS = {
        'likeCounter': getXmlNodeText, 
        'authorImageUrl': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaSocialComment.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialNetworkComment.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialComment.toParams(self)
        kparams.put("objectType", "KalturaSocialNetworkComment")
        kparams.addStringIfDefined("likeCounter", self.likeCounter)
        kparams.addStringIfDefined("authorImageUrl", self.authorImageUrl)
        return kparams

    def getLikeCounter(self):
        return self.likeCounter

    def setLikeCounter(self, newLikeCounter):
        self.likeCounter = newLikeCounter

    def getAuthorImageUrl(self):
        return self.authorImageUrl

    def setAuthorImageUrl(self, newAuthorImageUrl):
        self.authorImageUrl = newAuthorImageUrl


# @package Kaltura
# @subpackage Client
class KalturaTwitterTwit(KalturaSocialNetworkComment):
    def __init__(self,
            header=NotImplemented,
            text=NotImplemented,
            createDate=NotImplemented,
            writer=NotImplemented,
            likeCounter=NotImplemented,
            authorImageUrl=NotImplemented):
        KalturaSocialNetworkComment.__init__(self,
            header,
            text,
            createDate,
            writer,
            likeCounter,
            authorImageUrl)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaSocialNetworkComment.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTwitterTwit.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialNetworkComment.toParams(self)
        kparams.put("objectType", "KalturaTwitterTwit")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaFacebookPost(KalturaSocialNetworkComment):
    def __init__(self,
            header=NotImplemented,
            text=NotImplemented,
            createDate=NotImplemented,
            writer=NotImplemented,
            likeCounter=NotImplemented,
            authorImageUrl=NotImplemented,
            comments=NotImplemented,
            link=NotImplemented):
        KalturaSocialNetworkComment.__init__(self,
            header,
            text,
            createDate,
            writer,
            likeCounter,
            authorImageUrl)

        # List of comments on the post
        # @var array of KalturaSocialNetworkComment
        self.comments = comments

        # A link associated to the post
        # @var string
        self.link = link


    PROPERTY_LOADERS = {
        'comments': (KalturaObjectFactory.createArray, 'KalturaSocialNetworkComment'), 
        'link': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaSocialNetworkComment.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFacebookPost.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialNetworkComment.toParams(self)
        kparams.put("objectType", "KalturaFacebookPost")
        kparams.addArrayIfDefined("comments", self.comments)
        kparams.addStringIfDefined("link", self.link)
        return kparams

    def getComments(self):
        return self.comments

    def setComments(self, newComments):
        self.comments = newComments

    def getLink(self):
        return self.link

    def setLink(self, newLink):
        self.link = newLink


# @package Kaltura
# @subpackage Client
class KalturaAssetComment(KalturaSocialComment):
    """Asset Comment"""

    def __init__(self,
            header=NotImplemented,
            text=NotImplemented,
            createDate=NotImplemented,
            writer=NotImplemented,
            id=NotImplemented,
            assetId=NotImplemented,
            assetType=NotImplemented,
            subHeader=NotImplemented):
        KalturaSocialComment.__init__(self,
            header,
            text,
            createDate,
            writer)

        # Comment ID
        # @var int
        self.id = id

        # Asset identifier
        # @var int
        self.assetId = assetId

        # Asset Type
        # @var KalturaAssetType
        self.assetType = assetType

        # Sub Header
        # @var string
        self.subHeader = subHeader


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'assetId': getXmlNodeInt, 
        'assetType': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'subHeader': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaSocialComment.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetComment.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialComment.toParams(self)
        kparams.put("objectType", "KalturaAssetComment")
        kparams.addIntIfDefined("id", self.id)
        kparams.addIntIfDefined("assetId", self.assetId)
        kparams.addStringEnumIfDefined("assetType", self.assetType)
        kparams.addStringIfDefined("subHeader", self.subHeader)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId

    def getAssetType(self):
        return self.assetType

    def setAssetType(self, newAssetType):
        self.assetType = newAssetType

    def getSubHeader(self):
        return self.subHeader

    def setSubHeader(self, newSubHeader):
        self.subHeader = newSubHeader


# @package Kaltura
# @subpackage Client
class KalturaSocialAction(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            actionType=NotImplemented,
            time=NotImplemented,
            assetId=NotImplemented,
            assetType=NotImplemented,
            url=NotImplemented):
        KalturaObjectBase.__init__(self)

        # social action document id
        # @var string
        # @readonly
        self.id = id

        # Action type
        # @var KalturaSocialActionType
        self.actionType = actionType

        # EPOC based timestamp for when the action occurred
        # @var int
        self.time = time

        # ID of the asset that was acted upon
        # @var int
        self.assetId = assetId

        # Type of the asset that was acted upon, currently only VOD (media)
        # @var KalturaAssetType
        self.assetType = assetType

        # The value of the url
        # @var string
        self.url = url


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'actionType': (KalturaEnumsFactory.createString, "KalturaSocialActionType"), 
        'time': getXmlNodeInt, 
        'assetId': getXmlNodeInt, 
        'assetType': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'url': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialAction.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSocialAction")
        kparams.addStringEnumIfDefined("actionType", self.actionType)
        kparams.addIntIfDefined("time", self.time)
        kparams.addIntIfDefined("assetId", self.assetId)
        kparams.addStringEnumIfDefined("assetType", self.assetType)
        kparams.addStringIfDefined("url", self.url)
        return kparams

    def getId(self):
        return self.id

    def getActionType(self):
        return self.actionType

    def setActionType(self, newActionType):
        self.actionType = newActionType

    def getTime(self):
        return self.time

    def setTime(self, newTime):
        self.time = newTime

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId

    def getAssetType(self):
        return self.assetType

    def setAssetType(self, newAssetType):
        self.assetType = newAssetType

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl


# @package Kaltura
# @subpackage Client
class KalturaSocialFriendActivity(KalturaObjectBase):
    def __init__(self,
            userFullName=NotImplemented,
            userPictureUrl=NotImplemented,
            socialAction=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The full name of the user who did the social action
        # @var string
        self.userFullName = userFullName

        # The URL of the profile picture of the user who did the social action
        # @var string
        self.userPictureUrl = userPictureUrl

        # The social action
        # @var KalturaSocialAction
        self.socialAction = socialAction


    PROPERTY_LOADERS = {
        'userFullName': getXmlNodeText, 
        'userPictureUrl': getXmlNodeText, 
        'socialAction': (KalturaObjectFactory.create, 'KalturaSocialAction'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialFriendActivity.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSocialFriendActivity")
        kparams.addStringIfDefined("userFullName", self.userFullName)
        kparams.addStringIfDefined("userPictureUrl", self.userPictureUrl)
        kparams.addObjectIfDefined("socialAction", self.socialAction)
        return kparams

    def getUserFullName(self):
        return self.userFullName

    def setUserFullName(self, newUserFullName):
        self.userFullName = newUserFullName

    def getUserPictureUrl(self):
        return self.userPictureUrl

    def setUserPictureUrl(self, newUserPictureUrl):
        self.userPictureUrl = newUserPictureUrl

    def getSocialAction(self):
        return self.socialAction

    def setSocialAction(self, newSocialAction):
        self.socialAction = newSocialAction


# @package Kaltura
# @subpackage Client
class KalturaSocialFriendActivityListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Social friends activity
        # @var array of KalturaSocialFriendActivity
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSocialFriendActivity'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialFriendActivityListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSocialFriendActivityListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaSocialActionRate(KalturaSocialAction):
    def __init__(self,
            id=NotImplemented,
            actionType=NotImplemented,
            time=NotImplemented,
            assetId=NotImplemented,
            assetType=NotImplemented,
            url=NotImplemented,
            rate=NotImplemented):
        KalturaSocialAction.__init__(self,
            id,
            actionType,
            time,
            assetId,
            assetType,
            url)

        # The value of the rating
        # @var int
        self.rate = rate


    PROPERTY_LOADERS = {
        'rate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaSocialAction.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialActionRate.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialAction.toParams(self)
        kparams.put("objectType", "KalturaSocialActionRate")
        kparams.addIntIfDefined("rate", self.rate)
        return kparams

    def getRate(self):
        return self.rate

    def setRate(self, newRate):
        self.rate = newRate


# @package Kaltura
# @subpackage Client
class KalturaSocialActionListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # The social actions
        # @var array of KalturaSocialAction
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSocialAction'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialActionListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSocialActionListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentMethod(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            externalId=NotImplemented,
            paymentGatewayId=NotImplemented,
            details=NotImplemented,
            isDefault=NotImplemented,
            paymentMethodProfileId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Household payment method identifier (internal)
        # @var int
        # @readonly
        self.id = id

        # External identifier for the household payment method
        # @var string
        # @insertonly
        self.externalId = externalId

        # Payment-gateway identifier
        # @var int
        self.paymentGatewayId = paymentGatewayId

        # Description of the payment method details
        # @var string
        self.details = details

        # indicates whether the payment method is set as default for the household
        # @var bool
        # @readonly
        self.isDefault = isDefault

        # Payment method profile identifier
        # @var int
        self.paymentMethodProfileId = paymentMethodProfileId


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'externalId': getXmlNodeText, 
        'paymentGatewayId': getXmlNodeInt, 
        'details': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
        'paymentMethodProfileId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdPaymentMethod.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdPaymentMethod")
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addIntIfDefined("paymentGatewayId", self.paymentGatewayId)
        kparams.addStringIfDefined("details", self.details)
        kparams.addIntIfDefined("paymentMethodProfileId", self.paymentMethodProfileId)
        return kparams

    def getId(self):
        return self.id

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getPaymentGatewayId(self):
        return self.paymentGatewayId

    def setPaymentGatewayId(self, newPaymentGatewayId):
        self.paymentGatewayId = newPaymentGatewayId

    def getDetails(self):
        return self.details

    def setDetails(self, newDetails):
        self.details = newDetails

    def getIsDefault(self):
        return self.isDefault

    def getPaymentMethodProfileId(self):
        return self.paymentMethodProfileId

    def setPaymentMethodProfileId(self, newPaymentMethodProfileId):
        self.paymentMethodProfileId = newPaymentMethodProfileId


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentMethodListResponse(KalturaListResponse):
    """List of household payment methods."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Follow data list
        # @var array of KalturaHouseholdPaymentMethod
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaHouseholdPaymentMethod'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdPaymentMethodListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaHouseholdPaymentMethodListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaPaymentMethodProfile(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            paymentGatewayId=NotImplemented,
            name=NotImplemented,
            allowMultiInstance=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Payment method identifier (internal)
        # @var int
        # @readonly
        self.id = id

        # Payment gateway identifier (internal)
        # @var int
        self.paymentGatewayId = paymentGatewayId

        # Payment method name
        # @var string
        self.name = name

        # Indicates whether the payment method allow multiple instances
        # @var bool
        self.allowMultiInstance = allowMultiInstance


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'paymentGatewayId': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'allowMultiInstance': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentMethodProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPaymentMethodProfile")
        kparams.addIntIfDefined("paymentGatewayId", self.paymentGatewayId)
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("allowMultiInstance", self.allowMultiInstance)
        return kparams

    def getId(self):
        return self.id

    def getPaymentGatewayId(self):
        return self.paymentGatewayId

    def setPaymentGatewayId(self, newPaymentGatewayId):
        self.paymentGatewayId = newPaymentGatewayId

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getAllowMultiInstance(self):
        return self.allowMultiInstance

    def setAllowMultiInstance(self, newAllowMultiInstance):
        self.allowMultiInstance = newAllowMultiInstance


# @package Kaltura
# @subpackage Client
class KalturaPaymentMethodProfileListResponse(KalturaListResponse):
    """List of payment method profiles."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Payment method profiles list
        # @var array of KalturaPaymentMethodProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaPaymentMethodProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentMethodProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaPaymentMethodProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentGateway(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isDefault=NotImplemented,
            selectedBy=NotImplemented):
        KalturaObjectBase.__init__(self)

        # payment gateway id
        # @var int
        # @readonly
        self.id = id

        # payment gateway name
        # @var string
        self.name = name

        # Payment gateway default (true/false)
        # @var bool
        self.isDefault = isDefault

        # distinction payment gateway selected by account or household
        # @var KalturaHouseholdPaymentGatewaySelectedBy
        self.selectedBy = selectedBy


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
        'selectedBy': (KalturaEnumsFactory.createString, "KalturaHouseholdPaymentGatewaySelectedBy"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdPaymentGateway.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdPaymentGateway")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        kparams.addStringEnumIfDefined("selectedBy", self.selectedBy)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault

    def getSelectedBy(self):
        return self.selectedBy

    def setSelectedBy(self, newSelectedBy):
        self.selectedBy = newSelectedBy


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentGatewayListResponse(KalturaListResponse):
    """List of household payment gateways."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Follow data list
        # @var array of KalturaHouseholdPaymentGateway
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaHouseholdPaymentGateway'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdPaymentGatewayListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaHouseholdPaymentGatewayListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaPaymentGatewayBaseProfile(KalturaObjectBase):
    """Payment gateway base profile"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isDefault=NotImplemented,
            selectedBy=NotImplemented):
        KalturaObjectBase.__init__(self)

        # payment gateway id
        # @var int
        # @readonly
        self.id = id

        # payment gateway name
        # @var string
        self.name = name

        # Payment gateway default (true/false)
        # @var bool
        self.isDefault = isDefault

        # distinction payment gateway selected by account or household
        # @var KalturaHouseholdPaymentGatewaySelectedBy
        self.selectedBy = selectedBy


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
        'selectedBy': (KalturaEnumsFactory.createString, "KalturaHouseholdPaymentGatewaySelectedBy"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentGatewayBaseProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPaymentGatewayBaseProfile")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        kparams.addStringEnumIfDefined("selectedBy", self.selectedBy)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault

    def getSelectedBy(self):
        return self.selectedBy

    def setSelectedBy(self, newSelectedBy):
        self.selectedBy = newSelectedBy


# @package Kaltura
# @subpackage Client
class KalturaValue(KalturaObjectBase):
    """A representation to return an array of values"""

    def __init__(self,
            description=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Description
        # @var string
        self.description = description


    PROPERTY_LOADERS = {
        'description': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaValue")
        kparams.addStringIfDefined("description", self.description)
        return kparams

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription


# @package Kaltura
# @subpackage Client
class KalturaStringValue(KalturaValue):
    """A string representation to return an array of strings"""

    def __init__(self,
            description=NotImplemented,
            value=NotImplemented):
        KalturaValue.__init__(self,
            description)

        # Value
        # @var string
        self.value = value


    PROPERTY_LOADERS = {
        'value': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaValue.fromXml(self, node)
        self.fromXmlImpl(node, KalturaStringValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaValue.toParams(self)
        kparams.put("objectType", "KalturaStringValue")
        kparams.addStringIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaPaymentGatewayProfile(KalturaPaymentGatewayBaseProfile):
    """Payment gateway profile"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isDefault=NotImplemented,
            selectedBy=NotImplemented,
            isActive=NotImplemented,
            adapterUrl=NotImplemented,
            transactUrl=NotImplemented,
            statusUrl=NotImplemented,
            renewUrl=NotImplemented,
            paymentGatewaySettings=NotImplemented,
            externalIdentifier=NotImplemented,
            pendingInterval=NotImplemented,
            pendingRetries=NotImplemented,
            sharedSecret=NotImplemented,
            renewIntervalMinutes=NotImplemented,
            renewStartMinutes=NotImplemented,
            externalVerification=NotImplemented):
        KalturaPaymentGatewayBaseProfile.__init__(self,
            id,
            name,
            isDefault,
            selectedBy)

        # Payment gateway is active status
        # @var int
        self.isActive = isActive

        # Payment gateway adapter URL
        # @var string
        self.adapterUrl = adapterUrl

        # Payment gateway transact URL
        # @var string
        self.transactUrl = transactUrl

        # Payment gateway status URL
        # @var string
        self.statusUrl = statusUrl

        # Payment gateway renew URL
        # @var string
        self.renewUrl = renewUrl

        # Payment gateway extra parameters
        # @var map
        self.paymentGatewaySettings = paymentGatewaySettings

        # Payment gateway external identifier
        # @var string
        self.externalIdentifier = externalIdentifier

        # Pending Interval in minutes
        # @var int
        self.pendingInterval = pendingInterval

        # Pending Retries
        # @var int
        self.pendingRetries = pendingRetries

        # Shared Secret
        # @var string
        self.sharedSecret = sharedSecret

        # Renew Interval Minutes
        # @var int
        self.renewIntervalMinutes = renewIntervalMinutes

        # Renew Start Minutes
        # @var int
        self.renewStartMinutes = renewStartMinutes

        # Payment gateway external verification
        # @var bool
        self.externalVerification = externalVerification


    PROPERTY_LOADERS = {
        'isActive': getXmlNodeInt, 
        'adapterUrl': getXmlNodeText, 
        'transactUrl': getXmlNodeText, 
        'statusUrl': getXmlNodeText, 
        'renewUrl': getXmlNodeText, 
        'paymentGatewaySettings': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'externalIdentifier': getXmlNodeText, 
        'pendingInterval': getXmlNodeInt, 
        'pendingRetries': getXmlNodeInt, 
        'sharedSecret': getXmlNodeText, 
        'renewIntervalMinutes': getXmlNodeInt, 
        'renewStartMinutes': getXmlNodeInt, 
        'externalVerification': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaPaymentGatewayBaseProfile.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentGatewayProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPaymentGatewayBaseProfile.toParams(self)
        kparams.put("objectType", "KalturaPaymentGatewayProfile")
        kparams.addIntIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("adapterUrl", self.adapterUrl)
        kparams.addStringIfDefined("transactUrl", self.transactUrl)
        kparams.addStringIfDefined("statusUrl", self.statusUrl)
        kparams.addStringIfDefined("renewUrl", self.renewUrl)
        kparams.addMapIfDefined("paymentGatewaySettings", self.paymentGatewaySettings)
        kparams.addStringIfDefined("externalIdentifier", self.externalIdentifier)
        kparams.addIntIfDefined("pendingInterval", self.pendingInterval)
        kparams.addIntIfDefined("pendingRetries", self.pendingRetries)
        kparams.addStringIfDefined("sharedSecret", self.sharedSecret)
        kparams.addIntIfDefined("renewIntervalMinutes", self.renewIntervalMinutes)
        kparams.addIntIfDefined("renewStartMinutes", self.renewStartMinutes)
        kparams.addBoolIfDefined("externalVerification", self.externalVerification)
        return kparams

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getAdapterUrl(self):
        return self.adapterUrl

    def setAdapterUrl(self, newAdapterUrl):
        self.adapterUrl = newAdapterUrl

    def getTransactUrl(self):
        return self.transactUrl

    def setTransactUrl(self, newTransactUrl):
        self.transactUrl = newTransactUrl

    def getStatusUrl(self):
        return self.statusUrl

    def setStatusUrl(self, newStatusUrl):
        self.statusUrl = newStatusUrl

    def getRenewUrl(self):
        return self.renewUrl

    def setRenewUrl(self, newRenewUrl):
        self.renewUrl = newRenewUrl

    def getPaymentGatewaySettings(self):
        return self.paymentGatewaySettings

    def setPaymentGatewaySettings(self, newPaymentGatewaySettings):
        self.paymentGatewaySettings = newPaymentGatewaySettings

    def getExternalIdentifier(self):
        return self.externalIdentifier

    def setExternalIdentifier(self, newExternalIdentifier):
        self.externalIdentifier = newExternalIdentifier

    def getPendingInterval(self):
        return self.pendingInterval

    def setPendingInterval(self, newPendingInterval):
        self.pendingInterval = newPendingInterval

    def getPendingRetries(self):
        return self.pendingRetries

    def setPendingRetries(self, newPendingRetries):
        self.pendingRetries = newPendingRetries

    def getSharedSecret(self):
        return self.sharedSecret

    def setSharedSecret(self, newSharedSecret):
        self.sharedSecret = newSharedSecret

    def getRenewIntervalMinutes(self):
        return self.renewIntervalMinutes

    def setRenewIntervalMinutes(self, newRenewIntervalMinutes):
        self.renewIntervalMinutes = newRenewIntervalMinutes

    def getRenewStartMinutes(self):
        return self.renewStartMinutes

    def setRenewStartMinutes(self, newRenewStartMinutes):
        self.renewStartMinutes = newRenewStartMinutes

    def getExternalVerification(self):
        return self.externalVerification

    def setExternalVerification(self, newExternalVerification):
        self.externalVerification = newExternalVerification


# @package Kaltura
# @subpackage Client
class KalturaPaymentGatewayProfileListResponse(KalturaListResponse):
    """PaymentGatewayProfile list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of payment-gateway profiles
        # @var array of KalturaPaymentGatewayProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaPaymentGatewayProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentGatewayProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaPaymentGatewayProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaTranslationToken(KalturaObjectBase):
    """Container for translation"""

    def __init__(self,
            language=NotImplemented,
            value=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Language code
        # @var string
        self.language = language

        # Translated value
        # @var string
        self.value = value


    PROPERTY_LOADERS = {
        'language': getXmlNodeText, 
        'value': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTranslationToken.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaTranslationToken")
        kparams.addStringIfDefined("language", self.language)
        kparams.addStringIfDefined("value", self.value)
        return kparams

    def getLanguage(self):
        return self.language

    def setLanguage(self, newLanguage):
        self.language = newLanguage

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaMultilingualStringValue(KalturaValue):
    """Array of translated strings"""

    def __init__(self,
            description=NotImplemented,
            value=NotImplemented,
            multilingualValue=NotImplemented):
        KalturaValue.__init__(self,
            description)

        # Value
        # @var string
        # @readonly
        self.value = value

        # Value
        # @var array of KalturaTranslationToken
        self.multilingualValue = multilingualValue


    PROPERTY_LOADERS = {
        'value': getXmlNodeText, 
        'multilingualValue': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
    }

    def fromXml(self, node):
        KalturaValue.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMultilingualStringValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaValue.toParams(self)
        kparams.put("objectType", "KalturaMultilingualStringValue")
        kparams.addArrayIfDefined("multilingualValue", self.multilingualValue)
        return kparams

    def getValue(self):
        return self.value

    def getMultilingualValue(self):
        return self.multilingualValue

    def setMultilingualValue(self, newMultilingualValue):
        self.multilingualValue = newMultilingualValue


# @package Kaltura
# @subpackage Client
class KalturaLongValue(KalturaValue):
    """A string representation to return an array of longs"""

    def __init__(self,
            description=NotImplemented,
            value=NotImplemented):
        KalturaValue.__init__(self,
            description)

        # Value
        # @var int
        self.value = value


    PROPERTY_LOADERS = {
        'value': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaValue.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLongValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaValue.toParams(self)
        kparams.put("objectType", "KalturaLongValue")
        kparams.addIntIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaDoubleValue(KalturaValue):
    """A string representation to return an array of doubles"""

    def __init__(self,
            description=NotImplemented,
            value=NotImplemented):
        KalturaValue.__init__(self,
            description)

        # Value
        # @var float
        self.value = value


    PROPERTY_LOADERS = {
        'value': getXmlNodeFloat, 
    }

    def fromXml(self, node):
        KalturaValue.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDoubleValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaValue.toParams(self)
        kparams.put("objectType", "KalturaDoubleValue")
        kparams.addFloatIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaBooleanValue(KalturaValue):
    """A string representation to return an array of booleans"""

    def __init__(self,
            description=NotImplemented,
            value=NotImplemented):
        KalturaValue.__init__(self,
            description)

        # Value
        # @var bool
        self.value = value


    PROPERTY_LOADERS = {
        'value': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaValue.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBooleanValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaValue.toParams(self)
        kparams.put("objectType", "KalturaBooleanValue")
        kparams.addBoolIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaIntegerValue(KalturaValue):
    """A string representation to return an array of ints"""

    def __init__(self,
            description=NotImplemented,
            value=NotImplemented):
        KalturaValue.__init__(self,
            description)

        # Value
        # @var int
        self.value = value


    PROPERTY_LOADERS = {
        'value': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaValue.fromXml(self, node)
        self.fromXmlImpl(node, KalturaIntegerValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaValue.toParams(self)
        kparams.put("objectType", "KalturaIntegerValue")
        kparams.addIntIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaPluginData(KalturaObjectBase):
    def __init__(self):
        KalturaObjectBase.__init__(self)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPluginData.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPluginData")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaDrmPlaybackPluginData(KalturaPluginData):
    def __init__(self,
            scheme=NotImplemented,
            licenseURL=NotImplemented):
        KalturaPluginData.__init__(self)

        # Scheme
        # @var KalturaDrmSchemeName
        self.scheme = scheme

        # License URL
        # @var string
        self.licenseURL = licenseURL


    PROPERTY_LOADERS = {
        'scheme': (KalturaEnumsFactory.createString, "KalturaDrmSchemeName"), 
        'licenseURL': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaPluginData.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDrmPlaybackPluginData.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPluginData.toParams(self)
        kparams.put("objectType", "KalturaDrmPlaybackPluginData")
        kparams.addStringEnumIfDefined("scheme", self.scheme)
        kparams.addStringIfDefined("licenseURL", self.licenseURL)
        return kparams

    def getScheme(self):
        return self.scheme

    def setScheme(self, newScheme):
        self.scheme = newScheme

    def getLicenseURL(self):
        return self.licenseURL

    def setLicenseURL(self, newLicenseURL):
        self.licenseURL = newLicenseURL


# @package Kaltura
# @subpackage Client
class KalturaCustomDrmPlaybackPluginData(KalturaDrmPlaybackPluginData):
    def __init__(self,
            scheme=NotImplemented,
            licenseURL=NotImplemented,
            data=NotImplemented):
        KalturaDrmPlaybackPluginData.__init__(self,
            scheme,
            licenseURL)

        # Custom DRM license data
        # @var string
        self.data = data


    PROPERTY_LOADERS = {
        'data': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaDrmPlaybackPluginData.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCustomDrmPlaybackPluginData.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaDrmPlaybackPluginData.toParams(self)
        kparams.put("objectType", "KalturaCustomDrmPlaybackPluginData")
        kparams.addStringIfDefined("data", self.data)
        return kparams

    def getData(self):
        return self.data

    def setData(self, newData):
        self.data = newData


# @package Kaltura
# @subpackage Client
class KalturaHouseholdDevice(KalturaObjectBase):
    """Device details"""

    def __init__(self,
            householdId=NotImplemented,
            udid=NotImplemented,
            name=NotImplemented,
            brandId=NotImplemented,
            activatedOn=NotImplemented,
            status=NotImplemented,
            deviceFamilyId=NotImplemented,
            drm=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Household identifier
        # @var int
        self.householdId = householdId

        # Device UDID
        # @var string
        # @insertonly
        self.udid = udid

        # Device name
        # @var string
        self.name = name

        # Device brand identifier
        # @var int
        self.brandId = brandId

        # Device activation date (epoch)
        # @var int
        self.activatedOn = activatedOn

        # Device state
        # @var KalturaDeviceStatus
        # @readonly
        self.status = status

        # Device family id
        # @var int
        # @readonly
        self.deviceFamilyId = deviceFamilyId

        # Device DRM data
        # @var KalturaCustomDrmPlaybackPluginData
        # @readonly
        self.drm = drm


    PROPERTY_LOADERS = {
        'householdId': getXmlNodeInt, 
        'udid': getXmlNodeText, 
        'name': getXmlNodeText, 
        'brandId': getXmlNodeInt, 
        'activatedOn': getXmlNodeInt, 
        'status': (KalturaEnumsFactory.createString, "KalturaDeviceStatus"), 
        'deviceFamilyId': getXmlNodeInt, 
        'drm': (KalturaObjectFactory.create, 'KalturaCustomDrmPlaybackPluginData'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdDevice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdDevice")
        kparams.addIntIfDefined("householdId", self.householdId)
        kparams.addStringIfDefined("udid", self.udid)
        kparams.addStringIfDefined("name", self.name)
        kparams.addIntIfDefined("brandId", self.brandId)
        kparams.addIntIfDefined("activatedOn", self.activatedOn)
        return kparams

    def getHouseholdId(self):
        return self.householdId

    def setHouseholdId(self, newHouseholdId):
        self.householdId = newHouseholdId

    def getUdid(self):
        return self.udid

    def setUdid(self, newUdid):
        self.udid = newUdid

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getBrandId(self):
        return self.brandId

    def setBrandId(self, newBrandId):
        self.brandId = newBrandId

    def getActivatedOn(self):
        return self.activatedOn

    def setActivatedOn(self, newActivatedOn):
        self.activatedOn = newActivatedOn

    def getStatus(self):
        return self.status

    def getDeviceFamilyId(self):
        return self.deviceFamilyId

    def getDrm(self):
        return self.drm


# @package Kaltura
# @subpackage Client
class KalturaHouseholdDeviceListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Household devices
        # @var array of KalturaHouseholdDevice
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaHouseholdDevice'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdDeviceListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaHouseholdDeviceListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaFairPlayPlaybackPluginData(KalturaDrmPlaybackPluginData):
    def __init__(self,
            scheme=NotImplemented,
            licenseURL=NotImplemented,
            certificate=NotImplemented):
        KalturaDrmPlaybackPluginData.__init__(self,
            scheme,
            licenseURL)

        # Custom data string
        # @var string
        self.certificate = certificate


    PROPERTY_LOADERS = {
        'certificate': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaDrmPlaybackPluginData.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFairPlayPlaybackPluginData.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaDrmPlaybackPluginData.toParams(self)
        kparams.put("objectType", "KalturaFairPlayPlaybackPluginData")
        kparams.addStringIfDefined("certificate", self.certificate)
        return kparams

    def getCertificate(self):
        return self.certificate

    def setCertificate(self, newCertificate):
        self.certificate = newCertificate


# @package Kaltura
# @subpackage Client
class KalturaHouseholdUser(KalturaObjectBase):
    """Household user"""

    def __init__(self,
            householdId=NotImplemented,
            userId=NotImplemented,
            isMaster=NotImplemented,
            householdMasterUsername=NotImplemented,
            status=NotImplemented,
            isDefault=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The identifier of the household
        # @var int
        self.householdId = householdId

        # The identifier of the user
        # @var string
        self.userId = userId

        # True if the user added as master use
        # @var bool
        self.isMaster = isMaster

        # The username of the household master for adding a user in status pending for the household master to approve
        # @var string
        # @insertonly
        self.householdMasterUsername = householdMasterUsername

        # The status of the user in the household
        # @var KalturaHouseholdUserStatus
        # @readonly
        self.status = status

        # True if the user is a default user
        # @var bool
        # @readonly
        self.isDefault = isDefault


    PROPERTY_LOADERS = {
        'householdId': getXmlNodeInt, 
        'userId': getXmlNodeText, 
        'isMaster': getXmlNodeBool, 
        'householdMasterUsername': getXmlNodeText, 
        'status': (KalturaEnumsFactory.createString, "KalturaHouseholdUserStatus"), 
        'isDefault': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdUser.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdUser")
        kparams.addIntIfDefined("householdId", self.householdId)
        kparams.addStringIfDefined("userId", self.userId)
        kparams.addBoolIfDefined("isMaster", self.isMaster)
        kparams.addStringIfDefined("householdMasterUsername", self.householdMasterUsername)
        return kparams

    def getHouseholdId(self):
        return self.householdId

    def setHouseholdId(self, newHouseholdId):
        self.householdId = newHouseholdId

    def getUserId(self):
        return self.userId

    def setUserId(self, newUserId):
        self.userId = newUserId

    def getIsMaster(self):
        return self.isMaster

    def setIsMaster(self, newIsMaster):
        self.isMaster = newIsMaster

    def getHouseholdMasterUsername(self):
        return self.householdMasterUsername

    def setHouseholdMasterUsername(self, newHouseholdMasterUsername):
        self.householdMasterUsername = newHouseholdMasterUsername

    def getStatus(self):
        return self.status

    def getIsDefault(self):
        return self.isDefault


# @package Kaltura
# @subpackage Client
class KalturaHouseholdUserListResponse(KalturaListResponse):
    """Household users list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Household users
        # @var array of KalturaHouseholdUser
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaHouseholdUser'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdUserListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaHouseholdUserListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaHomeNetwork(KalturaObjectBase):
    """Home network details"""

    def __init__(self,
            externalId=NotImplemented,
            name=NotImplemented,
            description=NotImplemented,
            isActive=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Home network identifier
        # @var string
        # @insertonly
        self.externalId = externalId

        # Home network name
        # @var string
        self.name = name

        # Home network description
        # @var string
        self.description = description

        # Is home network is active
        # @var bool
        self.isActive = isActive


    PROPERTY_LOADERS = {
        'externalId': getXmlNodeText, 
        'name': getXmlNodeText, 
        'description': getXmlNodeText, 
        'isActive': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHomeNetwork.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHomeNetwork")
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("description", self.description)
        kparams.addBoolIfDefined("isActive", self.isActive)
        return kparams

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive


# @package Kaltura
# @subpackage Client
class KalturaHomeNetworkListResponse(KalturaListResponse):
    """Home networks"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Home networks
        # @var array of KalturaHomeNetwork
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaHomeNetwork'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHomeNetworkListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaHomeNetworkListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaConfigurations(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            partnerId=NotImplemented,
            configurationGroupId=NotImplemented,
            appName=NotImplemented,
            clientVersion=NotImplemented,
            platform=NotImplemented,
            externalPushId=NotImplemented,
            isForceUpdate=NotImplemented,
            content=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Configuration id
        # @var string
        # @readonly
        self.id = id

        # Partner id
        # @var int
        # @readonly
        self.partnerId = partnerId

        # Configuration group id
        # @var string
        self.configurationGroupId = configurationGroupId

        # Application name
        # @var string
        self.appName = appName

        # Client version
        # @var string
        self.clientVersion = clientVersion

        # Platform: Android/iOS/WindowsPhone/Blackberry/STB/CTV/Other
        # @var KalturaPlatform
        self.platform = platform

        # External push id
        # @var string
        self.externalPushId = externalPushId

        # Is force update
        # @var bool
        self.isForceUpdate = isForceUpdate

        # Content
        # @var string
        self.content = content


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'partnerId': getXmlNodeInt, 
        'configurationGroupId': getXmlNodeText, 
        'appName': getXmlNodeText, 
        'clientVersion': getXmlNodeText, 
        'platform': (KalturaEnumsFactory.createString, "KalturaPlatform"), 
        'externalPushId': getXmlNodeText, 
        'isForceUpdate': getXmlNodeBool, 
        'content': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurations.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaConfigurations")
        kparams.addStringIfDefined("configurationGroupId", self.configurationGroupId)
        kparams.addStringIfDefined("appName", self.appName)
        kparams.addStringIfDefined("clientVersion", self.clientVersion)
        kparams.addStringEnumIfDefined("platform", self.platform)
        kparams.addStringIfDefined("externalPushId", self.externalPushId)
        kparams.addBoolIfDefined("isForceUpdate", self.isForceUpdate)
        kparams.addStringIfDefined("content", self.content)
        return kparams

    def getId(self):
        return self.id

    def getPartnerId(self):
        return self.partnerId

    def getConfigurationGroupId(self):
        return self.configurationGroupId

    def setConfigurationGroupId(self, newConfigurationGroupId):
        self.configurationGroupId = newConfigurationGroupId

    def getAppName(self):
        return self.appName

    def setAppName(self, newAppName):
        self.appName = newAppName

    def getClientVersion(self):
        return self.clientVersion

    def setClientVersion(self, newClientVersion):
        self.clientVersion = newClientVersion

    def getPlatform(self):
        return self.platform

    def setPlatform(self, newPlatform):
        self.platform = newPlatform

    def getExternalPushId(self):
        return self.externalPushId

    def setExternalPushId(self, newExternalPushId):
        self.externalPushId = newExternalPushId

    def getIsForceUpdate(self):
        return self.isForceUpdate

    def setIsForceUpdate(self, newIsForceUpdate):
        self.isForceUpdate = newIsForceUpdate

    def getContent(self):
        return self.content

    def setContent(self, newContent):
        self.content = newContent


# @package Kaltura
# @subpackage Client
class KalturaConfigurationsListResponse(KalturaListResponse):
    """Configurations info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Configurations
        # @var array of KalturaConfigurations
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaConfigurations'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationsListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaConfigurationsListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupDevice(KalturaObjectBase):
    def __init__(self,
            configurationGroupId=NotImplemented,
            partnerId=NotImplemented,
            udid=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Configuration group id
        # @var string
        self.configurationGroupId = configurationGroupId

        # Partner id
        # @var int
        # @readonly
        self.partnerId = partnerId

        # Device UDID
        # @var string
        self.udid = udid


    PROPERTY_LOADERS = {
        'configurationGroupId': getXmlNodeText, 
        'partnerId': getXmlNodeInt, 
        'udid': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupDevice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupDevice")
        kparams.addStringIfDefined("configurationGroupId", self.configurationGroupId)
        kparams.addStringIfDefined("udid", self.udid)
        return kparams

    def getConfigurationGroupId(self):
        return self.configurationGroupId

    def setConfigurationGroupId(self, newConfigurationGroupId):
        self.configurationGroupId = newConfigurationGroupId

    def getPartnerId(self):
        return self.partnerId

    def getUdid(self):
        return self.udid

    def setUdid(self, newUdid):
        self.udid = newUdid


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupDeviceListResponse(KalturaListResponse):
    """Configuration group devices info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Configuration group devices
        # @var array of KalturaConfigurationGroupDevice
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaConfigurationGroupDevice'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupDeviceListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupDeviceListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupTag(KalturaObjectBase):
    def __init__(self,
            configurationGroupId=NotImplemented,
            partnerId=NotImplemented,
            tag=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Configuration group identifier
        # @var string
        self.configurationGroupId = configurationGroupId

        # Partner identifier
        # @var int
        # @readonly
        self.partnerId = partnerId

        # Tag
        # @var string
        self.tag = tag


    PROPERTY_LOADERS = {
        'configurationGroupId': getXmlNodeText, 
        'partnerId': getXmlNodeInt, 
        'tag': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupTag.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupTag")
        kparams.addStringIfDefined("configurationGroupId", self.configurationGroupId)
        kparams.addStringIfDefined("tag", self.tag)
        return kparams

    def getConfigurationGroupId(self):
        return self.configurationGroupId

    def setConfigurationGroupId(self, newConfigurationGroupId):
        self.configurationGroupId = newConfigurationGroupId

    def getPartnerId(self):
        return self.partnerId

    def getTag(self):
        return self.tag

    def setTag(self, newTag):
        self.tag = newTag


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupTagListResponse(KalturaListResponse):
    """Configurations group tags info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Configuration group tags
        # @var array of KalturaConfigurationGroupTag
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaConfigurationGroupTag'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupTagListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupTagListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaConfigurationIdentifier(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Identifier
        # @var string
        self.id = id

        # Name
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationIdentifier.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaConfigurationIdentifier")
        kparams.addStringIfDefined("id", self.id)
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroup(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            partnerId=NotImplemented,
            isDefault=NotImplemented,
            tags=NotImplemented,
            numberOfDevices=NotImplemented,
            configurationIdentifiers=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Configuration group identifier
        # @var string
        # @readonly
        self.id = id

        # Configuration group name
        # @var string
        self.name = name

        # Partner id
        # @var int
        # @readonly
        self.partnerId = partnerId

        # Is default
        # @var bool
        # @insertonly
        self.isDefault = isDefault

        # tags
        # @var array of KalturaStringValue
        # @readonly
        self.tags = tags

        # Number of devices
        # @var int
        # @readonly
        self.numberOfDevices = numberOfDevices

        # Configuration identifiers
        # @var array of KalturaConfigurationIdentifier
        # @readonly
        self.configurationIdentifiers = configurationIdentifiers


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
        'partnerId': getXmlNodeInt, 
        'isDefault': getXmlNodeBool, 
        'tags': (KalturaObjectFactory.createArray, 'KalturaStringValue'), 
        'numberOfDevices': getXmlNodeInt, 
        'configurationIdentifiers': (KalturaObjectFactory.createArray, 'KalturaConfigurationIdentifier'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroup.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroup")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getPartnerId(self):
        return self.partnerId

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault

    def getTags(self):
        return self.tags

    def getNumberOfDevices(self):
        return self.numberOfDevices

    def getConfigurationIdentifiers(self):
        return self.configurationIdentifiers


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupListResponse(KalturaListResponse):
    """Configuration groups info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Configuration groups
        # @var array of KalturaConfigurationGroup
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaConfigurationGroup'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaUserInterestTopic(KalturaObjectBase):
    """User interest topic"""

    def __init__(self,
            metaId=NotImplemented,
            value=NotImplemented,
            parentTopic=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Meta identifier
        # @var string
        self.metaId = metaId

        # Meta Value
        # @var string
        self.value = value

        # Parent topic
        # @var KalturaUserInterestTopic
        self.parentTopic = parentTopic


    PROPERTY_LOADERS = {
        'metaId': getXmlNodeText, 
        'value': getXmlNodeText, 
        'parentTopic': (KalturaObjectFactory.create, 'KalturaObjectBase'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserInterestTopic.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserInterestTopic")
        kparams.addStringIfDefined("metaId", self.metaId)
        kparams.addStringIfDefined("value", self.value)
        kparams.addObjectIfDefined("parentTopic", self.parentTopic)
        return kparams

    def getMetaId(self):
        return self.metaId

    def setMetaId(self, newMetaId):
        self.metaId = newMetaId

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue

    def getParentTopic(self):
        return self.parentTopic

    def setParentTopic(self, newParentTopic):
        self.parentTopic = newParentTopic


# @package Kaltura
# @subpackage Client
class KalturaUserInterest(KalturaObjectBase):
    """User Interest"""

    def __init__(self,
            id=NotImplemented,
            topic=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Identifier
        # @var string
        self.id = id

        # Topic
        # @var KalturaUserInterestTopic
        self.topic = topic


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'topic': (KalturaObjectFactory.create, 'KalturaUserInterestTopic'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserInterest.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserInterest")
        kparams.addStringIfDefined("id", self.id)
        kparams.addObjectIfDefined("topic", self.topic)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getTopic(self):
        return self.topic

    def setTopic(self, newTopic):
        self.topic = newTopic


# @package Kaltura
# @subpackage Client
class KalturaUserInterestListResponse(KalturaListResponse):
    """User interest list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of UserInterests
        # @var array of KalturaUserInterest
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaUserInterest'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserInterestListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaUserInterestListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaMediaImage(KalturaObjectBase):
    """Image details"""

    def __init__(self,
            ratio=NotImplemented,
            width=NotImplemented,
            height=NotImplemented,
            url=NotImplemented,
            version=NotImplemented,
            id=NotImplemented,
            isDefault=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Image aspect ratio
        # @var string
        self.ratio = ratio

        # Image width
        # @var int
        self.width = width

        # Image height
        # @var int
        self.height = height

        # Image URL
        # @var string
        self.url = url

        # Image Version
        # @var int
        self.version = version

        # Image ID
        # @var string
        # @readonly
        self.id = id

        # Determined whether image was taken from default configuration or not
        # @var bool
        self.isDefault = isDefault


    PROPERTY_LOADERS = {
        'ratio': getXmlNodeText, 
        'width': getXmlNodeInt, 
        'height': getXmlNodeInt, 
        'url': getXmlNodeText, 
        'version': getXmlNodeInt, 
        'id': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMediaImage.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaMediaImage")
        kparams.addStringIfDefined("ratio", self.ratio)
        kparams.addIntIfDefined("width", self.width)
        kparams.addIntIfDefined("height", self.height)
        kparams.addStringIfDefined("url", self.url)
        kparams.addIntIfDefined("version", self.version)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        return kparams

    def getRatio(self):
        return self.ratio

    def setRatio(self, newRatio):
        self.ratio = newRatio

    def getWidth(self):
        return self.width

    def setWidth(self, newWidth):
        self.width = newWidth

    def getHeight(self):
        return self.height

    def setHeight(self, newHeight):
        self.height = newHeight

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl

    def getVersion(self):
        return self.version

    def setVersion(self, newVersion):
        self.version = newVersion

    def getId(self):
        return self.id

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault


# @package Kaltura
# @subpackage Client
class KalturaMediaFile(KalturaObjectBase):
    """Media file details"""

    def __init__(self,
            assetId=NotImplemented,
            id=NotImplemented,
            type=NotImplemented,
            url=NotImplemented,
            duration=NotImplemented,
            externalId=NotImplemented,
            fileSize=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique identifier for the asset
        # @var int
        self.assetId = assetId

        # File unique identifier
        # @var int
        # @readonly
        self.id = id

        # Device types as defined in the system
        # @var string
        self.type = type

        # URL of the media file to be played
        # @var string
        self.url = url

        # Duration of the media file
        # @var int
        self.duration = duration

        # External identifier for the media file
        # @var string
        self.externalId = externalId

        # File size
        # @var int
        self.fileSize = fileSize


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
        'id': getXmlNodeInt, 
        'type': getXmlNodeText, 
        'url': getXmlNodeText, 
        'duration': getXmlNodeInt, 
        'externalId': getXmlNodeText, 
        'fileSize': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMediaFile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaMediaFile")
        kparams.addIntIfDefined("assetId", self.assetId)
        kparams.addStringIfDefined("type", self.type)
        kparams.addStringIfDefined("url", self.url)
        kparams.addIntIfDefined("duration", self.duration)
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addIntIfDefined("fileSize", self.fileSize)
        return kparams

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl

    def getDuration(self):
        return self.duration

    def setDuration(self, newDuration):
        self.duration = newDuration

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getFileSize(self):
        return self.fileSize

    def setFileSize(self, newFileSize):
        self.fileSize = newFileSize


# @package Kaltura
# @subpackage Client
class KalturaBuzzScore(KalturaObjectBase):
    """Buzz score"""

    def __init__(self,
            normalizedAvgScore=NotImplemented,
            updateDate=NotImplemented,
            avgScore=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Normalized average score
        # @var float
        self.normalizedAvgScore = normalizedAvgScore

        # Update date
        # @var int
        self.updateDate = updateDate

        # Average score
        # @var float
        self.avgScore = avgScore


    PROPERTY_LOADERS = {
        'normalizedAvgScore': getXmlNodeFloat, 
        'updateDate': getXmlNodeInt, 
        'avgScore': getXmlNodeFloat, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBuzzScore.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaBuzzScore")
        kparams.addFloatIfDefined("normalizedAvgScore", self.normalizedAvgScore)
        kparams.addIntIfDefined("updateDate", self.updateDate)
        kparams.addFloatIfDefined("avgScore", self.avgScore)
        return kparams

    def getNormalizedAvgScore(self):
        return self.normalizedAvgScore

    def setNormalizedAvgScore(self, newNormalizedAvgScore):
        self.normalizedAvgScore = newNormalizedAvgScore

    def getUpdateDate(self):
        return self.updateDate

    def setUpdateDate(self, newUpdateDate):
        self.updateDate = newUpdateDate

    def getAvgScore(self):
        return self.avgScore

    def setAvgScore(self, newAvgScore):
        self.avgScore = newAvgScore


# @package Kaltura
# @subpackage Client
class KalturaAssetStatistics(KalturaObjectBase):
    """Asset statistics"""

    def __init__(self,
            assetId=NotImplemented,
            likes=NotImplemented,
            views=NotImplemented,
            ratingCount=NotImplemented,
            rating=NotImplemented,
            buzzScore=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique identifier for the asset
        # @var int
        self.assetId = assetId

        # Total number of likes for this asset
        # @var int
        self.likes = likes

        # Total number of views for this asset
        # @var int
        self.views = views

        # Number of people that rated the asset
        # @var int
        self.ratingCount = ratingCount

        # Average rating for the asset
        # @var float
        self.rating = rating

        # Buzz score
        # @var KalturaBuzzScore
        self.buzzScore = buzzScore


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
        'likes': getXmlNodeInt, 
        'views': getXmlNodeInt, 
        'ratingCount': getXmlNodeInt, 
        'rating': getXmlNodeFloat, 
        'buzzScore': (KalturaObjectFactory.create, 'KalturaBuzzScore'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetStatistics.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetStatistics")
        kparams.addIntIfDefined("assetId", self.assetId)
        kparams.addIntIfDefined("likes", self.likes)
        kparams.addIntIfDefined("views", self.views)
        kparams.addIntIfDefined("ratingCount", self.ratingCount)
        kparams.addFloatIfDefined("rating", self.rating)
        kparams.addObjectIfDefined("buzzScore", self.buzzScore)
        return kparams

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId

    def getLikes(self):
        return self.likes

    def setLikes(self, newLikes):
        self.likes = newLikes

    def getViews(self):
        return self.views

    def setViews(self, newViews):
        self.views = newViews

    def getRatingCount(self):
        return self.ratingCount

    def setRatingCount(self, newRatingCount):
        self.ratingCount = newRatingCount

    def getRating(self):
        return self.rating

    def setRating(self, newRating):
        self.rating = newRating

    def getBuzzScore(self):
        return self.buzzScore

    def setBuzzScore(self, newBuzzScore):
        self.buzzScore = newBuzzScore


# @package Kaltura
# @subpackage Client
class KalturaMultilingualStringValueArray(KalturaObjectBase):
    """Array of translated strings"""

    def __init__(self,
            objects=NotImplemented):
        KalturaObjectBase.__init__(self)

        # List of string values
        # @var array of KalturaMultilingualStringValue
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaMultilingualStringValue'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMultilingualStringValueArray.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaMultilingualStringValueArray")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaFavorite(KalturaObjectBase):
    """Favorite details"""

    def __init__(self,
            assetId=NotImplemented,
            extraData=NotImplemented,
            createDate=NotImplemented):
        KalturaObjectBase.__init__(self)

        # AssetInfo Model
        # @var int
        self.assetId = assetId

        # Extra Value
        # @var string
        self.extraData = extraData

        # Specifies when was the favorite created. Date and time represented as epoch.
        # @var int
        # @readonly
        self.createDate = createDate


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
        'extraData': getXmlNodeText, 
        'createDate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFavorite.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaFavorite")
        kparams.addIntIfDefined("assetId", self.assetId)
        kparams.addStringIfDefined("extraData", self.extraData)
        return kparams

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId

    def getExtraData(self):
        return self.extraData

    def setExtraData(self, newExtraData):
        self.extraData = newExtraData

    def getCreateDate(self):
        return self.createDate


# @package Kaltura
# @subpackage Client
class KalturaFavoriteListResponse(KalturaListResponse):
    """Favorite list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of favorites
        # @var array of KalturaFavorite
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaFavorite'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFavoriteListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaFavoriteListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaPlaybackSource(KalturaMediaFile):
    def __init__(self,
            assetId=NotImplemented,
            id=NotImplemented,
            type=NotImplemented,
            url=NotImplemented,
            duration=NotImplemented,
            externalId=NotImplemented,
            fileSize=NotImplemented,
            format=NotImplemented,
            protocols=NotImplemented,
            drm=NotImplemented):
        KalturaMediaFile.__init__(self,
            assetId,
            id,
            type,
            url,
            duration,
            externalId,
            fileSize)

        # Source format according to delivery profile streamer type (applehttp, mpegdash etc.)
        # @var string
        self.format = format

        # Comma separated string according to deliveryProfile media protocols (&#39;http,https&#39; etc.)
        # @var string
        self.protocols = protocols

        # DRM data object containing relevant license URL ,scheme name and certificate
        # @var array of KalturaDrmPlaybackPluginData
        self.drm = drm


    PROPERTY_LOADERS = {
        'format': getXmlNodeText, 
        'protocols': getXmlNodeText, 
        'drm': (KalturaObjectFactory.createArray, 'KalturaDrmPlaybackPluginData'), 
    }

    def fromXml(self, node):
        KalturaMediaFile.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPlaybackSource.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaMediaFile.toParams(self)
        kparams.put("objectType", "KalturaPlaybackSource")
        kparams.addStringIfDefined("format", self.format)
        kparams.addStringIfDefined("protocols", self.protocols)
        kparams.addArrayIfDefined("drm", self.drm)
        return kparams

    def getFormat(self):
        return self.format

    def setFormat(self, newFormat):
        self.format = newFormat

    def getProtocols(self):
        return self.protocols

    def setProtocols(self, newProtocols):
        self.protocols = newProtocols

    def getDrm(self):
        return self.drm

    def setDrm(self, newDrm):
        self.drm = newDrm


# @package Kaltura
# @subpackage Client
class KalturaBaseOTTUser(KalturaObjectBase):
    """Slim user data"""

    def __init__(self,
            id=NotImplemented,
            username=NotImplemented,
            firstName=NotImplemented,
            lastName=NotImplemented):
        KalturaObjectBase.__init__(self)

        # User identifier
        # @var string
        # @readonly
        self.id = id

        # Username
        # @var string
        self.username = username

        # First name
        # @var string
        self.firstName = firstName

        # Last name
        # @var string
        self.lastName = lastName


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'username': getXmlNodeText, 
        'firstName': getXmlNodeText, 
        'lastName': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBaseOTTUser.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaBaseOTTUser")
        kparams.addStringIfDefined("username", self.username)
        kparams.addStringIfDefined("firstName", self.firstName)
        kparams.addStringIfDefined("lastName", self.lastName)
        return kparams

    def getId(self):
        return self.id

    def getUsername(self):
        return self.username

    def setUsername(self, newUsername):
        self.username = newUsername

    def getFirstName(self):
        return self.firstName

    def setFirstName(self, newFirstName):
        self.firstName = newFirstName

    def getLastName(self):
        return self.lastName

    def setLastName(self, newLastName):
        self.lastName = newLastName


# @package Kaltura
# @subpackage Client
class KalturaCountry(KalturaObjectBase):
    """Country details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            code=NotImplemented,
            mainLanguageCode=NotImplemented,
            languagesCode=NotImplemented,
            currency=NotImplemented,
            currencySign=NotImplemented,
            vatPercent=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Country identifier
        # @var int
        # @readonly
        self.id = id

        # Country name
        # @var string
        self.name = name

        # Country code
        # @var string
        self.code = code

        # The main language code in the country
        # @var string
        self.mainLanguageCode = mainLanguageCode

        # All the languages code that are supported in the country
        # @var string
        self.languagesCode = languagesCode

        # Currency code
        # @var string
        self.currency = currency

        # Currency Sign
        # @var string
        self.currencySign = currencySign

        # Vat Percent in the country
        # @var float
        self.vatPercent = vatPercent


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'code': getXmlNodeText, 
        'mainLanguageCode': getXmlNodeText, 
        'languagesCode': getXmlNodeText, 
        'currency': getXmlNodeText, 
        'currencySign': getXmlNodeText, 
        'vatPercent': getXmlNodeFloat, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCountry.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCountry")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("code", self.code)
        kparams.addStringIfDefined("mainLanguageCode", self.mainLanguageCode)
        kparams.addStringIfDefined("languagesCode", self.languagesCode)
        kparams.addStringIfDefined("currency", self.currency)
        kparams.addStringIfDefined("currencySign", self.currencySign)
        kparams.addFloatIfDefined("vatPercent", self.vatPercent)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getCode(self):
        return self.code

    def setCode(self, newCode):
        self.code = newCode

    def getMainLanguageCode(self):
        return self.mainLanguageCode

    def setMainLanguageCode(self, newMainLanguageCode):
        self.mainLanguageCode = newMainLanguageCode

    def getLanguagesCode(self):
        return self.languagesCode

    def setLanguagesCode(self, newLanguagesCode):
        self.languagesCode = newLanguagesCode

    def getCurrency(self):
        return self.currency

    def setCurrency(self, newCurrency):
        self.currency = newCurrency

    def getCurrencySign(self):
        return self.currencySign

    def setCurrencySign(self, newCurrencySign):
        self.currencySign = newCurrencySign

    def getVatPercent(self):
        return self.vatPercent

    def setVatPercent(self, newVatPercent):
        self.vatPercent = newVatPercent


# @package Kaltura
# @subpackage Client
class KalturaOTTUserType(KalturaObjectBase):
    """User type"""

    def __init__(self,
            id=NotImplemented,
            description=NotImplemented):
        KalturaObjectBase.__init__(self)

        # User type identifier
        # @var int
        # @readonly
        self.id = id

        # User type description
        # @var string
        self.description = description


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'description': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOTTUserType.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaOTTUserType")
        kparams.addStringIfDefined("description", self.description)
        return kparams

    def getId(self):
        return self.id

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription


# @package Kaltura
# @subpackage Client
class KalturaOTTUser(KalturaBaseOTTUser):
    """User"""

    def __init__(self,
            id=NotImplemented,
            username=NotImplemented,
            firstName=NotImplemented,
            lastName=NotImplemented,
            householdId=NotImplemented,
            email=NotImplemented,
            address=NotImplemented,
            city=NotImplemented,
            countryId=NotImplemented,
            zip=NotImplemented,
            phone=NotImplemented,
            affiliateCode=NotImplemented,
            externalId=NotImplemented,
            userType=NotImplemented,
            dynamicData=NotImplemented,
            isHouseholdMaster=NotImplemented,
            suspensionState=NotImplemented,
            userState=NotImplemented):
        KalturaBaseOTTUser.__init__(self,
            id,
            username,
            firstName,
            lastName)

        # Household identifier
        # @var int
        # @readonly
        self.householdId = householdId

        # Email
        # @var string
        self.email = email

        # Address
        # @var string
        self.address = address

        # City
        # @var string
        self.city = city

        # Country identifier
        # @var int
        self.countryId = countryId

        # Zip code
        # @var string
        self.zip = zip

        # Phone
        # @var string
        self.phone = phone

        # Affiliate code
        # @var string
        # @insertonly
        self.affiliateCode = affiliateCode

        # External user identifier
        # @var string
        self.externalId = externalId

        # User type
        # @var KalturaOTTUserType
        self.userType = userType

        # Dynamic data
        # @var map
        self.dynamicData = dynamicData

        # Is the user the household master
        # @var bool
        # @readonly
        self.isHouseholdMaster = isHouseholdMaster

        # Suspension state
        # @var KalturaHouseholdSuspensionState
        # @readonly
        self.suspensionState = suspensionState

        # User state
        # @var KalturaUserState
        # @readonly
        self.userState = userState


    PROPERTY_LOADERS = {
        'householdId': getXmlNodeInt, 
        'email': getXmlNodeText, 
        'address': getXmlNodeText, 
        'city': getXmlNodeText, 
        'countryId': getXmlNodeInt, 
        'zip': getXmlNodeText, 
        'phone': getXmlNodeText, 
        'affiliateCode': getXmlNodeText, 
        'externalId': getXmlNodeText, 
        'userType': (KalturaObjectFactory.create, 'KalturaOTTUserType'), 
        'dynamicData': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'isHouseholdMaster': getXmlNodeBool, 
        'suspensionState': (KalturaEnumsFactory.createString, "KalturaHouseholdSuspensionState"), 
        'userState': (KalturaEnumsFactory.createString, "KalturaUserState"), 
    }

    def fromXml(self, node):
        KalturaBaseOTTUser.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOTTUser.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaBaseOTTUser.toParams(self)
        kparams.put("objectType", "KalturaOTTUser")
        kparams.addStringIfDefined("email", self.email)
        kparams.addStringIfDefined("address", self.address)
        kparams.addStringIfDefined("city", self.city)
        kparams.addIntIfDefined("countryId", self.countryId)
        kparams.addStringIfDefined("zip", self.zip)
        kparams.addStringIfDefined("phone", self.phone)
        kparams.addStringIfDefined("affiliateCode", self.affiliateCode)
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addObjectIfDefined("userType", self.userType)
        kparams.addMapIfDefined("dynamicData", self.dynamicData)
        return kparams

    def getHouseholdId(self):
        return self.householdId

    def getEmail(self):
        return self.email

    def setEmail(self, newEmail):
        self.email = newEmail

    def getAddress(self):
        return self.address

    def setAddress(self, newAddress):
        self.address = newAddress

    def getCity(self):
        return self.city

    def setCity(self, newCity):
        self.city = newCity

    def getCountryId(self):
        return self.countryId

    def setCountryId(self, newCountryId):
        self.countryId = newCountryId

    def getZip(self):
        return self.zip

    def setZip(self, newZip):
        self.zip = newZip

    def getPhone(self):
        return self.phone

    def setPhone(self, newPhone):
        self.phone = newPhone

    def getAffiliateCode(self):
        return self.affiliateCode

    def setAffiliateCode(self, newAffiliateCode):
        self.affiliateCode = newAffiliateCode

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getUserType(self):
        return self.userType

    def setUserType(self, newUserType):
        self.userType = newUserType

    def getDynamicData(self):
        return self.dynamicData

    def setDynamicData(self, newDynamicData):
        self.dynamicData = newDynamicData

    def getIsHouseholdMaster(self):
        return self.isHouseholdMaster

    def getSuspensionState(self):
        return self.suspensionState

    def getUserState(self):
        return self.userState


# @package Kaltura
# @subpackage Client
class KalturaOTTUserListResponse(KalturaListResponse):
    """Users list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of users
        # @var array of KalturaOTTUser
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaOTTUser'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOTTUserListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaOTTUserListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaBaseChannel(KalturaObjectBase):
    """Slim channel"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique identifier for the channel
        # @var int
        # @readonly
        self.id = id

        # Channel name
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBaseChannel.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaBaseChannel")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaDiscountModule(KalturaObjectBase):
    """Discount module"""

    def __init__(self,
            percent=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The discount percentage
        # @var float
        self.percent = percent

        # The first date the discount is available
        # @var int
        self.startDate = startDate

        # The last date the discount is available
        # @var int
        self.endDate = endDate


    PROPERTY_LOADERS = {
        'percent': getXmlNodeFloat, 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDiscountModule.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaDiscountModule")
        kparams.addFloatIfDefined("percent", self.percent)
        kparams.addIntIfDefined("startDate", self.startDate)
        kparams.addIntIfDefined("endDate", self.endDate)
        return kparams

    def getPercent(self):
        return self.percent

    def setPercent(self, newPercent):
        self.percent = newPercent

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate


# @package Kaltura
# @subpackage Client
class KalturaUsageModule(KalturaObjectBase):
    """Pricing usage module"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            maxViewsNumber=NotImplemented,
            viewLifeCycle=NotImplemented,
            fullLifeCycle=NotImplemented,
            couponId=NotImplemented,
            waiverPeriod=NotImplemented,
            isWaiverEnabled=NotImplemented,
            isOfflinePlayback=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Usage module identifier
        # @var int
        # @readonly
        self.id = id

        # Usage module name
        # @var string
        # @readonly
        self.name = name

        # The maximum number of times an item in this usage module can be viewed
        # @var int
        # @readonly
        self.maxViewsNumber = maxViewsNumber

        # The amount time an item is available for viewing since a user started watching the item
        # @var int
        # @readonly
        self.viewLifeCycle = viewLifeCycle

        # The amount time an item is available for viewing
        # @var int
        # @readonly
        self.fullLifeCycle = fullLifeCycle

        # Identifies a specific coupon linked to this object
        # @var int
        # @readonly
        self.couponId = couponId

        # Time period during which the end user can waive his rights to cancel a purchase. When the time period is passed, the purchase can no longer be cancelled
        # @var int
        # @readonly
        self.waiverPeriod = waiverPeriod

        # Indicates whether or not the end user has the right to waive his rights to cancel a purchase
        # @var bool
        # @readonly
        self.isWaiverEnabled = isWaiverEnabled

        # Indicates that usage is targeted for offline playback
        # @var bool
        # @readonly
        self.isOfflinePlayback = isOfflinePlayback


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'maxViewsNumber': getXmlNodeInt, 
        'viewLifeCycle': getXmlNodeInt, 
        'fullLifeCycle': getXmlNodeInt, 
        'couponId': getXmlNodeInt, 
        'waiverPeriod': getXmlNodeInt, 
        'isWaiverEnabled': getXmlNodeBool, 
        'isOfflinePlayback': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUsageModule.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUsageModule")
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getMaxViewsNumber(self):
        return self.maxViewsNumber

    def getViewLifeCycle(self):
        return self.viewLifeCycle

    def getFullLifeCycle(self):
        return self.fullLifeCycle

    def getCouponId(self):
        return self.couponId

    def getWaiverPeriod(self):
        return self.waiverPeriod

    def getIsWaiverEnabled(self):
        return self.isWaiverEnabled

    def getIsOfflinePlayback(self):
        return self.isOfflinePlayback


# @package Kaltura
# @subpackage Client
class KalturaCouponsGroup(KalturaObjectBase):
    """Coupons group details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            descriptions=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            maxUsesNumber=NotImplemented,
            maxUsesNumberOnRenewableSub=NotImplemented,
            couponGroupType=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Coupon group identifier
        # @var string
        # @readonly
        self.id = id

        # Coupon group name
        # @var string
        self.name = name

        # A list of the descriptions of the coupon group on different languages (language code and translation)
        # @var array of KalturaTranslationToken
        self.descriptions = descriptions

        # The first date the coupons in this coupons group are valid
        # @var int
        self.startDate = startDate

        # The last date the coupons in this coupons group are valid
        # @var int
        self.endDate = endDate

        # Maximum number of uses for each coupon in the group
        # @var int
        self.maxUsesNumber = maxUsesNumber

        # Maximum number of uses for each coupon in the group on a renewable subscription
        # @var int
        self.maxUsesNumberOnRenewableSub = maxUsesNumberOnRenewableSub

        # Type of the coupon group
        # @var KalturaCouponGroupType
        self.couponGroupType = couponGroupType


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
        'descriptions': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'maxUsesNumber': getXmlNodeInt, 
        'maxUsesNumberOnRenewableSub': getXmlNodeInt, 
        'couponGroupType': (KalturaEnumsFactory.createString, "KalturaCouponGroupType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCouponsGroup.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCouponsGroup")
        kparams.addStringIfDefined("name", self.name)
        kparams.addArrayIfDefined("descriptions", self.descriptions)
        kparams.addIntIfDefined("startDate", self.startDate)
        kparams.addIntIfDefined("endDate", self.endDate)
        kparams.addIntIfDefined("maxUsesNumber", self.maxUsesNumber)
        kparams.addIntIfDefined("maxUsesNumberOnRenewableSub", self.maxUsesNumberOnRenewableSub)
        kparams.addStringEnumIfDefined("couponGroupType", self.couponGroupType)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDescriptions(self):
        return self.descriptions

    def setDescriptions(self, newDescriptions):
        self.descriptions = newDescriptions

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate

    def getMaxUsesNumber(self):
        return self.maxUsesNumber

    def setMaxUsesNumber(self, newMaxUsesNumber):
        self.maxUsesNumber = newMaxUsesNumber

    def getMaxUsesNumberOnRenewableSub(self):
        return self.maxUsesNumberOnRenewableSub

    def setMaxUsesNumberOnRenewableSub(self, newMaxUsesNumberOnRenewableSub):
        self.maxUsesNumberOnRenewableSub = newMaxUsesNumberOnRenewableSub

    def getCouponGroupType(self):
        return self.couponGroupType

    def setCouponGroupType(self, newCouponGroupType):
        self.couponGroupType = newCouponGroupType


# @package Kaltura
# @subpackage Client
class KalturaProductCode(KalturaObjectBase):
    """Product Code"""

    def __init__(self,
            inappProvider=NotImplemented,
            code=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Provider Name
        # @var string
        self.inappProvider = inappProvider

        # Product Code
        # @var string
        self.code = code


    PROPERTY_LOADERS = {
        'inappProvider': getXmlNodeText, 
        'code': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaProductCode.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaProductCode")
        kparams.addStringIfDefined("inappProvider", self.inappProvider)
        kparams.addStringIfDefined("code", self.code)
        return kparams

    def getInappProvider(self):
        return self.inappProvider

    def setInappProvider(self, newInappProvider):
        self.inappProvider = newInappProvider

    def getCode(self):
        return self.code

    def setCode(self, newCode):
        self.code = newCode


# @package Kaltura
# @subpackage Client
class KalturaCollection(KalturaObjectBase):
    """Collection"""

    def __init__(self,
            id=NotImplemented,
            channels=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            discountModule=NotImplemented,
            name=NotImplemented,
            multilingualName=NotImplemented,
            description=NotImplemented,
            multilingualDescription=NotImplemented,
            usageModule=NotImplemented,
            couponsGroups=NotImplemented,
            externalId=NotImplemented,
            productCodes=NotImplemented,
            priceDetailsId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Collection identifier
        # @var string
        self.id = id

        # A list of channels associated with this collection
        # @var array of KalturaBaseChannel
        self.channels = channels

        # The first date the collection is available for purchasing
        # @var int
        self.startDate = startDate

        # The last date the collection is available for purchasing
        # @var int
        self.endDate = endDate

        # The internal discount module for the subscription
        # @var KalturaDiscountModule
        self.discountModule = discountModule

        # Name of the subscription
        # @var string
        # @readonly
        self.name = name

        # Name of the subscription
        # @var array of KalturaTranslationToken
        self.multilingualName = multilingualName

        # description of the subscription
        # @var string
        # @readonly
        self.description = description

        # description of the subscription
        # @var array of KalturaTranslationToken
        self.multilingualDescription = multilingualDescription

        # Collection usage module
        # @var KalturaUsageModule
        self.usageModule = usageModule

        # List of Coupons group
        # @var array of KalturaCouponsGroup
        self.couponsGroups = couponsGroups

        # External ID
        # @var string
        self.externalId = externalId

        # List of Collection product codes
        # @var array of KalturaProductCode
        self.productCodes = productCodes

        # The ID of the price details associated with this collection
        # @var int
        self.priceDetailsId = priceDetailsId


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'channels': (KalturaObjectFactory.createArray, 'KalturaBaseChannel'), 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'discountModule': (KalturaObjectFactory.create, 'KalturaDiscountModule'), 
        'name': getXmlNodeText, 
        'multilingualName': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'description': getXmlNodeText, 
        'multilingualDescription': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'usageModule': (KalturaObjectFactory.create, 'KalturaUsageModule'), 
        'couponsGroups': (KalturaObjectFactory.createArray, 'KalturaCouponsGroup'), 
        'externalId': getXmlNodeText, 
        'productCodes': (KalturaObjectFactory.createArray, 'KalturaProductCode'), 
        'priceDetailsId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCollection.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCollection")
        kparams.addStringIfDefined("id", self.id)
        kparams.addArrayIfDefined("channels", self.channels)
        kparams.addIntIfDefined("startDate", self.startDate)
        kparams.addIntIfDefined("endDate", self.endDate)
        kparams.addObjectIfDefined("discountModule", self.discountModule)
        kparams.addArrayIfDefined("multilingualName", self.multilingualName)
        kparams.addArrayIfDefined("multilingualDescription", self.multilingualDescription)
        kparams.addObjectIfDefined("usageModule", self.usageModule)
        kparams.addArrayIfDefined("couponsGroups", self.couponsGroups)
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addArrayIfDefined("productCodes", self.productCodes)
        kparams.addIntIfDefined("priceDetailsId", self.priceDetailsId)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getChannels(self):
        return self.channels

    def setChannels(self, newChannels):
        self.channels = newChannels

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate

    def getDiscountModule(self):
        return self.discountModule

    def setDiscountModule(self, newDiscountModule):
        self.discountModule = newDiscountModule

    def getName(self):
        return self.name

    def getMultilingualName(self):
        return self.multilingualName

    def setMultilingualName(self, newMultilingualName):
        self.multilingualName = newMultilingualName

    def getDescription(self):
        return self.description

    def getMultilingualDescription(self):
        return self.multilingualDescription

    def setMultilingualDescription(self, newMultilingualDescription):
        self.multilingualDescription = newMultilingualDescription

    def getUsageModule(self):
        return self.usageModule

    def setUsageModule(self, newUsageModule):
        self.usageModule = newUsageModule

    def getCouponsGroups(self):
        return self.couponsGroups

    def setCouponsGroups(self, newCouponsGroups):
        self.couponsGroups = newCouponsGroups

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getProductCodes(self):
        return self.productCodes

    def setProductCodes(self, newProductCodes):
        self.productCodes = newProductCodes

    def getPriceDetailsId(self):
        return self.priceDetailsId

    def setPriceDetailsId(self, newPriceDetailsId):
        self.priceDetailsId = newPriceDetailsId


# @package Kaltura
# @subpackage Client
class KalturaCollectionListResponse(KalturaListResponse):
    """Collections list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of collections
        # @var array of KalturaCollection
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaCollection'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCollectionListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaCollectionListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaAssetGroupBy(KalturaObjectBase):
    """Abstarct class - represents an asset parameter that can be used for grouping"""

    def __init__(self):
        KalturaObjectBase.__init__(self)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetGroupBy.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetGroupBy")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaChannel(KalturaBaseChannel):
    """Channel details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            description=NotImplemented,
            images=NotImplemented,
            assetTypes=NotImplemented,
            filterExpression=NotImplemented,
            isActive=NotImplemented,
            order=NotImplemented,
            groupBy=NotImplemented):
        KalturaBaseChannel.__init__(self,
            id,
            name)

        # Cannel description
        # @var string
        self.description = description

        # Channel images
        # @var array of KalturaMediaImage
        self.images = images

        # Asset types in the channel.
        #             -26 is EPG
        # @var array of KalturaIntegerValue
        self.assetTypes = assetTypes

        # Filter expression
        # @var string
        self.filterExpression = filterExpression

        # active status
        # @var bool
        self.isActive = isActive

        # Channel order
        # @var KalturaAssetOrderBy
        self.order = order

        # Channel group by
        # @var KalturaAssetGroupBy
        self.groupBy = groupBy


    PROPERTY_LOADERS = {
        'description': getXmlNodeText, 
        'images': (KalturaObjectFactory.createArray, 'KalturaMediaImage'), 
        'assetTypes': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
        'filterExpression': getXmlNodeText, 
        'isActive': getXmlNodeBool, 
        'order': (KalturaEnumsFactory.createString, "KalturaAssetOrderBy"), 
        'groupBy': (KalturaObjectFactory.create, 'KalturaAssetGroupBy'), 
    }

    def fromXml(self, node):
        KalturaBaseChannel.fromXml(self, node)
        self.fromXmlImpl(node, KalturaChannel.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaBaseChannel.toParams(self)
        kparams.put("objectType", "KalturaChannel")
        kparams.addStringIfDefined("description", self.description)
        kparams.addArrayIfDefined("images", self.images)
        kparams.addArrayIfDefined("assetTypes", self.assetTypes)
        kparams.addStringIfDefined("filterExpression", self.filterExpression)
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringEnumIfDefined("order", self.order)
        kparams.addObjectIfDefined("groupBy", self.groupBy)
        return kparams

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription

    def getImages(self):
        return self.images

    def setImages(self, newImages):
        self.images = newImages

    def getAssetTypes(self):
        return self.assetTypes

    def setAssetTypes(self, newAssetTypes):
        self.assetTypes = newAssetTypes

    def getFilterExpression(self):
        return self.filterExpression

    def setFilterExpression(self, newFilterExpression):
        self.filterExpression = newFilterExpression

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getOrder(self):
        return self.order

    def setOrder(self, newOrder):
        self.order = newOrder

    def getGroupBy(self):
        return self.groupBy

    def setGroupBy(self, newGroupBy):
        self.groupBy = newGroupBy


# @package Kaltura
# @subpackage Client
class KalturaAssetMetaOrTagGroupBy(KalturaAssetGroupBy):
    """Group by a tag or meta - according to the name that appears in the system (similar to KSQL)"""

    def __init__(self,
            value=NotImplemented):
        KalturaAssetGroupBy.__init__(self)

        # Group by a tag or meta - according to the name that appears in the system (similar to KSQL)
        # @var string
        self.value = value


    PROPERTY_LOADERS = {
        'value': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaAssetGroupBy.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetMetaOrTagGroupBy.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetGroupBy.toParams(self)
        kparams.put("objectType", "KalturaAssetMetaOrTagGroupBy")
        kparams.addStringIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaAssetFieldGroupBy(KalturaAssetGroupBy):
    """Group by a field that is defined in enum"""

    def __init__(self,
            value=NotImplemented):
        KalturaAssetGroupBy.__init__(self)

        # Group by a specific field that is defined in enum
        # @var KalturaGroupByField
        self.value = value


    PROPERTY_LOADERS = {
        'value': (KalturaEnumsFactory.createString, "KalturaGroupByField"), 
    }

    def fromXml(self, node):
        KalturaAssetGroupBy.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetFieldGroupBy.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetGroupBy.toParams(self)
        kparams.put("objectType", "KalturaAssetFieldGroupBy")
        kparams.addStringEnumIfDefined("value", self.value)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaPricePlan(KalturaUsageModule):
    """Price plan"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            maxViewsNumber=NotImplemented,
            viewLifeCycle=NotImplemented,
            fullLifeCycle=NotImplemented,
            couponId=NotImplemented,
            waiverPeriod=NotImplemented,
            isWaiverEnabled=NotImplemented,
            isOfflinePlayback=NotImplemented,
            isRenewable=NotImplemented,
            renewalsNumber=NotImplemented,
            discountId=NotImplemented,
            priceDetailsId=NotImplemented):
        KalturaUsageModule.__init__(self,
            id,
            name,
            maxViewsNumber,
            viewLifeCycle,
            fullLifeCycle,
            couponId,
            waiverPeriod,
            isWaiverEnabled,
            isOfflinePlayback)

        # Denotes whether or not this object can be renewed
        # @var bool
        # @readonly
        self.isRenewable = isRenewable

        # Defines the number of times the module will be renewed (for the life_cycle period)
        # @var int
        # @readonly
        self.renewalsNumber = renewalsNumber

        # The discount module identifier of the price plan
        # @var int
        # @readonly
        self.discountId = discountId

        # The ID of the price details associated with this price plan
        # @var int
        self.priceDetailsId = priceDetailsId


    PROPERTY_LOADERS = {
        'isRenewable': getXmlNodeBool, 
        'renewalsNumber': getXmlNodeInt, 
        'discountId': getXmlNodeInt, 
        'priceDetailsId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaUsageModule.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPricePlan.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaUsageModule.toParams(self)
        kparams.put("objectType", "KalturaPricePlan")
        kparams.addIntIfDefined("priceDetailsId", self.priceDetailsId)
        return kparams

    def getIsRenewable(self):
        return self.isRenewable

    def getRenewalsNumber(self):
        return self.renewalsNumber

    def getDiscountId(self):
        return self.discountId

    def getPriceDetailsId(self):
        return self.priceDetailsId

    def setPriceDetailsId(self, newPriceDetailsId):
        self.priceDetailsId = newPriceDetailsId


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSet(KalturaObjectBase):
    """Subscription details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            type=NotImplemented,
            subscriptionIds=NotImplemented):
        KalturaObjectBase.__init__(self)

        # SubscriptionSet identifier
        # @var int
        # @readonly
        self.id = id

        # SubscriptionSet name
        # @var string
        self.name = name

        # Type of the Subscription Set
        # @var KalturaSubscriptionSetType
        # @readonly
        self.type = type

        # A list of comma separated subscription ids associated with this set ordered by priority ascending
        # @var string
        self.subscriptionIds = subscriptionIds


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'type': (KalturaEnumsFactory.createString, "KalturaSubscriptionSetType"), 
        'subscriptionIds': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionSet.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionSet")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("subscriptionIds", self.subscriptionIds)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getType(self):
        return self.type

    def getSubscriptionIds(self):
        return self.subscriptionIds

    def setSubscriptionIds(self, newSubscriptionIds):
        self.subscriptionIds = newSubscriptionIds


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSetListResponse(KalturaListResponse):
    """SubscriptionSets list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of subscriptionSets
        # @var array of KalturaSubscriptionSet
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSubscriptionSet'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionSetListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionSetListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionDependencySet(KalturaSubscriptionSet):
    """Subscription Dependency Set"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            type=NotImplemented,
            subscriptionIds=NotImplemented,
            baseSubscriptionId=NotImplemented):
        KalturaSubscriptionSet.__init__(self,
            id,
            name,
            type,
            subscriptionIds)

        # Base Subscription identifier
        # @var int
        self.baseSubscriptionId = baseSubscriptionId


    PROPERTY_LOADERS = {
        'baseSubscriptionId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaSubscriptionSet.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionDependencySet.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSubscriptionSet.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionDependencySet")
        kparams.addIntIfDefined("baseSubscriptionId", self.baseSubscriptionId)
        return kparams

    def getBaseSubscriptionId(self):
        return self.baseSubscriptionId

    def setBaseSubscriptionId(self, newBaseSubscriptionId):
        self.baseSubscriptionId = newBaseSubscriptionId


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSwitchSet(KalturaSubscriptionSet):
    """Subscription details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            type=NotImplemented,
            subscriptionIds=NotImplemented):
        KalturaSubscriptionSet.__init__(self,
            id,
            name,
            type,
            subscriptionIds)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaSubscriptionSet.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionSwitchSet.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSubscriptionSet.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionSwitchSet")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPrice(KalturaObjectBase):
    """Price"""

    def __init__(self,
            amount=NotImplemented,
            currency=NotImplemented,
            currencySign=NotImplemented,
            countryId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Price
        # @var float
        self.amount = amount

        # Currency
        # @var string
        self.currency = currency

        # Currency Sign
        # @var string
        self.currencySign = currencySign

        # Country ID
        # @var int
        self.countryId = countryId


    PROPERTY_LOADERS = {
        'amount': getXmlNodeFloat, 
        'currency': getXmlNodeText, 
        'currencySign': getXmlNodeText, 
        'countryId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPrice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPrice")
        kparams.addFloatIfDefined("amount", self.amount)
        kparams.addStringIfDefined("currency", self.currency)
        kparams.addStringIfDefined("currencySign", self.currencySign)
        kparams.addIntIfDefined("countryId", self.countryId)
        return kparams

    def getAmount(self):
        return self.amount

    def setAmount(self, newAmount):
        self.amount = newAmount

    def getCurrency(self):
        return self.currency

    def setCurrency(self, newCurrency):
        self.currency = newCurrency

    def getCurrencySign(self):
        return self.currencySign

    def setCurrencySign(self, newCurrencySign):
        self.currencySign = newCurrencySign

    def getCountryId(self):
        return self.countryId

    def setCountryId(self, newCountryId):
        self.countryId = newCountryId


# @package Kaltura
# @subpackage Client
class KalturaProductPrice(KalturaObjectBase):
    def __init__(self,
            productId=NotImplemented,
            productType=NotImplemented,
            price=NotImplemented,
            purchaseStatus=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Product identifier
        # @var string
        self.productId = productId

        # Product Type
        # @var KalturaTransactionType
        self.productType = productType

        # Product price
        # @var KalturaPrice
        self.price = price

        # Product purchase status
        # @var KalturaPurchaseStatus
        self.purchaseStatus = purchaseStatus


    PROPERTY_LOADERS = {
        'productId': getXmlNodeText, 
        'productType': (KalturaEnumsFactory.createString, "KalturaTransactionType"), 
        'price': (KalturaObjectFactory.create, 'KalturaPrice'), 
        'purchaseStatus': (KalturaEnumsFactory.createString, "KalturaPurchaseStatus"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaProductPrice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaProductPrice")
        kparams.addStringIfDefined("productId", self.productId)
        kparams.addStringEnumIfDefined("productType", self.productType)
        kparams.addObjectIfDefined("price", self.price)
        kparams.addStringEnumIfDefined("purchaseStatus", self.purchaseStatus)
        return kparams

    def getProductId(self):
        return self.productId

    def setProductId(self, newProductId):
        self.productId = newProductId

    def getProductType(self):
        return self.productType

    def setProductType(self, newProductType):
        self.productType = newProductType

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getPurchaseStatus(self):
        return self.purchaseStatus

    def setPurchaseStatus(self, newPurchaseStatus):
        self.purchaseStatus = newPurchaseStatus


# @package Kaltura
# @subpackage Client
class KalturaProductPriceListResponse(KalturaListResponse):
    """Prices list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of prices
        # @var array of KalturaProductPrice
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaProductPrice'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaProductPriceListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaProductPriceListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaCollectionPrice(KalturaProductPrice):
    """Collection price details"""

    def __init__(self,
            productId=NotImplemented,
            productType=NotImplemented,
            price=NotImplemented,
            purchaseStatus=NotImplemented):
        KalturaProductPrice.__init__(self,
            productId,
            productType,
            price,
            purchaseStatus)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaProductPrice.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCollectionPrice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaProductPrice.toParams(self)
        kparams.put("objectType", "KalturaCollectionPrice")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPpvPrice(KalturaProductPrice):
    """PPV price details"""

    def __init__(self,
            productId=NotImplemented,
            productType=NotImplemented,
            price=NotImplemented,
            purchaseStatus=NotImplemented,
            fileId=NotImplemented,
            ppvModuleId=NotImplemented,
            isSubscriptionOnly=NotImplemented,
            fullPrice=NotImplemented,
            subscriptionId=NotImplemented,
            collectionId=NotImplemented,
            prePaidId=NotImplemented,
            ppvDescriptions=NotImplemented,
            purchaseUserId=NotImplemented,
            purchasedMediaFileId=NotImplemented,
            relatedMediaFileIds=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            discountEndDate=NotImplemented,
            firstDeviceName=NotImplemented,
            isInCancelationPeriod=NotImplemented,
            ppvProductCode=NotImplemented):
        KalturaProductPrice.__init__(self,
            productId,
            productType,
            price,
            purchaseStatus)

        # Media file identifier
        # @var int
        self.fileId = fileId

        # The associated PPV module identifier
        # @var string
        self.ppvModuleId = ppvModuleId

        # Denotes whether this object is available only as part of a subscription or can be sold separately
        # @var bool
        self.isSubscriptionOnly = isSubscriptionOnly

        # The full price of the item (with no discounts)
        # @var KalturaPrice
        self.fullPrice = fullPrice

        # The identifier of the relevant subscription
        # @var string
        self.subscriptionId = subscriptionId

        # The identifier of the relevant collection
        # @var string
        self.collectionId = collectionId

        # The identifier of the relevant pre paid
        # @var string
        self.prePaidId = prePaidId

        # A list of the descriptions of the PPV module on different languages (language code and translation)
        # @var array of KalturaTranslationToken
        self.ppvDescriptions = ppvDescriptions

        # If the item already purchased - the identifier of the user (in the household) who purchased this item
        # @var string
        self.purchaseUserId = purchaseUserId

        # If the item already purchased - the identifier of the purchased file
        # @var int
        self.purchasedMediaFileId = purchasedMediaFileId

        # Related media files identifiers (different types)
        # @var array of KalturaIntegerValue
        self.relatedMediaFileIds = relatedMediaFileIds

        # If the item already purchased - since when the user can start watching the item
        # @var int
        self.startDate = startDate

        # If the item already purchased - until when the user can watch the item
        # @var int
        self.endDate = endDate

        # Discount end date
        # @var int
        self.discountEndDate = discountEndDate

        # If the item already purchased and played - the name of the device on which it was first played
        # @var string
        self.firstDeviceName = firstDeviceName

        # If waiver period is enabled - donates whether the user is still in the cancelation window
        # @var bool
        self.isInCancelationPeriod = isInCancelationPeriod

        # The PPV product code
        # @var string
        self.ppvProductCode = ppvProductCode


    PROPERTY_LOADERS = {
        'fileId': getXmlNodeInt, 
        'ppvModuleId': getXmlNodeText, 
        'isSubscriptionOnly': getXmlNodeBool, 
        'fullPrice': (KalturaObjectFactory.create, 'KalturaPrice'), 
        'subscriptionId': getXmlNodeText, 
        'collectionId': getXmlNodeText, 
        'prePaidId': getXmlNodeText, 
        'ppvDescriptions': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'purchaseUserId': getXmlNodeText, 
        'purchasedMediaFileId': getXmlNodeInt, 
        'relatedMediaFileIds': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'discountEndDate': getXmlNodeInt, 
        'firstDeviceName': getXmlNodeText, 
        'isInCancelationPeriod': getXmlNodeBool, 
        'ppvProductCode': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaProductPrice.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPpvPrice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaProductPrice.toParams(self)
        kparams.put("objectType", "KalturaPpvPrice")
        kparams.addIntIfDefined("fileId", self.fileId)
        kparams.addStringIfDefined("ppvModuleId", self.ppvModuleId)
        kparams.addBoolIfDefined("isSubscriptionOnly", self.isSubscriptionOnly)
        kparams.addObjectIfDefined("fullPrice", self.fullPrice)
        kparams.addStringIfDefined("subscriptionId", self.subscriptionId)
        kparams.addStringIfDefined("collectionId", self.collectionId)
        kparams.addStringIfDefined("prePaidId", self.prePaidId)
        kparams.addArrayIfDefined("ppvDescriptions", self.ppvDescriptions)
        kparams.addStringIfDefined("purchaseUserId", self.purchaseUserId)
        kparams.addIntIfDefined("purchasedMediaFileId", self.purchasedMediaFileId)
        kparams.addArrayIfDefined("relatedMediaFileIds", self.relatedMediaFileIds)
        kparams.addIntIfDefined("startDate", self.startDate)
        kparams.addIntIfDefined("endDate", self.endDate)
        kparams.addIntIfDefined("discountEndDate", self.discountEndDate)
        kparams.addStringIfDefined("firstDeviceName", self.firstDeviceName)
        kparams.addBoolIfDefined("isInCancelationPeriod", self.isInCancelationPeriod)
        kparams.addStringIfDefined("ppvProductCode", self.ppvProductCode)
        return kparams

    def getFileId(self):
        return self.fileId

    def setFileId(self, newFileId):
        self.fileId = newFileId

    def getPpvModuleId(self):
        return self.ppvModuleId

    def setPpvModuleId(self, newPpvModuleId):
        self.ppvModuleId = newPpvModuleId

    def getIsSubscriptionOnly(self):
        return self.isSubscriptionOnly

    def setIsSubscriptionOnly(self, newIsSubscriptionOnly):
        self.isSubscriptionOnly = newIsSubscriptionOnly

    def getFullPrice(self):
        return self.fullPrice

    def setFullPrice(self, newFullPrice):
        self.fullPrice = newFullPrice

    def getSubscriptionId(self):
        return self.subscriptionId

    def setSubscriptionId(self, newSubscriptionId):
        self.subscriptionId = newSubscriptionId

    def getCollectionId(self):
        return self.collectionId

    def setCollectionId(self, newCollectionId):
        self.collectionId = newCollectionId

    def getPrePaidId(self):
        return self.prePaidId

    def setPrePaidId(self, newPrePaidId):
        self.prePaidId = newPrePaidId

    def getPpvDescriptions(self):
        return self.ppvDescriptions

    def setPpvDescriptions(self, newPpvDescriptions):
        self.ppvDescriptions = newPpvDescriptions

    def getPurchaseUserId(self):
        return self.purchaseUserId

    def setPurchaseUserId(self, newPurchaseUserId):
        self.purchaseUserId = newPurchaseUserId

    def getPurchasedMediaFileId(self):
        return self.purchasedMediaFileId

    def setPurchasedMediaFileId(self, newPurchasedMediaFileId):
        self.purchasedMediaFileId = newPurchasedMediaFileId

    def getRelatedMediaFileIds(self):
        return self.relatedMediaFileIds

    def setRelatedMediaFileIds(self, newRelatedMediaFileIds):
        self.relatedMediaFileIds = newRelatedMediaFileIds

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate

    def getDiscountEndDate(self):
        return self.discountEndDate

    def setDiscountEndDate(self, newDiscountEndDate):
        self.discountEndDate = newDiscountEndDate

    def getFirstDeviceName(self):
        return self.firstDeviceName

    def setFirstDeviceName(self, newFirstDeviceName):
        self.firstDeviceName = newFirstDeviceName

    def getIsInCancelationPeriod(self):
        return self.isInCancelationPeriod

    def setIsInCancelationPeriod(self, newIsInCancelationPeriod):
        self.isInCancelationPeriod = newIsInCancelationPeriod

    def getPpvProductCode(self):
        return self.ppvProductCode

    def setPpvProductCode(self, newPpvProductCode):
        self.ppvProductCode = newPpvProductCode


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionPrice(KalturaProductPrice):
    """Subscription price details"""

    def __init__(self,
            productId=NotImplemented,
            productType=NotImplemented,
            price=NotImplemented,
            purchaseStatus=NotImplemented,
            endDate=NotImplemented):
        KalturaProductPrice.__init__(self,
            productId,
            productType,
            price,
            purchaseStatus)

        # If the item related to unified billing cycle purchased - until when the this price is relevant
        # @var int
        self.endDate = endDate


    PROPERTY_LOADERS = {
        'endDate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaProductPrice.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionPrice.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaProductPrice.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionPrice")
        kparams.addIntIfDefined("endDate", self.endDate)
        return kparams

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate


# @package Kaltura
# @subpackage Client
class KalturaPriceDetails(KalturaObjectBase):
    """Price details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            price=NotImplemented,
            multiCurrencyPrice=NotImplemented,
            descriptions=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The price code identifier
        # @var int
        # @readonly
        self.id = id

        # The price code name
        # @var string
        self.name = name

        # The price
        # @var KalturaPrice
        # @readonly
        self.price = price

        # Multi currency prices for all countries and currencies
        # @var array of KalturaPrice
        self.multiCurrencyPrice = multiCurrencyPrice

        # A list of the descriptions for this price on different languages (language code and translation)
        # @var array of KalturaTranslationToken
        self.descriptions = descriptions


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'price': (KalturaObjectFactory.create, 'KalturaPrice'), 
        'multiCurrencyPrice': (KalturaObjectFactory.createArray, 'KalturaPrice'), 
        'descriptions': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPriceDetails.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPriceDetails")
        kparams.addStringIfDefined("name", self.name)
        kparams.addArrayIfDefined("multiCurrencyPrice", self.multiCurrencyPrice)
        kparams.addArrayIfDefined("descriptions", self.descriptions)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getPrice(self):
        return self.price

    def getMultiCurrencyPrice(self):
        return self.multiCurrencyPrice

    def setMultiCurrencyPrice(self, newMultiCurrencyPrice):
        self.multiCurrencyPrice = newMultiCurrencyPrice

    def getDescriptions(self):
        return self.descriptions

    def setDescriptions(self, newDescriptions):
        self.descriptions = newDescriptions


# @package Kaltura
# @subpackage Client
class KalturaPriceDetailsListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of price details
        # @var array of KalturaPriceDetails
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaPriceDetails'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPriceDetailsListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaPriceDetailsListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaPricePlanListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of price plans
        # @var array of KalturaPricePlan
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaPricePlan'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPricePlanListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaPricePlanListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaPreviewModule(KalturaObjectBase):
    """Preview module"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            lifeCycle=NotImplemented,
            nonRenewablePeriod=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Preview module identifier
        # @var int
        # @readonly
        self.id = id

        # Preview module name
        # @var string
        self.name = name

        # Preview module life cycle - for how long the preview module is active
        # @var int
        self.lifeCycle = lifeCycle

        # The time you can&#39;t buy the item to which the preview module is assigned to again
        # @var int
        self.nonRenewablePeriod = nonRenewablePeriod


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'lifeCycle': getXmlNodeInt, 
        'nonRenewablePeriod': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPreviewModule.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPreviewModule")
        kparams.addStringIfDefined("name", self.name)
        kparams.addIntIfDefined("lifeCycle", self.lifeCycle)
        kparams.addIntIfDefined("nonRenewablePeriod", self.nonRenewablePeriod)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getLifeCycle(self):
        return self.lifeCycle

    def setLifeCycle(self, newLifeCycle):
        self.lifeCycle = newLifeCycle

    def getNonRenewablePeriod(self):
        return self.nonRenewablePeriod

    def setNonRenewablePeriod(self, newNonRenewablePeriod):
        self.nonRenewablePeriod = newNonRenewablePeriod


# @package Kaltura
# @subpackage Client
class KalturaPremiumService(KalturaObjectBase):
    """Premium service"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Service identifier
        # @var int
        # @readonly
        self.id = id

        # Service name / description
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPremiumService.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPremiumService")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaSubscription(KalturaObjectBase):
    """Subscription details"""

    def __init__(self,
            id=NotImplemented,
            channels=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            fileTypes=NotImplemented,
            isRenewable=NotImplemented,
            renewalsNumber=NotImplemented,
            isInfiniteRenewal=NotImplemented,
            price=NotImplemented,
            discountModule=NotImplemented,
            name=NotImplemented,
            multilingualName=NotImplemented,
            description=NotImplemented,
            multilingualDescription=NotImplemented,
            mediaId=NotImplemented,
            prorityInOrder=NotImplemented,
            pricePlanIds=NotImplemented,
            previewModule=NotImplemented,
            householdLimitationsId=NotImplemented,
            gracePeriodMinutes=NotImplemented,
            premiumServices=NotImplemented,
            maxViewsNumber=NotImplemented,
            viewLifeCycle=NotImplemented,
            waiverPeriod=NotImplemented,
            isWaiverEnabled=NotImplemented,
            userTypes=NotImplemented,
            couponsGroups=NotImplemented,
            productCodes=NotImplemented,
            dependencyType=NotImplemented,
            externalId=NotImplemented,
            isCancellationBlocked=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Subscription identifier
        # @var string
        self.id = id

        # A list of channels associated with this subscription
        # @var array of KalturaBaseChannel
        self.channels = channels

        # The first date the subscription is available for purchasing
        # @var int
        self.startDate = startDate

        # The last date the subscription is available for purchasing
        # @var int
        self.endDate = endDate

        # A list of file types identifiers that are supported in this subscription
        # @var array of KalturaIntegerValue
        self.fileTypes = fileTypes

        # Denotes whether or not this subscription can be renewed
        # @var bool
        self.isRenewable = isRenewable

        # Defines the number of times this subscription will be renewed
        # @var int
        self.renewalsNumber = renewalsNumber

        # Indicates whether the subscription will renew forever
        # @var bool
        self.isInfiniteRenewal = isInfiniteRenewal

        # The price of the subscription
        # @var KalturaPriceDetails
        self.price = price

        # The internal discount module for the subscription
        # @var KalturaDiscountModule
        self.discountModule = discountModule

        # Name of the subscription
        # @var string
        # @readonly
        self.name = name

        # Name of the subscription
        # @var array of KalturaTranslationToken
        self.multilingualName = multilingualName

        # description of the subscription
        # @var string
        # @readonly
        self.description = description

        # description of the subscription
        # @var array of KalturaTranslationToken
        self.multilingualDescription = multilingualDescription

        # Identifier of the media associated with the subscription
        # @var int
        self.mediaId = mediaId

        # Subscription order (when returned in methods that retrieve subscriptions)
        # @var int
        self.prorityInOrder = prorityInOrder

        # Comma separated subscription price plan IDs
        # @var string
        self.pricePlanIds = pricePlanIds

        # Subscription preview module
        # @var KalturaPreviewModule
        self.previewModule = previewModule

        # The household limitation module identifier associated with this subscription
        # @var int
        self.householdLimitationsId = householdLimitationsId

        # The subscription grace period in minutes
        # @var int
        self.gracePeriodMinutes = gracePeriodMinutes

        # List of premium services included in the subscription
        # @var array of KalturaPremiumService
        self.premiumServices = premiumServices

        # The maximum number of times an item in this usage module can be viewed
        # @var int
        self.maxViewsNumber = maxViewsNumber

        # The amount time an item is available for viewing since a user started watching the item
        # @var int
        self.viewLifeCycle = viewLifeCycle

        # Time period during which the end user can waive his rights to cancel a purchase. When the time period is passed, the purchase can no longer be cancelled
        # @var int
        self.waiverPeriod = waiverPeriod

        # Indicates whether or not the end user has the right to waive his rights to cancel a purchase
        # @var bool
        self.isWaiverEnabled = isWaiverEnabled

        # List of permitted user types for the subscription
        # @var array of KalturaOTTUserType
        self.userTypes = userTypes

        # List of Coupons group
        # @var array of KalturaCouponsGroup
        self.couponsGroups = couponsGroups

        # List of Subscription product codes
        # @var array of KalturaProductCode
        self.productCodes = productCodes

        # Dependency Type
        # @var KalturaSubscriptionDependencyType
        self.dependencyType = dependencyType

        # External ID
        # @var string
        self.externalId = externalId

        # Is cancellation blocked for the subscription
        # @var bool
        self.isCancellationBlocked = isCancellationBlocked


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'channels': (KalturaObjectFactory.createArray, 'KalturaBaseChannel'), 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'fileTypes': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
        'isRenewable': getXmlNodeBool, 
        'renewalsNumber': getXmlNodeInt, 
        'isInfiniteRenewal': getXmlNodeBool, 
        'price': (KalturaObjectFactory.create, 'KalturaPriceDetails'), 
        'discountModule': (KalturaObjectFactory.create, 'KalturaDiscountModule'), 
        'name': getXmlNodeText, 
        'multilingualName': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'description': getXmlNodeText, 
        'multilingualDescription': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'mediaId': getXmlNodeInt, 
        'prorityInOrder': getXmlNodeInt, 
        'pricePlanIds': getXmlNodeText, 
        'previewModule': (KalturaObjectFactory.create, 'KalturaPreviewModule'), 
        'householdLimitationsId': getXmlNodeInt, 
        'gracePeriodMinutes': getXmlNodeInt, 
        'premiumServices': (KalturaObjectFactory.createArray, 'KalturaPremiumService'), 
        'maxViewsNumber': getXmlNodeInt, 
        'viewLifeCycle': getXmlNodeInt, 
        'waiverPeriod': getXmlNodeInt, 
        'isWaiverEnabled': getXmlNodeBool, 
        'userTypes': (KalturaObjectFactory.createArray, 'KalturaOTTUserType'), 
        'couponsGroups': (KalturaObjectFactory.createArray, 'KalturaCouponsGroup'), 
        'productCodes': (KalturaObjectFactory.createArray, 'KalturaProductCode'), 
        'dependencyType': (KalturaEnumsFactory.createString, "KalturaSubscriptionDependencyType"), 
        'externalId': getXmlNodeText, 
        'isCancellationBlocked': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscription.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSubscription")
        kparams.addStringIfDefined("id", self.id)
        kparams.addArrayIfDefined("channels", self.channels)
        kparams.addIntIfDefined("startDate", self.startDate)
        kparams.addIntIfDefined("endDate", self.endDate)
        kparams.addArrayIfDefined("fileTypes", self.fileTypes)
        kparams.addBoolIfDefined("isRenewable", self.isRenewable)
        kparams.addIntIfDefined("renewalsNumber", self.renewalsNumber)
        kparams.addBoolIfDefined("isInfiniteRenewal", self.isInfiniteRenewal)
        kparams.addObjectIfDefined("price", self.price)
        kparams.addObjectIfDefined("discountModule", self.discountModule)
        kparams.addArrayIfDefined("multilingualName", self.multilingualName)
        kparams.addArrayIfDefined("multilingualDescription", self.multilingualDescription)
        kparams.addIntIfDefined("mediaId", self.mediaId)
        kparams.addIntIfDefined("prorityInOrder", self.prorityInOrder)
        kparams.addStringIfDefined("pricePlanIds", self.pricePlanIds)
        kparams.addObjectIfDefined("previewModule", self.previewModule)
        kparams.addIntIfDefined("householdLimitationsId", self.householdLimitationsId)
        kparams.addIntIfDefined("gracePeriodMinutes", self.gracePeriodMinutes)
        kparams.addArrayIfDefined("premiumServices", self.premiumServices)
        kparams.addIntIfDefined("maxViewsNumber", self.maxViewsNumber)
        kparams.addIntIfDefined("viewLifeCycle", self.viewLifeCycle)
        kparams.addIntIfDefined("waiverPeriod", self.waiverPeriod)
        kparams.addBoolIfDefined("isWaiverEnabled", self.isWaiverEnabled)
        kparams.addArrayIfDefined("userTypes", self.userTypes)
        kparams.addArrayIfDefined("couponsGroups", self.couponsGroups)
        kparams.addArrayIfDefined("productCodes", self.productCodes)
        kparams.addStringEnumIfDefined("dependencyType", self.dependencyType)
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addBoolIfDefined("isCancellationBlocked", self.isCancellationBlocked)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getChannels(self):
        return self.channels

    def setChannels(self, newChannels):
        self.channels = newChannels

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate

    def getFileTypes(self):
        return self.fileTypes

    def setFileTypes(self, newFileTypes):
        self.fileTypes = newFileTypes

    def getIsRenewable(self):
        return self.isRenewable

    def setIsRenewable(self, newIsRenewable):
        self.isRenewable = newIsRenewable

    def getRenewalsNumber(self):
        return self.renewalsNumber

    def setRenewalsNumber(self, newRenewalsNumber):
        self.renewalsNumber = newRenewalsNumber

    def getIsInfiniteRenewal(self):
        return self.isInfiniteRenewal

    def setIsInfiniteRenewal(self, newIsInfiniteRenewal):
        self.isInfiniteRenewal = newIsInfiniteRenewal

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getDiscountModule(self):
        return self.discountModule

    def setDiscountModule(self, newDiscountModule):
        self.discountModule = newDiscountModule

    def getName(self):
        return self.name

    def getMultilingualName(self):
        return self.multilingualName

    def setMultilingualName(self, newMultilingualName):
        self.multilingualName = newMultilingualName

    def getDescription(self):
        return self.description

    def getMultilingualDescription(self):
        return self.multilingualDescription

    def setMultilingualDescription(self, newMultilingualDescription):
        self.multilingualDescription = newMultilingualDescription

    def getMediaId(self):
        return self.mediaId

    def setMediaId(self, newMediaId):
        self.mediaId = newMediaId

    def getProrityInOrder(self):
        return self.prorityInOrder

    def setProrityInOrder(self, newProrityInOrder):
        self.prorityInOrder = newProrityInOrder

    def getPricePlanIds(self):
        return self.pricePlanIds

    def setPricePlanIds(self, newPricePlanIds):
        self.pricePlanIds = newPricePlanIds

    def getPreviewModule(self):
        return self.previewModule

    def setPreviewModule(self, newPreviewModule):
        self.previewModule = newPreviewModule

    def getHouseholdLimitationsId(self):
        return self.householdLimitationsId

    def setHouseholdLimitationsId(self, newHouseholdLimitationsId):
        self.householdLimitationsId = newHouseholdLimitationsId

    def getGracePeriodMinutes(self):
        return self.gracePeriodMinutes

    def setGracePeriodMinutes(self, newGracePeriodMinutes):
        self.gracePeriodMinutes = newGracePeriodMinutes

    def getPremiumServices(self):
        return self.premiumServices

    def setPremiumServices(self, newPremiumServices):
        self.premiumServices = newPremiumServices

    def getMaxViewsNumber(self):
        return self.maxViewsNumber

    def setMaxViewsNumber(self, newMaxViewsNumber):
        self.maxViewsNumber = newMaxViewsNumber

    def getViewLifeCycle(self):
        return self.viewLifeCycle

    def setViewLifeCycle(self, newViewLifeCycle):
        self.viewLifeCycle = newViewLifeCycle

    def getWaiverPeriod(self):
        return self.waiverPeriod

    def setWaiverPeriod(self, newWaiverPeriod):
        self.waiverPeriod = newWaiverPeriod

    def getIsWaiverEnabled(self):
        return self.isWaiverEnabled

    def setIsWaiverEnabled(self, newIsWaiverEnabled):
        self.isWaiverEnabled = newIsWaiverEnabled

    def getUserTypes(self):
        return self.userTypes

    def setUserTypes(self, newUserTypes):
        self.userTypes = newUserTypes

    def getCouponsGroups(self):
        return self.couponsGroups

    def setCouponsGroups(self, newCouponsGroups):
        self.couponsGroups = newCouponsGroups

    def getProductCodes(self):
        return self.productCodes

    def setProductCodes(self, newProductCodes):
        self.productCodes = newProductCodes

    def getDependencyType(self):
        return self.dependencyType

    def setDependencyType(self, newDependencyType):
        self.dependencyType = newDependencyType

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getIsCancellationBlocked(self):
        return self.isCancellationBlocked

    def setIsCancellationBlocked(self, newIsCancellationBlocked):
        self.isCancellationBlocked = newIsCancellationBlocked


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionListResponse(KalturaListResponse):
    """Subscriptions list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of subscriptions
        # @var array of KalturaSubscription
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSubscription'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaNpvrPremiumService(KalturaPremiumService):
    """Npvr Premium Service"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            quotaInMinutes=NotImplemented):
        KalturaPremiumService.__init__(self,
            id,
            name)

        # Quota in minutes
        # @var int
        # @readonly
        self.quotaInMinutes = quotaInMinutes


    PROPERTY_LOADERS = {
        'quotaInMinutes': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaPremiumService.fromXml(self, node)
        self.fromXmlImpl(node, KalturaNpvrPremiumService.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPremiumService.toParams(self)
        kparams.put("objectType", "KalturaNpvrPremiumService")
        return kparams

    def getQuotaInMinutes(self):
        return self.quotaInMinutes


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPremiumService(KalturaPremiumService):
    """Houshold premium service"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaPremiumService.__init__(self,
            id,
            name)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaPremiumService.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdPremiumService.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPremiumService.toParams(self)
        kparams.put("objectType", "KalturaHouseholdPremiumService")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaProductsPriceListResponse(KalturaListResponse):
    """Prices list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of prices
        # @var array of KalturaProductPrice
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaProductPrice'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaProductsPriceListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaProductsPriceListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaEngagement(KalturaObjectBase):
    """Engagement"""

    def __init__(self,
            id=NotImplemented,
            totalNumberOfRecipients=NotImplemented,
            type=NotImplemented,
            adapterId=NotImplemented,
            adapterDynamicData=NotImplemented,
            intervalSeconds=NotImplemented,
            userList=NotImplemented,
            sendTimeInSeconds=NotImplemented,
            couponGroupId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Engagement id
        # @var int
        # @readonly
        self.id = id

        # Total number of recipients
        # @var int
        # @readonly
        self.totalNumberOfRecipients = totalNumberOfRecipients

        # Engagement type
        # @var KalturaEngagementType
        self.type = type

        # Engagement adapter id
        # @var int
        self.adapterId = adapterId

        # Engagement adapter dynamic data
        # @var string
        self.adapterDynamicData = adapterDynamicData

        # Interval (seconds)
        # @var int
        self.intervalSeconds = intervalSeconds

        # Manual User list
        # @var string
        self.userList = userList

        # Send time (seconds)
        # @var int
        self.sendTimeInSeconds = sendTimeInSeconds

        # Coupon GroupId
        # @var int
        self.couponGroupId = couponGroupId


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'totalNumberOfRecipients': getXmlNodeInt, 
        'type': (KalturaEnumsFactory.createString, "KalturaEngagementType"), 
        'adapterId': getXmlNodeInt, 
        'adapterDynamicData': getXmlNodeText, 
        'intervalSeconds': getXmlNodeInt, 
        'userList': getXmlNodeText, 
        'sendTimeInSeconds': getXmlNodeInt, 
        'couponGroupId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEngagement.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaEngagement")
        kparams.addStringEnumIfDefined("type", self.type)
        kparams.addIntIfDefined("adapterId", self.adapterId)
        kparams.addStringIfDefined("adapterDynamicData", self.adapterDynamicData)
        kparams.addIntIfDefined("intervalSeconds", self.intervalSeconds)
        kparams.addStringIfDefined("userList", self.userList)
        kparams.addIntIfDefined("sendTimeInSeconds", self.sendTimeInSeconds)
        kparams.addIntIfDefined("couponGroupId", self.couponGroupId)
        return kparams

    def getId(self):
        return self.id

    def getTotalNumberOfRecipients(self):
        return self.totalNumberOfRecipients

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getAdapterId(self):
        return self.adapterId

    def setAdapterId(self, newAdapterId):
        self.adapterId = newAdapterId

    def getAdapterDynamicData(self):
        return self.adapterDynamicData

    def setAdapterDynamicData(self, newAdapterDynamicData):
        self.adapterDynamicData = newAdapterDynamicData

    def getIntervalSeconds(self):
        return self.intervalSeconds

    def setIntervalSeconds(self, newIntervalSeconds):
        self.intervalSeconds = newIntervalSeconds

    def getUserList(self):
        return self.userList

    def setUserList(self, newUserList):
        self.userList = newUserList

    def getSendTimeInSeconds(self):
        return self.sendTimeInSeconds

    def setSendTimeInSeconds(self, newSendTimeInSeconds):
        self.sendTimeInSeconds = newSendTimeInSeconds

    def getCouponGroupId(self):
        return self.couponGroupId

    def setCouponGroupId(self, newCouponGroupId):
        self.couponGroupId = newCouponGroupId


# @package Kaltura
# @subpackage Client
class KalturaEngagementListResponse(KalturaListResponse):
    """Engagement adapter list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of Engagement
        # @var array of KalturaEngagement
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaEngagement'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEngagementListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaEngagementListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaEngagementAdapterBase(KalturaObjectBase):
    """Engagement adapter basic"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Engagement adapter id
        # @var int
        # @readonly
        self.id = id

        # Engagement adapter name
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEngagementAdapterBase.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaEngagementAdapterBase")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaEngagementAdapter(KalturaEngagementAdapterBase):
    """Engagement Adapter"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isActive=NotImplemented,
            adapterUrl=NotImplemented,
            providerUrl=NotImplemented,
            engagementAdapterSettings=NotImplemented,
            sharedSecret=NotImplemented):
        KalturaEngagementAdapterBase.__init__(self,
            id,
            name)

        # Engagement adapter active status
        # @var bool
        self.isActive = isActive

        # Engagement adapter adapter URL
        # @var string
        self.adapterUrl = adapterUrl

        # Engagement provider adapter URL
        # @var string
        self.providerUrl = providerUrl

        # Engagement adapter extra parameters
        # @var map
        self.engagementAdapterSettings = engagementAdapterSettings

        # Shared Secret
        # @var string
        # @readonly
        self.sharedSecret = sharedSecret


    PROPERTY_LOADERS = {
        'isActive': getXmlNodeBool, 
        'adapterUrl': getXmlNodeText, 
        'providerUrl': getXmlNodeText, 
        'engagementAdapterSettings': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'sharedSecret': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaEngagementAdapterBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEngagementAdapter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaEngagementAdapterBase.toParams(self)
        kparams.put("objectType", "KalturaEngagementAdapter")
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("adapterUrl", self.adapterUrl)
        kparams.addStringIfDefined("providerUrl", self.providerUrl)
        kparams.addMapIfDefined("engagementAdapterSettings", self.engagementAdapterSettings)
        return kparams

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getAdapterUrl(self):
        return self.adapterUrl

    def setAdapterUrl(self, newAdapterUrl):
        self.adapterUrl = newAdapterUrl

    def getProviderUrl(self):
        return self.providerUrl

    def setProviderUrl(self, newProviderUrl):
        self.providerUrl = newProviderUrl

    def getEngagementAdapterSettings(self):
        return self.engagementAdapterSettings

    def setEngagementAdapterSettings(self, newEngagementAdapterSettings):
        self.engagementAdapterSettings = newEngagementAdapterSettings

    def getSharedSecret(self):
        return self.sharedSecret


# @package Kaltura
# @subpackage Client
class KalturaEngagementAdapterListResponse(KalturaListResponse):
    """Engagement adapter list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of Engagement adapter
        # @var array of KalturaEngagementAdapter
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaEngagementAdapter'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEngagementAdapterListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaEngagementAdapterListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaReminder(KalturaObjectBase):
    def __init__(self,
            name=NotImplemented,
            id=NotImplemented,
            type=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Reminder name
        # @var string
        # @readonly
        self.name = name

        # Reminder id
        # @var int
        # @readonly
        self.id = id

        # Reminder type
        # @var KalturaReminderType
        self.type = type


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'id': getXmlNodeInt, 
        'type': (KalturaEnumsFactory.createString, "KalturaReminderType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaReminder.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaReminder")
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType


# @package Kaltura
# @subpackage Client
class KalturaReminderListResponse(KalturaListResponse):
    """List of reminders from DB."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Reminders
        # @var array of KalturaReminder
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaReminder'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaReminderListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaReminderListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaSeriesReminder(KalturaReminder):
    def __init__(self,
            name=NotImplemented,
            id=NotImplemented,
            type=NotImplemented,
            seriesId=NotImplemented,
            seasonNumber=NotImplemented,
            epgChannelId=NotImplemented):
        KalturaReminder.__init__(self,
            name,
            id,
            type)

        # Series identifier
        # @var string
        self.seriesId = seriesId

        # Season number
        # @var int
        self.seasonNumber = seasonNumber

        # EPG channel identifier
        # @var int
        self.epgChannelId = epgChannelId


    PROPERTY_LOADERS = {
        'seriesId': getXmlNodeText, 
        'seasonNumber': getXmlNodeInt, 
        'epgChannelId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaReminder.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSeriesReminder.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReminder.toParams(self)
        kparams.put("objectType", "KalturaSeriesReminder")
        kparams.addStringIfDefined("seriesId", self.seriesId)
        kparams.addIntIfDefined("seasonNumber", self.seasonNumber)
        kparams.addIntIfDefined("epgChannelId", self.epgChannelId)
        return kparams

    def getSeriesId(self):
        return self.seriesId

    def setSeriesId(self, newSeriesId):
        self.seriesId = newSeriesId

    def getSeasonNumber(self):
        return self.seasonNumber

    def setSeasonNumber(self, newSeasonNumber):
        self.seasonNumber = newSeasonNumber

    def getEpgChannelId(self):
        return self.epgChannelId

    def setEpgChannelId(self, newEpgChannelId):
        self.epgChannelId = newEpgChannelId


# @package Kaltura
# @subpackage Client
class KalturaAssetReminder(KalturaReminder):
    def __init__(self,
            name=NotImplemented,
            id=NotImplemented,
            type=NotImplemented,
            assetId=NotImplemented):
        KalturaReminder.__init__(self,
            name,
            id,
            type)

        # Asset id
        # @var int
        self.assetId = assetId


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaReminder.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetReminder.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReminder.toParams(self)
        kparams.put("objectType", "KalturaAssetReminder")
        kparams.addIntIfDefined("assetId", self.assetId)
        return kparams

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId


# @package Kaltura
# @subpackage Client
class KalturaInboxMessage(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            message=NotImplemented,
            status=NotImplemented,
            type=NotImplemented,
            createdAt=NotImplemented,
            url=NotImplemented):
        KalturaObjectBase.__init__(self)

        # message id
        # @var string
        # @readonly
        self.id = id

        # message
        # @var string
        self.message = message

        # Status
        # @var KalturaInboxMessageStatus
        # @readonly
        self.status = status

        # Type
        # @var KalturaInboxMessageType
        self.type = type

        # Created at
        # @var int
        # @readonly
        self.createdAt = createdAt

        # url
        # @var string
        self.url = url


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'message': getXmlNodeText, 
        'status': (KalturaEnumsFactory.createString, "KalturaInboxMessageStatus"), 
        'type': (KalturaEnumsFactory.createString, "KalturaInboxMessageType"), 
        'createdAt': getXmlNodeInt, 
        'url': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaInboxMessage.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaInboxMessage")
        kparams.addStringIfDefined("message", self.message)
        kparams.addStringEnumIfDefined("type", self.type)
        kparams.addStringIfDefined("url", self.url)
        return kparams

    def getId(self):
        return self.id

    def getMessage(self):
        return self.message

    def setMessage(self, newMessage):
        self.message = newMessage

    def getStatus(self):
        return self.status

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getCreatedAt(self):
        return self.createdAt

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl


# @package Kaltura
# @subpackage Client
class KalturaInboxMessageListResponse(KalturaListResponse):
    """List of inbox message."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Follow data list
        # @var array of KalturaInboxMessage
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaInboxMessage'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaInboxMessageListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaInboxMessageListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaFollowDataBase(KalturaObjectBase):
    def __init__(self,
            announcementId=NotImplemented,
            status=NotImplemented,
            title=NotImplemented,
            timestamp=NotImplemented,
            followPhrase=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Announcement Id
        # @var int
        # @readonly
        self.announcementId = announcementId

        # Status
        # @var int
        # @readonly
        self.status = status

        # Title
        # @var string
        # @readonly
        self.title = title

        # Timestamp
        # @var int
        # @readonly
        self.timestamp = timestamp

        # Follow Phrase
        # @var string
        # @readonly
        self.followPhrase = followPhrase


    PROPERTY_LOADERS = {
        'announcementId': getXmlNodeInt, 
        'status': getXmlNodeInt, 
        'title': getXmlNodeText, 
        'timestamp': getXmlNodeInt, 
        'followPhrase': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFollowDataBase.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaFollowDataBase")
        return kparams

    def getAnnouncementId(self):
        return self.announcementId

    def getStatus(self):
        return self.status

    def getTitle(self):
        return self.title

    def getTimestamp(self):
        return self.timestamp

    def getFollowPhrase(self):
        return self.followPhrase


# @package Kaltura
# @subpackage Client
class KalturaFollowTvSeries(KalturaFollowDataBase):
    def __init__(self,
            announcementId=NotImplemented,
            status=NotImplemented,
            title=NotImplemented,
            timestamp=NotImplemented,
            followPhrase=NotImplemented,
            assetId=NotImplemented):
        KalturaFollowDataBase.__init__(self,
            announcementId,
            status,
            title,
            timestamp,
            followPhrase)

        # Asset Id
        # @var int
        self.assetId = assetId


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFollowDataBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFollowTvSeries.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFollowDataBase.toParams(self)
        kparams.put("objectType", "KalturaFollowTvSeries")
        kparams.addIntIfDefined("assetId", self.assetId)
        return kparams

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId


# @package Kaltura
# @subpackage Client
class KalturaFollowTvSeriesListResponse(KalturaListResponse):
    """List of message follow data."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Follow data list
        # @var array of KalturaFollowTvSeries
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaFollowTvSeries'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFollowTvSeriesListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaFollowTvSeriesListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaAnnouncement(KalturaObjectBase):
    def __init__(self,
            name=NotImplemented,
            message=NotImplemented,
            enabled=NotImplemented,
            startTime=NotImplemented,
            timezone=NotImplemented,
            status=NotImplemented,
            recipients=NotImplemented,
            id=NotImplemented,
            imageUrl=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Announcement name
        # @var string
        self.name = name

        # Announcement message
        # @var string
        self.message = message

        # Announcement enabled
        # @var bool
        self.enabled = enabled

        # Announcement start time
        # @var int
        self.startTime = startTime

        # Announcement time zone
        # @var string
        self.timezone = timezone

        # Announcement status: NotSent=0/Sending=1/Sent=2/Aborted=3
        # @var KalturaAnnouncementStatus
        # @readonly
        self.status = status

        # Announcement recipients: All=0/LoggedIn=1/Guests=2/Other=3
        # @var KalturaAnnouncementRecipientsType
        self.recipients = recipients

        # Announcement id
        # @var int
        # @readonly
        self.id = id

        # Announcement image URL, relevant for system announcements
        # @var string
        self.imageUrl = imageUrl


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'message': getXmlNodeText, 
        'enabled': getXmlNodeBool, 
        'startTime': getXmlNodeInt, 
        'timezone': getXmlNodeText, 
        'status': (KalturaEnumsFactory.createString, "KalturaAnnouncementStatus"), 
        'recipients': (KalturaEnumsFactory.createString, "KalturaAnnouncementRecipientsType"), 
        'id': getXmlNodeInt, 
        'imageUrl': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAnnouncement.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAnnouncement")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("message", self.message)
        kparams.addBoolIfDefined("enabled", self.enabled)
        kparams.addIntIfDefined("startTime", self.startTime)
        kparams.addStringIfDefined("timezone", self.timezone)
        kparams.addStringEnumIfDefined("recipients", self.recipients)
        kparams.addStringIfDefined("imageUrl", self.imageUrl)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getMessage(self):
        return self.message

    def setMessage(self, newMessage):
        self.message = newMessage

    def getEnabled(self):
        return self.enabled

    def setEnabled(self, newEnabled):
        self.enabled = newEnabled

    def getStartTime(self):
        return self.startTime

    def setStartTime(self, newStartTime):
        self.startTime = newStartTime

    def getTimezone(self):
        return self.timezone

    def setTimezone(self, newTimezone):
        self.timezone = newTimezone

    def getStatus(self):
        return self.status

    def getRecipients(self):
        return self.recipients

    def setRecipients(self, newRecipients):
        self.recipients = newRecipients

    def getId(self):
        return self.id

    def getImageUrl(self):
        return self.imageUrl

    def setImageUrl(self, newImageUrl):
        self.imageUrl = newImageUrl


# @package Kaltura
# @subpackage Client
class KalturaAnnouncementListResponse(KalturaListResponse):
    """List of message announcements from DB."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Announcements
        # @var array of KalturaAnnouncement
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaAnnouncement'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAnnouncementListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaAnnouncementListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaFeed(KalturaObjectBase):
    def __init__(self,
            assetId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Asset identifier
        # @var int
        # @readonly
        self.assetId = assetId


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFeed.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaFeed")
        return kparams

    def getAssetId(self):
        return self.assetId


# @package Kaltura
# @subpackage Client
class KalturaPersonalFeed(KalturaFeed):
    def __init__(self,
            assetId=NotImplemented):
        KalturaFeed.__init__(self,
            assetId)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFeed.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPersonalFeed.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFeed.toParams(self)
        kparams.put("objectType", "KalturaPersonalFeed")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPersonalFeedListResponse(KalturaListResponse):
    """List of message follow data."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Follow data list
        # @var array of KalturaPersonalFeed
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaPersonalFeed'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPersonalFeedListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaPersonalFeedListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaTopic(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            subscribersAmount=NotImplemented,
            automaticIssueNotification=NotImplemented,
            lastMessageSentDateSec=NotImplemented):
        KalturaObjectBase.__init__(self)

        # message id
        # @var string
        # @readonly
        self.id = id

        # message
        # @var string
        self.name = name

        # message
        # @var string
        self.subscribersAmount = subscribersAmount

        # automaticIssueNotification
        # @var KalturaTopicAutomaticIssueNotification
        self.automaticIssueNotification = automaticIssueNotification

        # lastMessageSentDateSec
        # @var int
        self.lastMessageSentDateSec = lastMessageSentDateSec


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
        'subscribersAmount': getXmlNodeText, 
        'automaticIssueNotification': (KalturaEnumsFactory.createString, "KalturaTopicAutomaticIssueNotification"), 
        'lastMessageSentDateSec': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTopic.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaTopic")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("subscribersAmount", self.subscribersAmount)
        kparams.addStringEnumIfDefined("automaticIssueNotification", self.automaticIssueNotification)
        kparams.addIntIfDefined("lastMessageSentDateSec", self.lastMessageSentDateSec)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getSubscribersAmount(self):
        return self.subscribersAmount

    def setSubscribersAmount(self, newSubscribersAmount):
        self.subscribersAmount = newSubscribersAmount

    def getAutomaticIssueNotification(self):
        return self.automaticIssueNotification

    def setAutomaticIssueNotification(self, newAutomaticIssueNotification):
        self.automaticIssueNotification = newAutomaticIssueNotification

    def getLastMessageSentDateSec(self):
        return self.lastMessageSentDateSec

    def setLastMessageSentDateSec(self, newLastMessageSentDateSec):
        self.lastMessageSentDateSec = newLastMessageSentDateSec


# @package Kaltura
# @subpackage Client
class KalturaTopicListResponse(KalturaListResponse):
    """List of inbox message."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Follow data list
        # @var array of KalturaTopic
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaTopic'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTopicListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaTopicListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaIntegerValueListResponse(KalturaListResponse):
    """Integer list wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Interger value items
        # @var array of KalturaIntegerValue
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaIntegerValueListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaIntegerValueListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaReport(KalturaObjectBase):
    def __init__(self):
        KalturaObjectBase.__init__(self)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaReport.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaReport")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaReportListResponse(KalturaListResponse):
    """Reports info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Reports
        # @var array of KalturaReport
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaReport'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaReportListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaReportListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaPushParams(KalturaObjectBase):
    def __init__(self,
            token=NotImplemented,
            externalToken=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Device-Application push token
        # @var string
        self.token = token

        # External device token as received from external push provider in exchange for the device token
        # @var string
        self.externalToken = externalToken


    PROPERTY_LOADERS = {
        'token': getXmlNodeText, 
        'externalToken': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPushParams.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPushParams")
        kparams.addStringIfDefined("token", self.token)
        kparams.addStringIfDefined("externalToken", self.externalToken)
        return kparams

    def getToken(self):
        return self.token

    def setToken(self, newToken):
        self.token = newToken

    def getExternalToken(self):
        return self.externalToken

    def setExternalToken(self, newExternalToken):
        self.externalToken = newExternalToken


# @package Kaltura
# @subpackage Client
class KalturaDeviceReport(KalturaReport):
    def __init__(self,
            partnerId=NotImplemented,
            configurationGroupId=NotImplemented,
            udid=NotImplemented,
            pushParameters=NotImplemented,
            versionNumber=NotImplemented,
            versionPlatform=NotImplemented,
            versionAppName=NotImplemented,
            lastAccessIP=NotImplemented,
            lastAccessDate=NotImplemented,
            userAgent=NotImplemented,
            operationSystem=NotImplemented):
        KalturaReport.__init__(self)

        # Partner unique identifier
        # @var int
        self.partnerId = partnerId

        # Configuration group identifier which the version configuration the device last received belongs to
        # @var string
        self.configurationGroupId = configurationGroupId

        # Device unique identifier
        # @var string
        self.udid = udid

        # Device-Application push parameters
        # @var KalturaPushParams
        self.pushParameters = pushParameters

        # Application version number
        # @var string
        self.versionNumber = versionNumber

        # Application version type
        # @var KalturaPlatform
        self.versionPlatform = versionPlatform

        # Application version name
        # @var string
        self.versionAppName = versionAppName

        # Last access IP
        # @var string
        self.lastAccessIP = lastAccessIP

        # Last device configuration request date
        # @var int
        self.lastAccessDate = lastAccessDate

        # request header property
        # @var string
        self.userAgent = userAgent

        # Request header property
        #             Incase value cannot be found - returns &quot;Unknown 0.0&quot;
        # @var string
        self.operationSystem = operationSystem


    PROPERTY_LOADERS = {
        'partnerId': getXmlNodeInt, 
        'configurationGroupId': getXmlNodeText, 
        'udid': getXmlNodeText, 
        'pushParameters': (KalturaObjectFactory.create, 'KalturaPushParams'), 
        'versionNumber': getXmlNodeText, 
        'versionPlatform': (KalturaEnumsFactory.createString, "KalturaPlatform"), 
        'versionAppName': getXmlNodeText, 
        'lastAccessIP': getXmlNodeText, 
        'lastAccessDate': getXmlNodeInt, 
        'userAgent': getXmlNodeText, 
        'operationSystem': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaReport.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceReport.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReport.toParams(self)
        kparams.put("objectType", "KalturaDeviceReport")
        kparams.addIntIfDefined("partnerId", self.partnerId)
        kparams.addStringIfDefined("configurationGroupId", self.configurationGroupId)
        kparams.addStringIfDefined("udid", self.udid)
        kparams.addObjectIfDefined("pushParameters", self.pushParameters)
        kparams.addStringIfDefined("versionNumber", self.versionNumber)
        kparams.addStringEnumIfDefined("versionPlatform", self.versionPlatform)
        kparams.addStringIfDefined("versionAppName", self.versionAppName)
        kparams.addStringIfDefined("lastAccessIP", self.lastAccessIP)
        kparams.addIntIfDefined("lastAccessDate", self.lastAccessDate)
        kparams.addStringIfDefined("userAgent", self.userAgent)
        kparams.addStringIfDefined("operationSystem", self.operationSystem)
        return kparams

    def getPartnerId(self):
        return self.partnerId

    def setPartnerId(self, newPartnerId):
        self.partnerId = newPartnerId

    def getConfigurationGroupId(self):
        return self.configurationGroupId

    def setConfigurationGroupId(self, newConfigurationGroupId):
        self.configurationGroupId = newConfigurationGroupId

    def getUdid(self):
        return self.udid

    def setUdid(self, newUdid):
        self.udid = newUdid

    def getPushParameters(self):
        return self.pushParameters

    def setPushParameters(self, newPushParameters):
        self.pushParameters = newPushParameters

    def getVersionNumber(self):
        return self.versionNumber

    def setVersionNumber(self, newVersionNumber):
        self.versionNumber = newVersionNumber

    def getVersionPlatform(self):
        return self.versionPlatform

    def setVersionPlatform(self, newVersionPlatform):
        self.versionPlatform = newVersionPlatform

    def getVersionAppName(self):
        return self.versionAppName

    def setVersionAppName(self, newVersionAppName):
        self.versionAppName = newVersionAppName

    def getLastAccessIP(self):
        return self.lastAccessIP

    def setLastAccessIP(self, newLastAccessIP):
        self.lastAccessIP = newLastAccessIP

    def getLastAccessDate(self):
        return self.lastAccessDate

    def setLastAccessDate(self, newLastAccessDate):
        self.lastAccessDate = newLastAccessDate

    def getUserAgent(self):
        return self.userAgent

    def setUserAgent(self, newUserAgent):
        self.userAgent = newUserAgent

    def getOperationSystem(self):
        return self.operationSystem

    def setOperationSystem(self, newOperationSystem):
        self.operationSystem = newOperationSystem


# @package Kaltura
# @subpackage Client
class KalturaSeriesRecording(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            epgId=NotImplemented,
            channelId=NotImplemented,
            seriesId=NotImplemented,
            seasonNumber=NotImplemented,
            type=NotImplemented,
            createDate=NotImplemented,
            updateDate=NotImplemented,
            excludedSeasons=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Kaltura unique ID representing the series recording identifier
        # @var int
        # @readonly
        self.id = id

        # Kaltura EpgId
        # @var int
        self.epgId = epgId

        # Kaltura ChannelId
        # @var int
        self.channelId = channelId

        # Kaltura SeriesId
        # @var string
        self.seriesId = seriesId

        # Kaltura SeasonNumber
        # @var int
        self.seasonNumber = seasonNumber

        # Recording Type: single/series/season
        # @var KalturaRecordingType
        self.type = type

        # Specifies when was the series recording created. Date and time represented as epoch.
        # @var int
        # @readonly
        self.createDate = createDate

        # Specifies when was the series recording last updated. Date and time represented as epoch.
        # @var int
        # @readonly
        self.updateDate = updateDate

        # List of the season numbers to exclude.
        # @var array of KalturaIntegerValue
        # @readonly
        self.excludedSeasons = excludedSeasons


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'epgId': getXmlNodeInt, 
        'channelId': getXmlNodeInt, 
        'seriesId': getXmlNodeText, 
        'seasonNumber': getXmlNodeInt, 
        'type': (KalturaEnumsFactory.createString, "KalturaRecordingType"), 
        'createDate': getXmlNodeInt, 
        'updateDate': getXmlNodeInt, 
        'excludedSeasons': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSeriesRecording.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSeriesRecording")
        kparams.addIntIfDefined("epgId", self.epgId)
        kparams.addIntIfDefined("channelId", self.channelId)
        kparams.addStringIfDefined("seriesId", self.seriesId)
        kparams.addIntIfDefined("seasonNumber", self.seasonNumber)
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getId(self):
        return self.id

    def getEpgId(self):
        return self.epgId

    def setEpgId(self, newEpgId):
        self.epgId = newEpgId

    def getChannelId(self):
        return self.channelId

    def setChannelId(self, newChannelId):
        self.channelId = newChannelId

    def getSeriesId(self):
        return self.seriesId

    def setSeriesId(self, newSeriesId):
        self.seriesId = newSeriesId

    def getSeasonNumber(self):
        return self.seasonNumber

    def setSeasonNumber(self, newSeasonNumber):
        self.seasonNumber = newSeasonNumber

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getCreateDate(self):
        return self.createDate

    def getUpdateDate(self):
        return self.updateDate

    def getExcludedSeasons(self):
        return self.excludedSeasons


# @package Kaltura
# @subpackage Client
class KalturaSeriesRecordingListResponse(KalturaListResponse):
    """Series Recordings info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Series Recordings
        # @var array of KalturaSeriesRecording
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSeriesRecording'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSeriesRecordingListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSeriesRecordingListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPremiumServiceListResponse(KalturaListResponse):
    """Premium services list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of premium services
        # @var array of KalturaHouseholdPremiumService
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaHouseholdPremiumService'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdPremiumServiceListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaHouseholdPremiumServiceListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaCDVRAdapterProfile(KalturaObjectBase):
    """C-DVR Adapter"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isActive=NotImplemented,
            adapterUrl=NotImplemented,
            settings=NotImplemented,
            externalIdentifier=NotImplemented,
            sharedSecret=NotImplemented,
            dynamicLinksSupport=NotImplemented):
        KalturaObjectBase.__init__(self)

        # C-DVR adapter identifier
        # @var int
        # @readonly
        self.id = id

        # C-DVR adapter name
        # @var string
        self.name = name

        # C-DVR adapter active status
        # @var bool
        self.isActive = isActive

        # C-DVR adapter adapter URL
        # @var string
        self.adapterUrl = adapterUrl

        # C-DVR adapter extra parameters
        # @var map
        self.settings = settings

        # C-DVR adapter external identifier
        # @var string
        self.externalIdentifier = externalIdentifier

        # C-DVR shared secret
        # @var string
        # @readonly
        self.sharedSecret = sharedSecret

        # Indicates whether the C-DVR adapter supports dynamic URLs
        # @var bool
        self.dynamicLinksSupport = dynamicLinksSupport


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'isActive': getXmlNodeBool, 
        'adapterUrl': getXmlNodeText, 
        'settings': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'externalIdentifier': getXmlNodeText, 
        'sharedSecret': getXmlNodeText, 
        'dynamicLinksSupport': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCDVRAdapterProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCDVRAdapterProfile")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("adapterUrl", self.adapterUrl)
        kparams.addMapIfDefined("settings", self.settings)
        kparams.addStringIfDefined("externalIdentifier", self.externalIdentifier)
        kparams.addBoolIfDefined("dynamicLinksSupport", self.dynamicLinksSupport)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getAdapterUrl(self):
        return self.adapterUrl

    def setAdapterUrl(self, newAdapterUrl):
        self.adapterUrl = newAdapterUrl

    def getSettings(self):
        return self.settings

    def setSettings(self, newSettings):
        self.settings = newSettings

    def getExternalIdentifier(self):
        return self.externalIdentifier

    def setExternalIdentifier(self, newExternalIdentifier):
        self.externalIdentifier = newExternalIdentifier

    def getSharedSecret(self):
        return self.sharedSecret

    def getDynamicLinksSupport(self):
        return self.dynamicLinksSupport

    def setDynamicLinksSupport(self, newDynamicLinksSupport):
        self.dynamicLinksSupport = newDynamicLinksSupport


# @package Kaltura
# @subpackage Client
class KalturaCDVRAdapterProfileListResponse(KalturaListResponse):
    """C-DVR adapter profiles"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # C-DVR adapter profiles
        # @var array of KalturaCDVRAdapterProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaCDVRAdapterProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCDVRAdapterProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaCDVRAdapterProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaRecording(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            status=NotImplemented,
            assetId=NotImplemented,
            type=NotImplemented,
            viewableUntilDate=NotImplemented,
            isProtected=NotImplemented,
            createDate=NotImplemented,
            updateDate=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Kaltura unique ID representing the recording identifier
        # @var int
        # @readonly
        self.id = id

        # Recording state: scheduled/recording/recorded/canceled/failed/does_not_exists/deleted
        # @var KalturaRecordingStatus
        # @readonly
        self.status = status

        # Kaltura unique ID representing the program identifier
        # @var int
        self.assetId = assetId

        # Recording Type: single/season/series
        # @var KalturaRecordingType
        # @readonly
        self.type = type

        # Specifies until when the recording is available for viewing. Date and time represented as epoch.
        # @var int
        # @readonly
        self.viewableUntilDate = viewableUntilDate

        # Specifies whether or not the recording is protected
        # @var bool
        # @readonly
        self.isProtected = isProtected

        # Specifies when was the recording created. Date and time represented as epoch.
        # @var int
        # @readonly
        self.createDate = createDate

        # Specifies when was the recording last updated. Date and time represented as epoch.
        # @var int
        # @readonly
        self.updateDate = updateDate


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'status': (KalturaEnumsFactory.createString, "KalturaRecordingStatus"), 
        'assetId': getXmlNodeInt, 
        'type': (KalturaEnumsFactory.createString, "KalturaRecordingType"), 
        'viewableUntilDate': getXmlNodeInt, 
        'isProtected': getXmlNodeBool, 
        'createDate': getXmlNodeInt, 
        'updateDate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecording.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRecording")
        kparams.addIntIfDefined("assetId", self.assetId)
        return kparams

    def getId(self):
        return self.id

    def getStatus(self):
        return self.status

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId

    def getType(self):
        return self.type

    def getViewableUntilDate(self):
        return self.viewableUntilDate

    def getIsProtected(self):
        return self.isProtected

    def getCreateDate(self):
        return self.createDate

    def getUpdateDate(self):
        return self.updateDate


# @package Kaltura
# @subpackage Client
class KalturaRecordingListResponse(KalturaListResponse):
    """Recordings info wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Recordings
        # @var array of KalturaRecording
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaRecording'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecordingListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaRecordingListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaBillingTransaction(KalturaObjectBase):
    """Billing Transaction"""

    def __init__(self,
            recieptCode=NotImplemented,
            purchasedItemName=NotImplemented,
            purchasedItemCode=NotImplemented,
            itemType=NotImplemented,
            billingAction=NotImplemented,
            price=NotImplemented,
            actionDate=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            paymentMethod=NotImplemented,
            paymentMethodExtraDetails=NotImplemented,
            isRecurring=NotImplemented,
            billingProviderRef=NotImplemented,
            purchaseId=NotImplemented,
            remarks=NotImplemented,
            billingPriceType=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Reciept Code
        # @var string
        # @readonly
        self.recieptCode = recieptCode

        # Purchased Item Name
        # @var string
        # @readonly
        self.purchasedItemName = purchasedItemName

        # Purchased Item Code
        # @var string
        # @readonly
        self.purchasedItemCode = purchasedItemCode

        # Item Type
        # @var KalturaBillingItemsType
        # @readonly
        self.itemType = itemType

        # Billing Action
        # @var KalturaBillingAction
        # @readonly
        self.billingAction = billingAction

        # price
        # @var KalturaPrice
        # @readonly
        self.price = price

        # Action Date
        # @var int
        # @readonly
        self.actionDate = actionDate

        # Start Date
        # @var int
        # @readonly
        self.startDate = startDate

        # End Date
        # @var int
        # @readonly
        self.endDate = endDate

        # Payment Method
        # @var KalturaPaymentMethodType
        # @readonly
        self.paymentMethod = paymentMethod

        # Payment Method Extra Details
        # @var string
        # @readonly
        self.paymentMethodExtraDetails = paymentMethodExtraDetails

        # Is Recurring
        # @var bool
        # @readonly
        self.isRecurring = isRecurring

        # Billing Provider Ref
        # @var int
        # @readonly
        self.billingProviderRef = billingProviderRef

        # Purchase ID
        # @var int
        # @readonly
        self.purchaseId = purchaseId

        # Remarks
        # @var string
        # @readonly
        self.remarks = remarks

        # Billing Price Info
        # @var KalturaBillingPriceType
        # @readonly
        self.billingPriceType = billingPriceType


    PROPERTY_LOADERS = {
        'recieptCode': getXmlNodeText, 
        'purchasedItemName': getXmlNodeText, 
        'purchasedItemCode': getXmlNodeText, 
        'itemType': (KalturaEnumsFactory.createString, "KalturaBillingItemsType"), 
        'billingAction': (KalturaEnumsFactory.createString, "KalturaBillingAction"), 
        'price': (KalturaObjectFactory.create, 'KalturaPrice'), 
        'actionDate': getXmlNodeInt, 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'paymentMethod': (KalturaEnumsFactory.createString, "KalturaPaymentMethodType"), 
        'paymentMethodExtraDetails': getXmlNodeText, 
        'isRecurring': getXmlNodeBool, 
        'billingProviderRef': getXmlNodeInt, 
        'purchaseId': getXmlNodeInt, 
        'remarks': getXmlNodeText, 
        'billingPriceType': (KalturaEnumsFactory.createString, "KalturaBillingPriceType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBillingTransaction.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaBillingTransaction")
        return kparams

    def getRecieptCode(self):
        return self.recieptCode

    def getPurchasedItemName(self):
        return self.purchasedItemName

    def getPurchasedItemCode(self):
        return self.purchasedItemCode

    def getItemType(self):
        return self.itemType

    def getBillingAction(self):
        return self.billingAction

    def getPrice(self):
        return self.price

    def getActionDate(self):
        return self.actionDate

    def getStartDate(self):
        return self.startDate

    def getEndDate(self):
        return self.endDate

    def getPaymentMethod(self):
        return self.paymentMethod

    def getPaymentMethodExtraDetails(self):
        return self.paymentMethodExtraDetails

    def getIsRecurring(self):
        return self.isRecurring

    def getBillingProviderRef(self):
        return self.billingProviderRef

    def getPurchaseId(self):
        return self.purchaseId

    def getRemarks(self):
        return self.remarks

    def getBillingPriceType(self):
        return self.billingPriceType


# @package Kaltura
# @subpackage Client
class KalturaBillingTransactionListResponse(KalturaListResponse):
    """Billing Transactions"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Transactions
        # @var array of KalturaBillingTransaction
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaBillingTransaction'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBillingTransactionListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaBillingTransactionListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaEntitlement(KalturaObjectBase):
    """Entitlement"""

    def __init__(self,
            id=NotImplemented,
            productId=NotImplemented,
            currentUses=NotImplemented,
            endDate=NotImplemented,
            currentDate=NotImplemented,
            lastViewDate=NotImplemented,
            purchaseDate=NotImplemented,
            paymentMethod=NotImplemented,
            deviceUdid=NotImplemented,
            deviceName=NotImplemented,
            isCancelationWindowEnabled=NotImplemented,
            maxUses=NotImplemented,
            userId=NotImplemented,
            householdId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Purchase identifier (for subscriptions and collections only)
        # @var int
        # @readonly
        self.id = id

        # Product identifier
        # @var string
        # @readonly
        self.productId = productId

        # The current number of uses
        # @var int
        # @readonly
        self.currentUses = currentUses

        # The end date of the entitlement
        # @var int
        # @readonly
        self.endDate = endDate

        # Current date
        # @var int
        # @readonly
        self.currentDate = currentDate

        # The last date the item was viewed
        # @var int
        # @readonly
        self.lastViewDate = lastViewDate

        # Purchase date
        # @var int
        # @readonly
        self.purchaseDate = purchaseDate

        # Payment Method
        # @var KalturaPaymentMethodType
        # @readonly
        self.paymentMethod = paymentMethod

        # The UDID of the device from which the purchase was made
        # @var string
        # @readonly
        self.deviceUdid = deviceUdid

        # The name of the device from which the purchase was made
        # @var string
        # @readonly
        self.deviceName = deviceName

        # Indicates whether a cancelation window period is enabled
        # @var bool
        # @readonly
        self.isCancelationWindowEnabled = isCancelationWindowEnabled

        # The maximum number of uses available for this item (only for subscription and PPV)
        # @var int
        # @readonly
        self.maxUses = maxUses

        # The Identifier of the purchasing user
        # @var string
        # @readonly
        self.userId = userId

        # The Identifier of the purchasing household
        # @var int
        # @readonly
        self.householdId = householdId


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'productId': getXmlNodeText, 
        'currentUses': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'currentDate': getXmlNodeInt, 
        'lastViewDate': getXmlNodeInt, 
        'purchaseDate': getXmlNodeInt, 
        'paymentMethod': (KalturaEnumsFactory.createString, "KalturaPaymentMethodType"), 
        'deviceUdid': getXmlNodeText, 
        'deviceName': getXmlNodeText, 
        'isCancelationWindowEnabled': getXmlNodeBool, 
        'maxUses': getXmlNodeInt, 
        'userId': getXmlNodeText, 
        'householdId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEntitlement.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaEntitlement")
        return kparams

    def getId(self):
        return self.id

    def getProductId(self):
        return self.productId

    def getCurrentUses(self):
        return self.currentUses

    def getEndDate(self):
        return self.endDate

    def getCurrentDate(self):
        return self.currentDate

    def getLastViewDate(self):
        return self.lastViewDate

    def getPurchaseDate(self):
        return self.purchaseDate

    def getPaymentMethod(self):
        return self.paymentMethod

    def getDeviceUdid(self):
        return self.deviceUdid

    def getDeviceName(self):
        return self.deviceName

    def getIsCancelationWindowEnabled(self):
        return self.isCancelationWindowEnabled

    def getMaxUses(self):
        return self.maxUses

    def getUserId(self):
        return self.userId

    def getHouseholdId(self):
        return self.householdId


# @package Kaltura
# @subpackage Client
class KalturaEntitlementListResponse(KalturaListResponse):
    """Entitlements list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of entitlements
        # @var array of KalturaEntitlement
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaEntitlement'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEntitlementListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaEntitlementListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaCollectionEntitlement(KalturaEntitlement):
    def __init__(self,
            id=NotImplemented,
            productId=NotImplemented,
            currentUses=NotImplemented,
            endDate=NotImplemented,
            currentDate=NotImplemented,
            lastViewDate=NotImplemented,
            purchaseDate=NotImplemented,
            paymentMethod=NotImplemented,
            deviceUdid=NotImplemented,
            deviceName=NotImplemented,
            isCancelationWindowEnabled=NotImplemented,
            maxUses=NotImplemented,
            userId=NotImplemented,
            householdId=NotImplemented):
        KalturaEntitlement.__init__(self,
            id,
            productId,
            currentUses,
            endDate,
            currentDate,
            lastViewDate,
            purchaseDate,
            paymentMethod,
            deviceUdid,
            deviceName,
            isCancelationWindowEnabled,
            maxUses,
            userId,
            householdId)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaEntitlement.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCollectionEntitlement.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaEntitlement.toParams(self)
        kparams.put("objectType", "KalturaCollectionEntitlement")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPpvEntitlement(KalturaEntitlement):
    """KalturaPpvEntitlement"""

    def __init__(self,
            id=NotImplemented,
            productId=NotImplemented,
            currentUses=NotImplemented,
            endDate=NotImplemented,
            currentDate=NotImplemented,
            lastViewDate=NotImplemented,
            purchaseDate=NotImplemented,
            paymentMethod=NotImplemented,
            deviceUdid=NotImplemented,
            deviceName=NotImplemented,
            isCancelationWindowEnabled=NotImplemented,
            maxUses=NotImplemented,
            userId=NotImplemented,
            householdId=NotImplemented,
            mediaFileId=NotImplemented,
            mediaId=NotImplemented):
        KalturaEntitlement.__init__(self,
            id,
            productId,
            currentUses,
            endDate,
            currentDate,
            lastViewDate,
            purchaseDate,
            paymentMethod,
            deviceUdid,
            deviceName,
            isCancelationWindowEnabled,
            maxUses,
            userId,
            householdId)

        # Media file identifier
        # @var int
        # @readonly
        self.mediaFileId = mediaFileId

        # Media identifier
        # @var int
        # @readonly
        self.mediaId = mediaId


    PROPERTY_LOADERS = {
        'mediaFileId': getXmlNodeInt, 
        'mediaId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaEntitlement.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPpvEntitlement.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaEntitlement.toParams(self)
        kparams.put("objectType", "KalturaPpvEntitlement")
        return kparams

    def getMediaFileId(self):
        return self.mediaFileId

    def getMediaId(self):
        return self.mediaId


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionEntitlement(KalturaEntitlement):
    """KalturaSubscriptionEntitlement"""

    def __init__(self,
            id=NotImplemented,
            productId=NotImplemented,
            currentUses=NotImplemented,
            endDate=NotImplemented,
            currentDate=NotImplemented,
            lastViewDate=NotImplemented,
            purchaseDate=NotImplemented,
            paymentMethod=NotImplemented,
            deviceUdid=NotImplemented,
            deviceName=NotImplemented,
            isCancelationWindowEnabled=NotImplemented,
            maxUses=NotImplemented,
            userId=NotImplemented,
            householdId=NotImplemented,
            nextRenewalDate=NotImplemented,
            isRenewableForPurchase=NotImplemented,
            isRenewable=NotImplemented,
            isInGracePeriod=NotImplemented,
            paymentGatewayId=NotImplemented,
            paymentMethodId=NotImplemented,
            scheduledSubscriptionId=NotImplemented,
            unifiedPaymentId=NotImplemented,
            isSuspended=NotImplemented):
        KalturaEntitlement.__init__(self,
            id,
            productId,
            currentUses,
            endDate,
            currentDate,
            lastViewDate,
            purchaseDate,
            paymentMethod,
            deviceUdid,
            deviceName,
            isCancelationWindowEnabled,
            maxUses,
            userId,
            householdId)

        # The date of the next renewal (only for subscription)
        # @var int
        # @readonly
        self.nextRenewalDate = nextRenewalDate

        # Indicates whether the subscription is renewable in this purchase (only for subscription)
        # @var bool
        # @readonly
        self.isRenewableForPurchase = isRenewableForPurchase

        # Indicates whether a subscription is renewable (only for subscription)
        # @var bool
        # @readonly
        self.isRenewable = isRenewable

        # Indicates whether the user is currently in his grace period entitlement
        # @var bool
        # @readonly
        self.isInGracePeriod = isInGracePeriod

        # Payment Gateway identifier
        # @var int
        self.paymentGatewayId = paymentGatewayId

        # Payment Method identifier
        # @var int
        self.paymentMethodId = paymentMethodId

        # Scheduled Subscription Identifier
        # @var int
        self.scheduledSubscriptionId = scheduledSubscriptionId

        # Unified payment identifier
        # @var int
        self.unifiedPaymentId = unifiedPaymentId

        # Indicates if the subscription suspended
        # @var bool
        # @readonly
        self.isSuspended = isSuspended


    PROPERTY_LOADERS = {
        'nextRenewalDate': getXmlNodeInt, 
        'isRenewableForPurchase': getXmlNodeBool, 
        'isRenewable': getXmlNodeBool, 
        'isInGracePeriod': getXmlNodeBool, 
        'paymentGatewayId': getXmlNodeInt, 
        'paymentMethodId': getXmlNodeInt, 
        'scheduledSubscriptionId': getXmlNodeInt, 
        'unifiedPaymentId': getXmlNodeInt, 
        'isSuspended': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaEntitlement.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionEntitlement.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaEntitlement.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionEntitlement")
        kparams.addIntIfDefined("paymentGatewayId", self.paymentGatewayId)
        kparams.addIntIfDefined("paymentMethodId", self.paymentMethodId)
        kparams.addIntIfDefined("scheduledSubscriptionId", self.scheduledSubscriptionId)
        kparams.addIntIfDefined("unifiedPaymentId", self.unifiedPaymentId)
        return kparams

    def getNextRenewalDate(self):
        return self.nextRenewalDate

    def getIsRenewableForPurchase(self):
        return self.isRenewableForPurchase

    def getIsRenewable(self):
        return self.isRenewable

    def getIsInGracePeriod(self):
        return self.isInGracePeriod

    def getPaymentGatewayId(self):
        return self.paymentGatewayId

    def setPaymentGatewayId(self, newPaymentGatewayId):
        self.paymentGatewayId = newPaymentGatewayId

    def getPaymentMethodId(self):
        return self.paymentMethodId

    def setPaymentMethodId(self, newPaymentMethodId):
        self.paymentMethodId = newPaymentMethodId

    def getScheduledSubscriptionId(self):
        return self.scheduledSubscriptionId

    def setScheduledSubscriptionId(self, newScheduledSubscriptionId):
        self.scheduledSubscriptionId = newScheduledSubscriptionId

    def getUnifiedPaymentId(self):
        return self.unifiedPaymentId

    def setUnifiedPaymentId(self, newUnifiedPaymentId):
        self.unifiedPaymentId = newUnifiedPaymentId

    def getIsSuspended(self):
        return self.isSuspended


# @package Kaltura
# @subpackage Client
class KalturaAssetCount(KalturaObjectBase):
    """Asset count - represents a specific value of the field, its count and its sub groups."""

    def __init__(self,
            value=NotImplemented,
            count=NotImplemented,
            subs=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Value
        # @var string
        self.value = value

        # Count
        # @var int
        self.count = count

        # Sub groups
        # @var array of KalturaAssetsCount
        self.subs = subs


    PROPERTY_LOADERS = {
        'value': getXmlNodeText, 
        'count': getXmlNodeInt, 
        'subs': (KalturaObjectFactory.createArray, 'KalturaAssetsCount'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetCount.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetCount")
        kparams.addStringIfDefined("value", self.value)
        kparams.addIntIfDefined("count", self.count)
        kparams.addArrayIfDefined("subs", self.subs)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue

    def getCount(self):
        return self.count

    def setCount(self, newCount):
        self.count = newCount

    def getSubs(self):
        return self.subs

    def setSubs(self, newSubs):
        self.subs = newSubs


# @package Kaltura
# @subpackage Client
class KalturaAssetsCount(KalturaObjectBase):
    """Single aggregation objects"""

    def __init__(self,
            field=NotImplemented,
            objects=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Field name
        # @var string
        self.field = field

        # Values, their count and sub groups
        # @var array of KalturaAssetCount
        self.objects = objects


    PROPERTY_LOADERS = {
        'field': getXmlNodeText, 
        'objects': (KalturaObjectFactory.createArray, 'KalturaAssetCount'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetsCount.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetsCount")
        kparams.addStringIfDefined("field", self.field)
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getField(self):
        return self.field

    def setField(self, newField):
        self.field = newField

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaAssetCountListResponse(KalturaListResponse):
    """Asset counts wrapper - represents a group"""

    def __init__(self,
            totalCount=NotImplemented,
            assetsCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Count of assets that match filter result, regardless of group by result
        # @var int
        self.assetsCount = assetsCount

        # List of groupings (field name and sub-list of values and their counts)
        # @var array of KalturaAssetsCount
        self.objects = objects


    PROPERTY_LOADERS = {
        'assetsCount': getXmlNodeInt, 
        'objects': (KalturaObjectFactory.createArray, 'KalturaAssetsCount'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetCountListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaAssetCountListResponse")
        kparams.addIntIfDefined("assetsCount", self.assetsCount)
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getAssetsCount(self):
        return self.assetsCount

    def setAssetsCount(self, newAssetsCount):
        self.assetsCount = newAssetsCount

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaSlimAsset(KalturaObjectBase):
    """Slim Asset Details"""

    def __init__(self,
            id=NotImplemented,
            type=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Internal identifier of the asset
        # @var string
        # @insertonly
        self.id = id

        # The type of the asset. Possible values: media, recording, epg
        # @var KalturaAssetType
        # @insertonly
        self.type = type


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'type': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSlimAsset.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSlimAsset")
        kparams.addStringIfDefined("id", self.id)
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType


# @package Kaltura
# @subpackage Client
class KalturaBookmarkPlayerData(KalturaObjectBase):
    def __init__(self,
            action=NotImplemented,
            averageBitrate=NotImplemented,
            totalBitrate=NotImplemented,
            currentBitrate=NotImplemented,
            fileId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Action
        # @var KalturaBookmarkActionType
        self.action = action

        # Average Bitrate
        # @var int
        self.averageBitrate = averageBitrate

        # Total Bitrate
        # @var int
        self.totalBitrate = totalBitrate

        # Current Bitrate
        # @var int
        self.currentBitrate = currentBitrate

        # Identifier of the file
        # @var int
        self.fileId = fileId


    PROPERTY_LOADERS = {
        'action': (KalturaEnumsFactory.createString, "KalturaBookmarkActionType"), 
        'averageBitrate': getXmlNodeInt, 
        'totalBitrate': getXmlNodeInt, 
        'currentBitrate': getXmlNodeInt, 
        'fileId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBookmarkPlayerData.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaBookmarkPlayerData")
        kparams.addStringEnumIfDefined("action", self.action)
        kparams.addIntIfDefined("averageBitrate", self.averageBitrate)
        kparams.addIntIfDefined("totalBitrate", self.totalBitrate)
        kparams.addIntIfDefined("currentBitrate", self.currentBitrate)
        kparams.addIntIfDefined("fileId", self.fileId)
        return kparams

    def getAction(self):
        return self.action

    def setAction(self, newAction):
        self.action = newAction

    def getAverageBitrate(self):
        return self.averageBitrate

    def setAverageBitrate(self, newAverageBitrate):
        self.averageBitrate = newAverageBitrate

    def getTotalBitrate(self):
        return self.totalBitrate

    def setTotalBitrate(self, newTotalBitrate):
        self.totalBitrate = newTotalBitrate

    def getCurrentBitrate(self):
        return self.currentBitrate

    def setCurrentBitrate(self, newCurrentBitrate):
        self.currentBitrate = newCurrentBitrate

    def getFileId(self):
        return self.fileId

    def setFileId(self, newFileId):
        self.fileId = newFileId


# @package Kaltura
# @subpackage Client
class KalturaBookmark(KalturaSlimAsset):
    def __init__(self,
            id=NotImplemented,
            type=NotImplemented,
            userId=NotImplemented,
            position=NotImplemented,
            positionOwner=NotImplemented,
            finishedWatching=NotImplemented,
            playerData=NotImplemented):
        KalturaSlimAsset.__init__(self,
            id,
            type)

        # User identifier
        # @var string
        # @readonly
        self.userId = userId

        # The position of the user in the specific asset (in seconds)
        # @var int
        # @insertonly
        self.position = position

        # Indicates who is the owner of this position
        # @var KalturaPositionOwner
        # @readonly
        self.positionOwner = positionOwner

        # Specifies whether the user&#39;s current position exceeded 95% of the duration
        # @var bool
        # @readonly
        self.finishedWatching = finishedWatching

        # Insert only player data
        # @var KalturaBookmarkPlayerData
        self.playerData = playerData


    PROPERTY_LOADERS = {
        'userId': getXmlNodeText, 
        'position': getXmlNodeInt, 
        'positionOwner': (KalturaEnumsFactory.createString, "KalturaPositionOwner"), 
        'finishedWatching': getXmlNodeBool, 
        'playerData': (KalturaObjectFactory.create, 'KalturaBookmarkPlayerData'), 
    }

    def fromXml(self, node):
        KalturaSlimAsset.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBookmark.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSlimAsset.toParams(self)
        kparams.put("objectType", "KalturaBookmark")
        kparams.addIntIfDefined("position", self.position)
        kparams.addObjectIfDefined("playerData", self.playerData)
        return kparams

    def getUserId(self):
        return self.userId

    def getPosition(self):
        return self.position

    def setPosition(self, newPosition):
        self.position = newPosition

    def getPositionOwner(self):
        return self.positionOwner

    def getFinishedWatching(self):
        return self.finishedWatching

    def getPlayerData(self):
        return self.playerData

    def setPlayerData(self, newPlayerData):
        self.playerData = newPlayerData


# @package Kaltura
# @subpackage Client
class KalturaBookmarkListResponse(KalturaListResponse):
    """List of assets and their bookmarks"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Assets
        # @var array of KalturaBookmark
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaBookmark'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBookmarkListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaBookmarkListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaAsset(KalturaObjectBase):
    """Asset info"""

    def __init__(self,
            id=NotImplemented,
            type=NotImplemented,
            name=NotImplemented,
            multilingualName=NotImplemented,
            description=NotImplemented,
            multilingualDescription=NotImplemented,
            images=NotImplemented,
            mediaFiles=NotImplemented,
            metas=NotImplemented,
            tags=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            enableCdvr=NotImplemented,
            enableCatchUp=NotImplemented,
            enableStartOver=NotImplemented,
            enableTrickPlay=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique identifier for the asset
        # @var int
        # @readonly
        self.id = id

        # Identifies the asset type (EPG, Recording, Movie, TV Series, etc). 
        #             Possible values: 0 - EPG linear programs, 1 - Recording; or any asset type ID according to the asset types IDs defined in the system.
        # @var int
        self.type = type

        # Asset name
        # @var string
        # @readonly
        self.name = name

        # Asset name
        # @var array of KalturaTranslationToken
        self.multilingualName = multilingualName

        # Asset description
        # @var string
        # @readonly
        self.description = description

        # Asset description
        # @var array of KalturaTranslationToken
        self.multilingualDescription = multilingualDescription

        # Collection of images details that can be used to represent this asset
        # @var array of KalturaMediaImage
        self.images = images

        # Files
        # @var array of KalturaMediaFile
        self.mediaFiles = mediaFiles

        # Dynamic collection of key-value pairs according to the String Meta defined in the system
        # @var map
        self.metas = metas

        # Dynamic collection of key-value pairs according to the Tag Types defined in the system
        # @var map
        self.tags = tags

        # Date and time represented as epoch. For VOD - since when the asset is available in the catalog. For EPG/Linear - when the program is aired (can be in the future).
        # @var int
        self.startDate = startDate

        # Date and time represented as epoch. For VOD - till when the asset be available in the catalog. For EPG/Linear - program end time and date
        # @var int
        self.endDate = endDate

        # Enable cDVR
        # @var bool
        self.enableCdvr = enableCdvr

        # Enable catch-up
        # @var bool
        self.enableCatchUp = enableCatchUp

        # Enable start over
        # @var bool
        self.enableStartOver = enableStartOver

        # Enable trick-play
        # @var bool
        self.enableTrickPlay = enableTrickPlay


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'type': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'multilingualName': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'description': getXmlNodeText, 
        'multilingualDescription': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'images': (KalturaObjectFactory.createArray, 'KalturaMediaImage'), 
        'mediaFiles': (KalturaObjectFactory.createArray, 'KalturaMediaFile'), 
        'metas': (KalturaObjectFactory.createMap, 'KalturaValue'), 
        'tags': (KalturaObjectFactory.createMap, 'KalturaMultilingualStringValueArray'), 
        'startDate': getXmlNodeInt, 
        'endDate': getXmlNodeInt, 
        'enableCdvr': getXmlNodeBool, 
        'enableCatchUp': getXmlNodeBool, 
        'enableStartOver': getXmlNodeBool, 
        'enableTrickPlay': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAsset.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAsset")
        kparams.addIntIfDefined("type", self.type)
        kparams.addArrayIfDefined("multilingualName", self.multilingualName)
        kparams.addArrayIfDefined("multilingualDescription", self.multilingualDescription)
        kparams.addArrayIfDefined("images", self.images)
        kparams.addArrayIfDefined("mediaFiles", self.mediaFiles)
        kparams.addMapIfDefined("metas", self.metas)
        kparams.addMapIfDefined("tags", self.tags)
        kparams.addIntIfDefined("startDate", self.startDate)
        kparams.addIntIfDefined("endDate", self.endDate)
        kparams.addBoolIfDefined("enableCdvr", self.enableCdvr)
        kparams.addBoolIfDefined("enableCatchUp", self.enableCatchUp)
        kparams.addBoolIfDefined("enableStartOver", self.enableStartOver)
        kparams.addBoolIfDefined("enableTrickPlay", self.enableTrickPlay)
        return kparams

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getName(self):
        return self.name

    def getMultilingualName(self):
        return self.multilingualName

    def setMultilingualName(self, newMultilingualName):
        self.multilingualName = newMultilingualName

    def getDescription(self):
        return self.description

    def getMultilingualDescription(self):
        return self.multilingualDescription

    def setMultilingualDescription(self, newMultilingualDescription):
        self.multilingualDescription = newMultilingualDescription

    def getImages(self):
        return self.images

    def setImages(self, newImages):
        self.images = newImages

    def getMediaFiles(self):
        return self.mediaFiles

    def setMediaFiles(self, newMediaFiles):
        self.mediaFiles = newMediaFiles

    def getMetas(self):
        return self.metas

    def setMetas(self, newMetas):
        self.metas = newMetas

    def getTags(self):
        return self.tags

    def setTags(self, newTags):
        self.tags = newTags

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate

    def getEndDate(self):
        return self.endDate

    def setEndDate(self, newEndDate):
        self.endDate = newEndDate

    def getEnableCdvr(self):
        return self.enableCdvr

    def setEnableCdvr(self, newEnableCdvr):
        self.enableCdvr = newEnableCdvr

    def getEnableCatchUp(self):
        return self.enableCatchUp

    def setEnableCatchUp(self, newEnableCatchUp):
        self.enableCatchUp = newEnableCatchUp

    def getEnableStartOver(self):
        return self.enableStartOver

    def setEnableStartOver(self, newEnableStartOver):
        self.enableStartOver = newEnableStartOver

    def getEnableTrickPlay(self):
        return self.enableTrickPlay

    def setEnableTrickPlay(self, newEnableTrickPlay):
        self.enableTrickPlay = newEnableTrickPlay


# @package Kaltura
# @subpackage Client
class KalturaAssetListResponse(KalturaListResponse):
    """Asset wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Assets
        # @var array of KalturaAsset
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaAsset'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaAssetListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaProgramAsset(KalturaAsset):
    """Program-asset info"""

    def __init__(self,
            id=NotImplemented,
            type=NotImplemented,
            name=NotImplemented,
            multilingualName=NotImplemented,
            description=NotImplemented,
            multilingualDescription=NotImplemented,
            images=NotImplemented,
            mediaFiles=NotImplemented,
            metas=NotImplemented,
            tags=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            enableCdvr=NotImplemented,
            enableCatchUp=NotImplemented,
            enableStartOver=NotImplemented,
            enableTrickPlay=NotImplemented,
            epgChannelId=NotImplemented,
            epgId=NotImplemented,
            relatedMediaId=NotImplemented,
            crid=NotImplemented,
            linearAssetId=NotImplemented):
        KalturaAsset.__init__(self,
            id,
            type,
            name,
            multilingualName,
            description,
            multilingualDescription,
            images,
            mediaFiles,
            metas,
            tags,
            startDate,
            endDate,
            enableCdvr,
            enableCatchUp,
            enableStartOver,
            enableTrickPlay)

        # EPG channel identifier
        # @var int
        self.epgChannelId = epgChannelId

        # EPG identifier
        # @var string
        self.epgId = epgId

        # Ralated media identifier
        # @var int
        self.relatedMediaId = relatedMediaId

        # Unique identifier for the program
        # @var string
        self.crid = crid

        # Id of linear media asset
        # @var int
        self.linearAssetId = linearAssetId


    PROPERTY_LOADERS = {
        'epgChannelId': getXmlNodeInt, 
        'epgId': getXmlNodeText, 
        'relatedMediaId': getXmlNodeInt, 
        'crid': getXmlNodeText, 
        'linearAssetId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaAsset.fromXml(self, node)
        self.fromXmlImpl(node, KalturaProgramAsset.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAsset.toParams(self)
        kparams.put("objectType", "KalturaProgramAsset")
        kparams.addIntIfDefined("epgChannelId", self.epgChannelId)
        kparams.addStringIfDefined("epgId", self.epgId)
        kparams.addIntIfDefined("relatedMediaId", self.relatedMediaId)
        kparams.addStringIfDefined("crid", self.crid)
        kparams.addIntIfDefined("linearAssetId", self.linearAssetId)
        return kparams

    def getEpgChannelId(self):
        return self.epgChannelId

    def setEpgChannelId(self, newEpgChannelId):
        self.epgChannelId = newEpgChannelId

    def getEpgId(self):
        return self.epgId

    def setEpgId(self, newEpgId):
        self.epgId = newEpgId

    def getRelatedMediaId(self):
        return self.relatedMediaId

    def setRelatedMediaId(self, newRelatedMediaId):
        self.relatedMediaId = newRelatedMediaId

    def getCrid(self):
        return self.crid

    def setCrid(self, newCrid):
        self.crid = newCrid

    def getLinearAssetId(self):
        return self.linearAssetId

    def setLinearAssetId(self, newLinearAssetId):
        self.linearAssetId = newLinearAssetId


# @package Kaltura
# @subpackage Client
class KalturaRecordingAsset(KalturaProgramAsset):
    """Recording-asset info"""

    def __init__(self,
            id=NotImplemented,
            type=NotImplemented,
            name=NotImplemented,
            multilingualName=NotImplemented,
            description=NotImplemented,
            multilingualDescription=NotImplemented,
            images=NotImplemented,
            mediaFiles=NotImplemented,
            metas=NotImplemented,
            tags=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            enableCdvr=NotImplemented,
            enableCatchUp=NotImplemented,
            enableStartOver=NotImplemented,
            enableTrickPlay=NotImplemented,
            epgChannelId=NotImplemented,
            epgId=NotImplemented,
            relatedMediaId=NotImplemented,
            crid=NotImplemented,
            linearAssetId=NotImplemented,
            recordingId=NotImplemented,
            recordingType=NotImplemented):
        KalturaProgramAsset.__init__(self,
            id,
            type,
            name,
            multilingualName,
            description,
            multilingualDescription,
            images,
            mediaFiles,
            metas,
            tags,
            startDate,
            endDate,
            enableCdvr,
            enableCatchUp,
            enableStartOver,
            enableTrickPlay,
            epgChannelId,
            epgId,
            relatedMediaId,
            crid,
            linearAssetId)

        # Recording identifier
        # @var string
        self.recordingId = recordingId

        # Recording Type: single/season/series
        # @var KalturaRecordingType
        self.recordingType = recordingType


    PROPERTY_LOADERS = {
        'recordingId': getXmlNodeText, 
        'recordingType': (KalturaEnumsFactory.createString, "KalturaRecordingType"), 
    }

    def fromXml(self, node):
        KalturaProgramAsset.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecordingAsset.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaProgramAsset.toParams(self)
        kparams.put("objectType", "KalturaRecordingAsset")
        kparams.addStringIfDefined("recordingId", self.recordingId)
        kparams.addStringEnumIfDefined("recordingType", self.recordingType)
        return kparams

    def getRecordingId(self):
        return self.recordingId

    def setRecordingId(self, newRecordingId):
        self.recordingId = newRecordingId

    def getRecordingType(self):
        return self.recordingType

    def setRecordingType(self, newRecordingType):
        self.recordingType = newRecordingType


# @package Kaltura
# @subpackage Client
class KalturaMediaAsset(KalturaAsset):
    """Media-asset info"""

    def __init__(self,
            id=NotImplemented,
            type=NotImplemented,
            name=NotImplemented,
            multilingualName=NotImplemented,
            description=NotImplemented,
            multilingualDescription=NotImplemented,
            images=NotImplemented,
            mediaFiles=NotImplemented,
            metas=NotImplemented,
            tags=NotImplemented,
            startDate=NotImplemented,
            endDate=NotImplemented,
            enableCdvr=NotImplemented,
            enableCatchUp=NotImplemented,
            enableStartOver=NotImplemented,
            enableTrickPlay=NotImplemented,
            externalIds=NotImplemented,
            catchUpBuffer=NotImplemented,
            trickPlayBuffer=NotImplemented,
            enableRecordingPlaybackNonEntitledChannel=NotImplemented,
            entryId=NotImplemented):
        KalturaAsset.__init__(self,
            id,
            type,
            name,
            multilingualName,
            description,
            multilingualDescription,
            images,
            mediaFiles,
            metas,
            tags,
            startDate,
            endDate,
            enableCdvr,
            enableCatchUp,
            enableStartOver,
            enableTrickPlay)

        # External identifiers
        # @var string
        self.externalIds = externalIds

        # Catch-up buffer
        # @var int
        self.catchUpBuffer = catchUpBuffer

        # Trick-play buffer
        # @var int
        self.trickPlayBuffer = trickPlayBuffer

        # Enable Recording playback for non entitled channel
        # @var bool
        # @readonly
        self.enableRecordingPlaybackNonEntitledChannel = enableRecordingPlaybackNonEntitledChannel

        # Entry Identifier
        # @var string
        self.entryId = entryId


    PROPERTY_LOADERS = {
        'externalIds': getXmlNodeText, 
        'catchUpBuffer': getXmlNodeInt, 
        'trickPlayBuffer': getXmlNodeInt, 
        'enableRecordingPlaybackNonEntitledChannel': getXmlNodeBool, 
        'entryId': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaAsset.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMediaAsset.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAsset.toParams(self)
        kparams.put("objectType", "KalturaMediaAsset")
        kparams.addStringIfDefined("externalIds", self.externalIds)
        kparams.addIntIfDefined("catchUpBuffer", self.catchUpBuffer)
        kparams.addIntIfDefined("trickPlayBuffer", self.trickPlayBuffer)
        kparams.addStringIfDefined("entryId", self.entryId)
        return kparams

    def getExternalIds(self):
        return self.externalIds

    def setExternalIds(self, newExternalIds):
        self.externalIds = newExternalIds

    def getCatchUpBuffer(self):
        return self.catchUpBuffer

    def setCatchUpBuffer(self, newCatchUpBuffer):
        self.catchUpBuffer = newCatchUpBuffer

    def getTrickPlayBuffer(self):
        return self.trickPlayBuffer

    def setTrickPlayBuffer(self, newTrickPlayBuffer):
        self.trickPlayBuffer = newTrickPlayBuffer

    def getEnableRecordingPlaybackNonEntitledChannel(self):
        return self.enableRecordingPlaybackNonEntitledChannel

    def getEntryId(self):
        return self.entryId

    def setEntryId(self, newEntryId):
        self.entryId = newEntryId


# @package Kaltura
# @subpackage Client
class KalturaAssetCommentListResponse(KalturaListResponse):
    """Asset Comment Response"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Assets
        # @var array of KalturaAssetComment
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaAssetComment'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetCommentListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaAssetCommentListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaAssetStatisticsListResponse(KalturaListResponse):
    """List of assets statistics"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Assets
        # @var array of KalturaAssetStatistics
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaAssetStatistics'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetStatisticsListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaAssetStatisticsListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaAssetHistory(KalturaObjectBase):
    """Watch history asset info"""

    def __init__(self,
            assetId=NotImplemented,
            assetType=NotImplemented,
            position=NotImplemented,
            duration=NotImplemented,
            watchedDate=NotImplemented,
            finishedWatching=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Asset identifier
        # @var int
        # @readonly
        self.assetId = assetId

        # Asset identifier
        # @var KalturaAssetType
        # @readonly
        self.assetType = assetType

        # Position in seconds of the relevant asset
        # @var int
        # @readonly
        self.position = position

        # Duration in seconds of the relevant asset
        # @var int
        # @readonly
        self.duration = duration

        # The date when the media was last watched
        # @var int
        # @readonly
        self.watchedDate = watchedDate

        # Boolean which specifies whether the user finished watching the movie or not
        # @var bool
        # @readonly
        self.finishedWatching = finishedWatching


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeInt, 
        'assetType': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'position': getXmlNodeInt, 
        'duration': getXmlNodeInt, 
        'watchedDate': getXmlNodeInt, 
        'finishedWatching': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetHistory.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetHistory")
        return kparams

    def getAssetId(self):
        return self.assetId

    def getAssetType(self):
        return self.assetType

    def getPosition(self):
        return self.position

    def getDuration(self):
        return self.duration

    def getWatchedDate(self):
        return self.watchedDate

    def getFinishedWatching(self):
        return self.finishedWatching


# @package Kaltura
# @subpackage Client
class KalturaAssetHistoryListResponse(KalturaListResponse):
    """Watch history asset wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # WatchHistoryAssets Models
        # @var array of KalturaAssetHistory
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaAssetHistory'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetHistoryListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaAssetHistoryListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaCurrency(KalturaObjectBase):
    """Currency details"""

    def __init__(self,
            name=NotImplemented,
            code=NotImplemented,
            sign=NotImplemented,
            isDefault=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Currency name
        # @var string
        self.name = name

        # Currency code
        # @var string
        self.code = code

        # Currency Sign
        # @var string
        self.sign = sign

        # Is the default Currency of the account
        # @var bool
        self.isDefault = isDefault


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'code': getXmlNodeText, 
        'sign': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCurrency.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCurrency")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("code", self.code)
        kparams.addStringIfDefined("sign", self.sign)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getCode(self):
        return self.code

    def setCode(self, newCode):
        self.code = newCode

    def getSign(self):
        return self.sign

    def setSign(self, newSign):
        self.sign = newSign

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault


# @package Kaltura
# @subpackage Client
class KalturaCurrencyListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Currencies
        # @var array of KalturaCurrency
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaCurrency'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCurrencyListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaCurrencyListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaLanguage(KalturaObjectBase):
    """Language details"""

    def __init__(self,
            name=NotImplemented,
            systemName=NotImplemented,
            code=NotImplemented,
            direction=NotImplemented,
            isDefault=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Language name
        # @var string
        self.name = name

        # Language system name
        # @var string
        self.systemName = systemName

        # Language code
        # @var string
        self.code = code

        # Language direction (LTR/RTL)
        # @var string
        self.direction = direction

        # Is the default language of the account
        # @var bool
        self.isDefault = isDefault


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'systemName': getXmlNodeText, 
        'code': getXmlNodeText, 
        'direction': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLanguage.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaLanguage")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("systemName", self.systemName)
        kparams.addStringIfDefined("code", self.code)
        kparams.addStringIfDefined("direction", self.direction)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getSystemName(self):
        return self.systemName

    def setSystemName(self, newSystemName):
        self.systemName = newSystemName

    def getCode(self):
        return self.code

    def setCode(self, newCode):
        self.code = newCode

    def getDirection(self):
        return self.direction

    def setDirection(self, newDirection):
        self.direction = newDirection

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault


# @package Kaltura
# @subpackage Client
class KalturaLanguageListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Languages
        # @var array of KalturaLanguage
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaLanguage'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLanguageListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaLanguageListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaMeta(KalturaObjectBase):
    """Asset meta"""

    def __init__(self,
            name=NotImplemented,
            fieldName=NotImplemented,
            type=NotImplemented,
            assetType=NotImplemented,
            features=NotImplemented,
            id=NotImplemented,
            parentId=NotImplemented,
            partnerId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Meta name for the partner
        # @var string
        self.name = name

        # Meta system field name
        # @var KalturaMetaFieldName
        self.fieldName = fieldName

        # Meta value type
        # @var KalturaMetaType
        self.type = type

        # Asset type this meta is related to
        # @var KalturaAssetType
        self.assetType = assetType

        # List of supported features
        # @var string
        self.features = features

        # Meta id
        # @var string
        self.id = id

        # Parent meta id
        # @var string
        self.parentId = parentId

        # Partner Id
        # @var int
        self.partnerId = partnerId


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'fieldName': (KalturaEnumsFactory.createString, "KalturaMetaFieldName"), 
        'type': (KalturaEnumsFactory.createString, "KalturaMetaType"), 
        'assetType': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'features': getXmlNodeText, 
        'id': getXmlNodeText, 
        'parentId': getXmlNodeText, 
        'partnerId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMeta.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaMeta")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringEnumIfDefined("fieldName", self.fieldName)
        kparams.addStringEnumIfDefined("type", self.type)
        kparams.addStringEnumIfDefined("assetType", self.assetType)
        kparams.addStringIfDefined("features", self.features)
        kparams.addStringIfDefined("id", self.id)
        kparams.addStringIfDefined("parentId", self.parentId)
        kparams.addIntIfDefined("partnerId", self.partnerId)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getFieldName(self):
        return self.fieldName

    def setFieldName(self, newFieldName):
        self.fieldName = newFieldName

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getAssetType(self):
        return self.assetType

    def setAssetType(self, newAssetType):
        self.assetType = newAssetType

    def getFeatures(self):
        return self.features

    def setFeatures(self, newFeatures):
        self.features = newFeatures

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getParentId(self):
        return self.parentId

    def setParentId(self, newParentId):
        self.parentId = newParentId

    def getPartnerId(self):
        return self.partnerId

    def setPartnerId(self, newPartnerId):
        self.partnerId = newPartnerId


# @package Kaltura
# @subpackage Client
class KalturaMetaListResponse(KalturaListResponse):
    """Meta list response"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list asset meta
        # @var array of KalturaMeta
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaMeta'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMetaListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaMetaListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaDeviceBrand(KalturaObjectBase):
    """Device brand details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            deviceFamilyid=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Device brand identifier
        # @var int
        # @readonly
        self.id = id

        # Device brand name
        # @var string
        self.name = name

        # Device family identifier
        # @var int
        # @readonly
        self.deviceFamilyid = deviceFamilyid


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'deviceFamilyid': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceBrand.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaDeviceBrand")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDeviceFamilyid(self):
        return self.deviceFamilyid


# @package Kaltura
# @subpackage Client
class KalturaDeviceBrandListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Device brands
        # @var array of KalturaDeviceBrand
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaDeviceBrand'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceBrandListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaDeviceBrandListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaCountryListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Countries
        # @var array of KalturaCountry
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaCountry'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCountryListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaCountryListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaOSSAdapterBaseProfile(KalturaObjectBase):
    """OSS adapter basic"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaObjectBase.__init__(self)

        # OSS adapter id
        # @var int
        # @readonly
        self.id = id

        # OSS adapter name
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOSSAdapterBaseProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaOSSAdapterBaseProfile")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaOSSAdapterProfile(KalturaOSSAdapterBaseProfile):
    """OSS Adapter"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isActive=NotImplemented,
            adapterUrl=NotImplemented,
            ossAdapterSettings=NotImplemented,
            externalIdentifier=NotImplemented,
            sharedSecret=NotImplemented):
        KalturaOSSAdapterBaseProfile.__init__(self,
            id,
            name)

        # OSS adapter active status
        # @var bool
        self.isActive = isActive

        # OSS adapter adapter URL
        # @var string
        self.adapterUrl = adapterUrl

        # OSS adapter extra parameters
        # @var map
        self.ossAdapterSettings = ossAdapterSettings

        # OSS adapter external identifier
        # @var string
        self.externalIdentifier = externalIdentifier

        # Shared Secret
        # @var string
        # @readonly
        self.sharedSecret = sharedSecret


    PROPERTY_LOADERS = {
        'isActive': getXmlNodeBool, 
        'adapterUrl': getXmlNodeText, 
        'ossAdapterSettings': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'externalIdentifier': getXmlNodeText, 
        'sharedSecret': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaOSSAdapterBaseProfile.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOSSAdapterProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaOSSAdapterBaseProfile.toParams(self)
        kparams.put("objectType", "KalturaOSSAdapterProfile")
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("adapterUrl", self.adapterUrl)
        kparams.addMapIfDefined("ossAdapterSettings", self.ossAdapterSettings)
        kparams.addStringIfDefined("externalIdentifier", self.externalIdentifier)
        return kparams

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getAdapterUrl(self):
        return self.adapterUrl

    def setAdapterUrl(self, newAdapterUrl):
        self.adapterUrl = newAdapterUrl

    def getOssAdapterSettings(self):
        return self.ossAdapterSettings

    def setOssAdapterSettings(self, newOssAdapterSettings):
        self.ossAdapterSettings = newOssAdapterSettings

    def getExternalIdentifier(self):
        return self.externalIdentifier

    def setExternalIdentifier(self, newExternalIdentifier):
        self.externalIdentifier = newExternalIdentifier

    def getSharedSecret(self):
        return self.sharedSecret


# @package Kaltura
# @subpackage Client
class KalturaOSSAdapterProfileListResponse(KalturaListResponse):
    """OSS adapter-profiles list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of OSS adapter-profiles
        # @var array of KalturaOSSAdapterProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaOSSAdapterProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOSSAdapterProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaOSSAdapterProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaSearchHistory(KalturaObjectBase):
    """Search history info"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            filter=NotImplemented,
            language=NotImplemented,
            createdAt=NotImplemented,
            service=NotImplemented,
            action=NotImplemented,
            deviceId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Search ID
        # @var string
        # @readonly
        self.id = id

        # Search name
        # @var string
        # @readonly
        self.name = name

        # Filter
        # @var string
        # @readonly
        self.filter = filter

        # Search language
        # @var string
        # @readonly
        self.language = language

        # When search was performed
        # @var int
        # @readonly
        self.createdAt = createdAt

        # Kaltura OTT Service
        # @var string
        # @readonly
        self.service = service

        # Kaltura OTT Service Action
        # @var string
        # @readonly
        self.action = action

        # Unique Device ID
        # @var string
        # @readonly
        self.deviceId = deviceId


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
        'filter': getXmlNodeText, 
        'language': getXmlNodeText, 
        'createdAt': getXmlNodeInt, 
        'service': getXmlNodeText, 
        'action': getXmlNodeText, 
        'deviceId': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSearchHistory.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSearchHistory")
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getFilter(self):
        return self.filter

    def getLanguage(self):
        return self.language

    def getCreatedAt(self):
        return self.createdAt

    def getService(self):
        return self.service

    def getAction(self):
        return self.action

    def getDeviceId(self):
        return self.deviceId


# @package Kaltura
# @subpackage Client
class KalturaSearchHistoryListResponse(KalturaListResponse):
    """Search history wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # KalturaSearchHistory Models
        # @var array of KalturaSearchHistory
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaSearchHistory'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSearchHistoryListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaSearchHistoryListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaDeviceFamilyBase(KalturaObjectBase):
    """Device family details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Device family identifier
        # @var int
        # @readonly
        self.id = id

        # Device family name
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceFamilyBase.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaDeviceFamilyBase")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaDeviceFamily(KalturaDeviceFamilyBase):
    """Device family details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented):
        KalturaDeviceFamilyBase.__init__(self,
            id,
            name)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaDeviceFamilyBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceFamily.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaDeviceFamilyBase.toParams(self)
        kparams.put("objectType", "KalturaDeviceFamily")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaDeviceFamilyListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Device families
        # @var array of KalturaDeviceFamily
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaDeviceFamily'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceFamilyListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaDeviceFamilyListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaHouseholdDeviceFamilyLimitations(KalturaDeviceFamilyBase):
    """Device family limitations details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            frequency=NotImplemented,
            deviceLimit=NotImplemented,
            concurrentLimit=NotImplemented):
        KalturaDeviceFamilyBase.__init__(self,
            id,
            name)

        # Allowed device change frequency code
        # @var int
        self.frequency = frequency

        # Max number of devices allowed for this family
        # @var int
        self.deviceLimit = deviceLimit

        # Max number of streams allowed for this family
        # @var int
        self.concurrentLimit = concurrentLimit


    PROPERTY_LOADERS = {
        'frequency': getXmlNodeInt, 
        'deviceLimit': getXmlNodeInt, 
        'concurrentLimit': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaDeviceFamilyBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdDeviceFamilyLimitations.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaDeviceFamilyBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdDeviceFamilyLimitations")
        kparams.addIntIfDefined("frequency", self.frequency)
        kparams.addIntIfDefined("deviceLimit", self.deviceLimit)
        kparams.addIntIfDefined("concurrentLimit", self.concurrentLimit)
        return kparams

    def getFrequency(self):
        return self.frequency

    def setFrequency(self, newFrequency):
        self.frequency = newFrequency

    def getDeviceLimit(self):
        return self.deviceLimit

    def setDeviceLimit(self, newDeviceLimit):
        self.deviceLimit = newDeviceLimit

    def getConcurrentLimit(self):
        return self.concurrentLimit

    def setConcurrentLimit(self, newConcurrentLimit):
        self.concurrentLimit = newConcurrentLimit


# @package Kaltura
# @subpackage Client
class KalturaRegionalChannel(KalturaObjectBase):
    def __init__(self,
            linearChannelId=NotImplemented,
            channelNumber=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The identifier of the linear media representing the channel
        # @var int
        self.linearChannelId = linearChannelId

        # The number of the channel
        # @var int
        self.channelNumber = channelNumber


    PROPERTY_LOADERS = {
        'linearChannelId': getXmlNodeInt, 
        'channelNumber': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegionalChannel.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRegionalChannel")
        kparams.addIntIfDefined("linearChannelId", self.linearChannelId)
        kparams.addIntIfDefined("channelNumber", self.channelNumber)
        return kparams

    def getLinearChannelId(self):
        return self.linearChannelId

    def setLinearChannelId(self, newLinearChannelId):
        self.linearChannelId = newLinearChannelId

    def getChannelNumber(self):
        return self.channelNumber

    def setChannelNumber(self, newChannelNumber):
        self.channelNumber = newChannelNumber


# @package Kaltura
# @subpackage Client
class KalturaRegion(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            externalId=NotImplemented,
            isDefault=NotImplemented,
            linearChannels=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Region identifier
        # @var int
        self.id = id

        # Region name
        # @var string
        self.name = name

        # Region external identifier
        # @var string
        self.externalId = externalId

        # Indicates whether this is the default region for the partner
        # @var bool
        self.isDefault = isDefault

        # List of associated linear channels
        # @var array of KalturaRegionalChannel
        self.linearChannels = linearChannels


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'externalId': getXmlNodeText, 
        'isDefault': getXmlNodeBool, 
        'linearChannels': (KalturaObjectFactory.createArray, 'KalturaRegionalChannel'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegion.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRegion")
        kparams.addIntIfDefined("id", self.id)
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        kparams.addArrayIfDefined("linearChannels", self.linearChannels)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault

    def getLinearChannels(self):
        return self.linearChannels

    def setLinearChannels(self, newLinearChannels):
        self.linearChannels = newLinearChannels


# @package Kaltura
# @subpackage Client
class KalturaRegionListResponse(KalturaListResponse):
    """Regions list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of regions
        # @var array of KalturaRegion
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaRegion'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegionListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaRegionListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaUserAssetRule(KalturaObjectBase):
    """User asset rule - representing different type of rules on an asset(Parental, Geo, User Type, Device)"""

    def __init__(self,
            id=NotImplemented,
            ruleType=NotImplemented,
            name=NotImplemented,
            description=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique rule identifier
        # @var int
        # @readonly
        self.id = id

        # Rule type - possible values: Rule type - Parental, Geo, UserType, Device
        # @var KalturaRuleType
        self.ruleType = ruleType

        # Rule display name
        # @var string
        self.name = name

        # Additional description for the specific rule
        # @var string
        self.description = description


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'ruleType': (KalturaEnumsFactory.createString, "KalturaRuleType"), 
        'name': getXmlNodeText, 
        'description': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserAssetRule.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserAssetRule")
        kparams.addStringEnumIfDefined("ruleType", self.ruleType)
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("description", self.description)
        return kparams

    def getId(self):
        return self.id

    def getRuleType(self):
        return self.ruleType

    def setRuleType(self, newRuleType):
        self.ruleType = newRuleType

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription


# @package Kaltura
# @subpackage Client
class KalturaUserAssetRuleListResponse(KalturaListResponse):
    """GenericRules list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of generic rules
        # @var array of KalturaUserAssetRule
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaUserAssetRule'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserAssetRuleListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaUserAssetRuleListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaCDNAdapterProfile(KalturaObjectBase):
    """CDN Adapter"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isActive=NotImplemented,
            adapterUrl=NotImplemented,
            baseUrl=NotImplemented,
            settings=NotImplemented,
            systemName=NotImplemented,
            sharedSecret=NotImplemented):
        KalturaObjectBase.__init__(self)

        # CDN adapter identifier
        # @var int
        # @readonly
        self.id = id

        # CDNR adapter name
        # @var string
        self.name = name

        # CDN adapter active status
        # @var bool
        self.isActive = isActive

        # CDN adapter URL
        # @var string
        self.adapterUrl = adapterUrl

        # CDN adapter base URL
        # @var string
        self.baseUrl = baseUrl

        # CDN adapter settings
        # @var map
        self.settings = settings

        # CDN adapter alias
        # @var string
        self.systemName = systemName

        # CDN shared secret
        # @var string
        # @readonly
        self.sharedSecret = sharedSecret


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'isActive': getXmlNodeBool, 
        'adapterUrl': getXmlNodeText, 
        'baseUrl': getXmlNodeText, 
        'settings': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'systemName': getXmlNodeText, 
        'sharedSecret': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCDNAdapterProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCDNAdapterProfile")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("adapterUrl", self.adapterUrl)
        kparams.addStringIfDefined("baseUrl", self.baseUrl)
        kparams.addMapIfDefined("settings", self.settings)
        kparams.addStringIfDefined("systemName", self.systemName)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getAdapterUrl(self):
        return self.adapterUrl

    def setAdapterUrl(self, newAdapterUrl):
        self.adapterUrl = newAdapterUrl

    def getBaseUrl(self):
        return self.baseUrl

    def setBaseUrl(self, newBaseUrl):
        self.baseUrl = newBaseUrl

    def getSettings(self):
        return self.settings

    def setSettings(self, newSettings):
        self.settings = newSettings

    def getSystemName(self):
        return self.systemName

    def setSystemName(self, newSystemName):
        self.systemName = newSystemName

    def getSharedSecret(self):
        return self.sharedSecret


# @package Kaltura
# @subpackage Client
class KalturaCDNAdapterProfileListResponse(KalturaListResponse):
    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Adapters
        # @var array of KalturaCDNAdapterProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaCDNAdapterProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCDNAdapterProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaCDNAdapterProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaExportTask(KalturaObjectBase):
    """Bulk export task"""

    def __init__(self,
            id=NotImplemented,
            alias=NotImplemented,
            name=NotImplemented,
            dataType=NotImplemented,
            filter=NotImplemented,
            exportType=NotImplemented,
            frequency=NotImplemented,
            notificationUrl=NotImplemented,
            vodTypes=NotImplemented,
            isActive=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Task identifier
        # @var int
        # @readonly
        self.id = id

        # Alias for the task used to solicit an export using API
        # @var string
        self.alias = alias

        # Task display name
        # @var string
        self.name = name

        # The data type exported in this task
        # @var KalturaExportDataType
        self.dataType = dataType

        # Filter to apply on the export, utilize KSQL.
        #             Note: KSQL currently applies to media assets only. It cannot be used for USERS filtering
        # @var string
        self.filter = filter

        # Type of export batch - full or incremental
        # @var KalturaExportType
        self.exportType = exportType

        # How often the export should occur, reasonable minimum threshold should apply, configurable in minutes
        # @var int
        self.frequency = frequency

        # The URL for sending a notification when the task&#39;s export process is done
        # @var string
        self.notificationUrl = notificationUrl

        # List of media type identifiers (as configured in TVM) to export. used only in case data_type = vod
        # @var array of KalturaIntegerValue
        self.vodTypes = vodTypes

        # Indicates if the task is active or not
        # @var bool
        self.isActive = isActive


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'alias': getXmlNodeText, 
        'name': getXmlNodeText, 
        'dataType': (KalturaEnumsFactory.createString, "KalturaExportDataType"), 
        'filter': getXmlNodeText, 
        'exportType': (KalturaEnumsFactory.createString, "KalturaExportType"), 
        'frequency': getXmlNodeInt, 
        'notificationUrl': getXmlNodeText, 
        'vodTypes': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
        'isActive': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaExportTask.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaExportTask")
        kparams.addStringIfDefined("alias", self.alias)
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringEnumIfDefined("dataType", self.dataType)
        kparams.addStringIfDefined("filter", self.filter)
        kparams.addStringEnumIfDefined("exportType", self.exportType)
        kparams.addIntIfDefined("frequency", self.frequency)
        kparams.addStringIfDefined("notificationUrl", self.notificationUrl)
        kparams.addArrayIfDefined("vodTypes", self.vodTypes)
        kparams.addBoolIfDefined("isActive", self.isActive)
        return kparams

    def getId(self):
        return self.id

    def getAlias(self):
        return self.alias

    def setAlias(self, newAlias):
        self.alias = newAlias

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDataType(self):
        return self.dataType

    def setDataType(self, newDataType):
        self.dataType = newDataType

    def getFilter(self):
        return self.filter

    def setFilter(self, newFilter):
        self.filter = newFilter

    def getExportType(self):
        return self.exportType

    def setExportType(self, newExportType):
        self.exportType = newExportType

    def getFrequency(self):
        return self.frequency

    def setFrequency(self, newFrequency):
        self.frequency = newFrequency

    def getNotificationUrl(self):
        return self.notificationUrl

    def setNotificationUrl(self, newNotificationUrl):
        self.notificationUrl = newNotificationUrl

    def getVodTypes(self):
        return self.vodTypes

    def setVodTypes(self, newVodTypes):
        self.vodTypes = newVodTypes

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive


# @package Kaltura
# @subpackage Client
class KalturaExportTaskListResponse(KalturaListResponse):
    """Export task list wrapper"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Export task items
        # @var array of KalturaExportTask
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaExportTask'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaExportTaskListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaExportTaskListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaChannelEnrichmentHolder(KalturaObjectBase):
    """Holder object for channel enrichment enum"""

    def __init__(self,
            type=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Enrichment type
        # @var KalturaChannelEnrichment
        self.type = type


    PROPERTY_LOADERS = {
        'type': (KalturaEnumsFactory.createString, "KalturaChannelEnrichment"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaChannelEnrichmentHolder.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaChannelEnrichmentHolder")
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType


# @package Kaltura
# @subpackage Client
class KalturaExternalChannelProfile(KalturaObjectBase):
    """OSS Adapter"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isActive=NotImplemented,
            externalIdentifier=NotImplemented,
            filterExpression=NotImplemented,
            recommendationEngineId=NotImplemented,
            enrichments=NotImplemented):
        KalturaObjectBase.__init__(self)

        # External channel id
        # @var int
        # @readonly
        self.id = id

        # External channel name
        # @var string
        self.name = name

        # External channel active status
        # @var bool
        self.isActive = isActive

        # External channel external identifier
        # @var string
        self.externalIdentifier = externalIdentifier

        # Filter expression
        # @var string
        self.filterExpression = filterExpression

        # Recommendation engine id
        # @var int
        self.recommendationEngineId = recommendationEngineId

        # Enrichments
        # @var array of KalturaChannelEnrichmentHolder
        self.enrichments = enrichments


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'isActive': getXmlNodeBool, 
        'externalIdentifier': getXmlNodeText, 
        'filterExpression': getXmlNodeText, 
        'recommendationEngineId': getXmlNodeInt, 
        'enrichments': (KalturaObjectFactory.createArray, 'KalturaChannelEnrichmentHolder'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaExternalChannelProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaExternalChannelProfile")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("externalIdentifier", self.externalIdentifier)
        kparams.addStringIfDefined("filterExpression", self.filterExpression)
        kparams.addIntIfDefined("recommendationEngineId", self.recommendationEngineId)
        kparams.addArrayIfDefined("enrichments", self.enrichments)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getExternalIdentifier(self):
        return self.externalIdentifier

    def setExternalIdentifier(self, newExternalIdentifier):
        self.externalIdentifier = newExternalIdentifier

    def getFilterExpression(self):
        return self.filterExpression

    def setFilterExpression(self, newFilterExpression):
        self.filterExpression = newFilterExpression

    def getRecommendationEngineId(self):
        return self.recommendationEngineId

    def setRecommendationEngineId(self, newRecommendationEngineId):
        self.recommendationEngineId = newRecommendationEngineId

    def getEnrichments(self):
        return self.enrichments

    def setEnrichments(self, newEnrichments):
        self.enrichments = newEnrichments


# @package Kaltura
# @subpackage Client
class KalturaExternalChannelProfileListResponse(KalturaListResponse):
    """External channel profiles"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # External channel profiles
        # @var array of KalturaExternalChannelProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaExternalChannelProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaExternalChannelProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaExternalChannelProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaRecommendationProfile(KalturaObjectBase):
    """PaymentGW"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            isActive=NotImplemented,
            adapterUrl=NotImplemented,
            recommendationEngineSettings=NotImplemented,
            externalIdentifier=NotImplemented,
            sharedSecret=NotImplemented):
        KalturaObjectBase.__init__(self)

        # recommendation engine id
        # @var int
        # @readonly
        self.id = id

        # recommendation engine name
        # @var string
        self.name = name

        # recommendation engine is active status
        # @var bool
        self.isActive = isActive

        # recommendation engine adapter URL
        # @var string
        self.adapterUrl = adapterUrl

        # recommendation engine extra parameters
        # @var map
        self.recommendationEngineSettings = recommendationEngineSettings

        # recommendation engine external identifier
        # @var string
        self.externalIdentifier = externalIdentifier

        # Shared Secret
        # @var string
        # @readonly
        self.sharedSecret = sharedSecret


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'isActive': getXmlNodeBool, 
        'adapterUrl': getXmlNodeText, 
        'recommendationEngineSettings': (KalturaObjectFactory.createMap, 'KalturaStringValue'), 
        'externalIdentifier': getXmlNodeText, 
        'sharedSecret': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecommendationProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRecommendationProfile")
        kparams.addStringIfDefined("name", self.name)
        kparams.addBoolIfDefined("isActive", self.isActive)
        kparams.addStringIfDefined("adapterUrl", self.adapterUrl)
        kparams.addMapIfDefined("recommendationEngineSettings", self.recommendationEngineSettings)
        kparams.addStringIfDefined("externalIdentifier", self.externalIdentifier)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getIsActive(self):
        return self.isActive

    def setIsActive(self, newIsActive):
        self.isActive = newIsActive

    def getAdapterUrl(self):
        return self.adapterUrl

    def setAdapterUrl(self, newAdapterUrl):
        self.adapterUrl = newAdapterUrl

    def getRecommendationEngineSettings(self):
        return self.recommendationEngineSettings

    def setRecommendationEngineSettings(self, newRecommendationEngineSettings):
        self.recommendationEngineSettings = newRecommendationEngineSettings

    def getExternalIdentifier(self):
        return self.externalIdentifier

    def setExternalIdentifier(self, newExternalIdentifier):
        self.externalIdentifier = newExternalIdentifier

    def getSharedSecret(self):
        return self.sharedSecret


# @package Kaltura
# @subpackage Client
class KalturaRecommendationProfileListResponse(KalturaListResponse):
    """List of recommendation profiles."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Recommendation profiles list
        # @var array of KalturaRecommendationProfile
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaRecommendationProfile'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecommendationProfileListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaRecommendationProfileListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaRegistrySettings(KalturaObjectBase):
    def __init__(self,
            key=NotImplemented,
            value=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Permission item identifier
        # @var string
        self.key = key

        # Permission item name
        # @var string
        self.value = value


    PROPERTY_LOADERS = {
        'key': getXmlNodeText, 
        'value': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegistrySettings.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRegistrySettings")
        kparams.addStringIfDefined("key", self.key)
        kparams.addStringIfDefined("value", self.value)
        return kparams

    def getKey(self):
        return self.key

    def setKey(self, newKey):
        self.key = newKey

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaRegistrySettingsListResponse(KalturaListResponse):
    """List of registry settings."""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # Registry settings list
        # @var array of KalturaRegistrySettings
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaRegistrySettings'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegistrySettingsListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaRegistrySettingsListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaParentalRule(KalturaObjectBase):
    """Parental rule"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            description=NotImplemented,
            order=NotImplemented,
            mediaTag=NotImplemented,
            epgTag=NotImplemented,
            blockAnonymousAccess=NotImplemented,
            ruleType=NotImplemented,
            mediaTagValues=NotImplemented,
            epgTagValues=NotImplemented,
            isDefault=NotImplemented,
            origin=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique parental rule identifier
        # @var int
        # @readonly
        self.id = id

        # Rule display name
        # @var string
        self.name = name

        # Explanatory description
        # @var string
        self.description = description

        # Rule order within the full list of rules
        # @var int
        self.order = order

        # Media asset tag ID to in which to look for corresponding trigger values
        # @var int
        self.mediaTag = mediaTag

        # EPG asset tag ID to in which to look for corresponding trigger values
        # @var int
        self.epgTag = epgTag

        # Content that correspond to this rule is not available for guests
        # @var bool
        self.blockAnonymousAccess = blockAnonymousAccess

        # Rule type - Movies, TV series or both
        # @var KalturaParentalRuleType
        self.ruleType = ruleType

        # Media tag values that trigger rule
        # @var array of KalturaStringValue
        self.mediaTagValues = mediaTagValues

        # EPG tag values that trigger rule
        # @var array of KalturaStringValue
        self.epgTagValues = epgTagValues

        # Is the rule the default rule of the account
        # @var bool
        self.isDefault = isDefault

        # Where was this rule defined account, household or user
        # @var KalturaRuleLevel
        self.origin = origin


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'description': getXmlNodeText, 
        'order': getXmlNodeInt, 
        'mediaTag': getXmlNodeInt, 
        'epgTag': getXmlNodeInt, 
        'blockAnonymousAccess': getXmlNodeBool, 
        'ruleType': (KalturaEnumsFactory.createString, "KalturaParentalRuleType"), 
        'mediaTagValues': (KalturaObjectFactory.createArray, 'KalturaStringValue'), 
        'epgTagValues': (KalturaObjectFactory.createArray, 'KalturaStringValue'), 
        'isDefault': getXmlNodeBool, 
        'origin': (KalturaEnumsFactory.createString, "KalturaRuleLevel"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaParentalRule.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaParentalRule")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("description", self.description)
        kparams.addIntIfDefined("order", self.order)
        kparams.addIntIfDefined("mediaTag", self.mediaTag)
        kparams.addIntIfDefined("epgTag", self.epgTag)
        kparams.addBoolIfDefined("blockAnonymousAccess", self.blockAnonymousAccess)
        kparams.addStringEnumIfDefined("ruleType", self.ruleType)
        kparams.addArrayIfDefined("mediaTagValues", self.mediaTagValues)
        kparams.addArrayIfDefined("epgTagValues", self.epgTagValues)
        kparams.addBoolIfDefined("isDefault", self.isDefault)
        kparams.addStringEnumIfDefined("origin", self.origin)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription

    def getOrder(self):
        return self.order

    def setOrder(self, newOrder):
        self.order = newOrder

    def getMediaTag(self):
        return self.mediaTag

    def setMediaTag(self, newMediaTag):
        self.mediaTag = newMediaTag

    def getEpgTag(self):
        return self.epgTag

    def setEpgTag(self, newEpgTag):
        self.epgTag = newEpgTag

    def getBlockAnonymousAccess(self):
        return self.blockAnonymousAccess

    def setBlockAnonymousAccess(self, newBlockAnonymousAccess):
        self.blockAnonymousAccess = newBlockAnonymousAccess

    def getRuleType(self):
        return self.ruleType

    def setRuleType(self, newRuleType):
        self.ruleType = newRuleType

    def getMediaTagValues(self):
        return self.mediaTagValues

    def setMediaTagValues(self, newMediaTagValues):
        self.mediaTagValues = newMediaTagValues

    def getEpgTagValues(self):
        return self.epgTagValues

    def setEpgTagValues(self, newEpgTagValues):
        self.epgTagValues = newEpgTagValues

    def getIsDefault(self):
        return self.isDefault

    def setIsDefault(self, newIsDefault):
        self.isDefault = newIsDefault

    def getOrigin(self):
        return self.origin

    def setOrigin(self, newOrigin):
        self.origin = newOrigin


# @package Kaltura
# @subpackage Client
class KalturaParentalRuleListResponse(KalturaListResponse):
    """ParentalRules list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of parental rules
        # @var array of KalturaParentalRule
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaParentalRule'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaParentalRuleListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaParentalRuleListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaUserRole(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            permissionNames=NotImplemented,
            excludedPermissionNames=NotImplemented):
        KalturaObjectBase.__init__(self)

        # User role identifier
        # @var int
        # @readonly
        self.id = id

        # User role name
        # @var string
        self.name = name

        # permissions associated with the user role
        # @var string
        self.permissionNames = permissionNames

        # permissions associated with the user role in is_exclueded = true
        # @var string
        self.excludedPermissionNames = excludedPermissionNames


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'permissionNames': getXmlNodeText, 
        'excludedPermissionNames': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserRole.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserRole")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("permissionNames", self.permissionNames)
        kparams.addStringIfDefined("excludedPermissionNames", self.excludedPermissionNames)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getPermissionNames(self):
        return self.permissionNames

    def setPermissionNames(self, newPermissionNames):
        self.permissionNames = newPermissionNames

    def getExcludedPermissionNames(self):
        return self.excludedPermissionNames

    def setExcludedPermissionNames(self, newExcludedPermissionNames):
        self.excludedPermissionNames = newExcludedPermissionNames


# @package Kaltura
# @subpackage Client
class KalturaUserRoleListResponse(KalturaListResponse):
    """User-roles list"""

    def __init__(self,
            totalCount=NotImplemented,
            objects=NotImplemented):
        KalturaListResponse.__init__(self,
            totalCount)

        # A list of generic rules
        # @var array of KalturaUserRole
        self.objects = objects


    PROPERTY_LOADERS = {
        'objects': (KalturaObjectFactory.createArray, 'KalturaUserRole'), 
    }

    def fromXml(self, node):
        KalturaListResponse.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserRoleListResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaListResponse.toParams(self)
        kparams.put("objectType", "KalturaUserRoleListResponse")
        kparams.addArrayIfDefined("objects", self.objects)
        return kparams

    def getObjects(self):
        return self.objects

    def setObjects(self, newObjects):
        self.objects = newObjects


# @package Kaltura
# @subpackage Client
class KalturaClientConfiguration(KalturaObjectBase):
    """Define client optional configurations"""

    def __init__(self,
            clientTag=NotImplemented,
            apiVersion=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Client Tag
        # @var string
        self.clientTag = clientTag

        # API client version
        # @var string
        self.apiVersion = apiVersion


    PROPERTY_LOADERS = {
        'clientTag': getXmlNodeText, 
        'apiVersion': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaClientConfiguration.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaClientConfiguration")
        kparams.addStringIfDefined("clientTag", self.clientTag)
        kparams.addStringIfDefined("apiVersion", self.apiVersion)
        return kparams

    def getClientTag(self):
        return self.clientTag

    def setClientTag(self, newClientTag):
        self.clientTag = newClientTag

    def getApiVersion(self):
        return self.apiVersion

    def setApiVersion(self, newApiVersion):
        self.apiVersion = newApiVersion


# @package Kaltura
# @subpackage Client
class KalturaBaseResponseProfile(KalturaObjectBase):
    """Define base profile response -  optional configurations"""

    def __init__(self):
        KalturaObjectBase.__init__(self)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBaseResponseProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaBaseResponseProfile")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaRequestConfiguration(KalturaObjectBase):
    """Define client request optional configurations"""

    def __init__(self,
            partnerId=NotImplemented,
            userId=NotImplemented,
            language=NotImplemented,
            currency=NotImplemented,
            ks=NotImplemented,
            responseProfile=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Impersonated partner id
        # @var int
        self.partnerId = partnerId

        # Impersonated user id
        # @var int
        self.userId = userId

        # Content language
        # @var string
        self.language = language

        # Currency to be used
        # @var string
        self.currency = currency

        # Kaltura API session
        # @var string
        self.ks = ks

        # Kaltura response profile object
        # @var KalturaBaseResponseProfile
        self.responseProfile = responseProfile


    PROPERTY_LOADERS = {
        'partnerId': getXmlNodeInt, 
        'userId': getXmlNodeInt, 
        'language': getXmlNodeText, 
        'currency': getXmlNodeText, 
        'ks': getXmlNodeText, 
        'responseProfile': (KalturaObjectFactory.create, 'KalturaBaseResponseProfile'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRequestConfiguration.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRequestConfiguration")
        kparams.addIntIfDefined("partnerId", self.partnerId)
        kparams.addIntIfDefined("userId", self.userId)
        kparams.addStringIfDefined("language", self.language)
        kparams.addStringIfDefined("currency", self.currency)
        kparams.addStringIfDefined("ks", self.ks)
        kparams.addObjectIfDefined("responseProfile", self.responseProfile)
        return kparams

    def getPartnerId(self):
        return self.partnerId

    def setPartnerId(self, newPartnerId):
        self.partnerId = newPartnerId

    def getUserId(self):
        return self.userId

    def setUserId(self, newUserId):
        self.userId = newUserId

    def getLanguage(self):
        return self.language

    def setLanguage(self, newLanguage):
        self.language = newLanguage

    def getCurrency(self):
        return self.currency

    def setCurrency(self, newCurrency):
        self.currency = newCurrency

    def getKs(self):
        return self.ks

    def setKs(self, newKs):
        self.ks = newKs

    def getResponseProfile(self):
        return self.responseProfile

    def setResponseProfile(self, newResponseProfile):
        self.responseProfile = newResponseProfile


# @package Kaltura
# @subpackage Client
class KalturaFilter(KalturaObjectBase):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaObjectBase.__init__(self)

        # order by
        # @var string
        self.orderBy = orderBy


    PROPERTY_LOADERS = {
        'orderBy': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaFilter")
        kparams.addStringIfDefined("orderBy", self.orderBy)
        return kparams

    def getOrderBy(self):
        return self.orderBy

    def setOrderBy(self, newOrderBy):
        self.orderBy = newOrderBy


# @package Kaltura
# @subpackage Client
class KalturaDetachedResponseProfile(KalturaBaseResponseProfile):
    """Define specific base profile response"""

    def __init__(self,
            name=NotImplemented,
            filter=NotImplemented,
            relatedProfiles=NotImplemented):
        KalturaBaseResponseProfile.__init__(self)

        # name
        # @var string
        self.name = name

        # filter
        # @var KalturaRelatedObjectFilter
        self.filter = filter

        # relatedProfiles
        # @var array of KalturaDetachedResponseProfile
        self.relatedProfiles = relatedProfiles


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'filter': (KalturaObjectFactory.create, 'KalturaRelatedObjectFilter'), 
        'relatedProfiles': (KalturaObjectFactory.createArray, 'KalturaObjectBase'), 
    }

    def fromXml(self, node):
        KalturaBaseResponseProfile.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDetachedResponseProfile.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaBaseResponseProfile.toParams(self)
        kparams.put("objectType", "KalturaDetachedResponseProfile")
        kparams.addStringIfDefined("name", self.name)
        kparams.addObjectIfDefined("filter", self.filter)
        kparams.addArrayIfDefined("relatedProfiles", self.relatedProfiles)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getFilter(self):
        return self.filter

    def setFilter(self, newFilter):
        self.filter = newFilter

    def getRelatedProfiles(self):
        return self.relatedProfiles

    def setRelatedProfiles(self, newRelatedProfiles):
        self.relatedProfiles = newRelatedProfiles


# @package Kaltura
# @subpackage Client
class KalturaRelatedObjectFilter(KalturaFilter):
    """Define KalturaRelatedObjectFilter"""

    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRelatedObjectFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaRelatedObjectFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaSocialCommentFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            assetIdEqual=NotImplemented,
            assetTypeEqual=NotImplemented,
            socialPlatformEqual=NotImplemented,
            createDateGreaterThan=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Asset ID to filter by
        # @var int
        self.assetIdEqual = assetIdEqual

        # Asset type to filter by, currently only VOD (media)
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual

        # Comma separated list of social actions to filter by
        # @var KalturaSocialPlatform
        self.socialPlatformEqual = socialPlatformEqual

        # The create date from which to get the comments
        # @var int
        self.createDateGreaterThan = createDateGreaterThan


    PROPERTY_LOADERS = {
        'assetIdEqual': getXmlNodeInt, 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'socialPlatformEqual': (KalturaEnumsFactory.createString, "KalturaSocialPlatform"), 
        'createDateGreaterThan': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialCommentFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSocialCommentFilter")
        kparams.addIntIfDefined("assetIdEqual", self.assetIdEqual)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        kparams.addStringEnumIfDefined("socialPlatformEqual", self.socialPlatformEqual)
        kparams.addIntIfDefined("createDateGreaterThan", self.createDateGreaterThan)
        return kparams

    def getAssetIdEqual(self):
        return self.assetIdEqual

    def setAssetIdEqual(self, newAssetIdEqual):
        self.assetIdEqual = newAssetIdEqual

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual

    def getSocialPlatformEqual(self):
        return self.socialPlatformEqual

    def setSocialPlatformEqual(self, newSocialPlatformEqual):
        self.socialPlatformEqual = newSocialPlatformEqual

    def getCreateDateGreaterThan(self):
        return self.createDateGreaterThan

    def setCreateDateGreaterThan(self, newCreateDateGreaterThan):
        self.createDateGreaterThan = newCreateDateGreaterThan


# @package Kaltura
# @subpackage Client
class KalturaSocialFriendActivityFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            assetIdEqual=NotImplemented,
            assetTypeEqual=NotImplemented,
            actionTypeIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Asset ID to filter by
        # @var int
        self.assetIdEqual = assetIdEqual

        # Asset type to filter by, currently only VOD (media)
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual

        # Comma separated list of social actions to filter by
        # @var string
        self.actionTypeIn = actionTypeIn


    PROPERTY_LOADERS = {
        'assetIdEqual': getXmlNodeInt, 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'actionTypeIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialFriendActivityFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSocialFriendActivityFilter")
        kparams.addIntIfDefined("assetIdEqual", self.assetIdEqual)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        kparams.addStringIfDefined("actionTypeIn", self.actionTypeIn)
        return kparams

    def getAssetIdEqual(self):
        return self.assetIdEqual

    def setAssetIdEqual(self, newAssetIdEqual):
        self.assetIdEqual = newAssetIdEqual

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual

    def getActionTypeIn(self):
        return self.actionTypeIn

    def setActionTypeIn(self, newActionTypeIn):
        self.actionTypeIn = newActionTypeIn


# @package Kaltura
# @subpackage Client
class KalturaSocialActionFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            assetIdIn=NotImplemented,
            assetTypeEqual=NotImplemented,
            actionTypeIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated list of asset identifiers.
        # @var string
        self.assetIdIn = assetIdIn

        # Asset Type
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual

        # Comma separated list of social actions to filter by
        # @var string
        self.actionTypeIn = actionTypeIn


    PROPERTY_LOADERS = {
        'assetIdIn': getXmlNodeText, 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'actionTypeIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialActionFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSocialActionFilter")
        kparams.addStringIfDefined("assetIdIn", self.assetIdIn)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        kparams.addStringIfDefined("actionTypeIn", self.actionTypeIn)
        return kparams

    def getAssetIdIn(self):
        return self.assetIdIn

    def setAssetIdIn(self, newAssetIdIn):
        self.assetIdIn = newAssetIdIn

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual

    def getActionTypeIn(self):
        return self.actionTypeIn

    def setActionTypeIn(self, newActionTypeIn):
        self.actionTypeIn = newActionTypeIn


# @package Kaltura
# @subpackage Client
class KalturaPaymentMethodProfileFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            paymentGatewayIdEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Payment gateway identifier to list the payment methods for
        # @var int
        self.paymentGatewayIdEqual = paymentGatewayIdEqual


    PROPERTY_LOADERS = {
        'paymentGatewayIdEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentMethodProfileFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaPaymentMethodProfileFilter")
        kparams.addIntIfDefined("paymentGatewayIdEqual", self.paymentGatewayIdEqual)
        return kparams

    def getPaymentGatewayIdEqual(self):
        return self.paymentGatewayIdEqual

    def setPaymentGatewayIdEqual(self, newPaymentGatewayIdEqual):
        self.paymentGatewayIdEqual = newPaymentGatewayIdEqual


# @package Kaltura
# @subpackage Client
class KalturaHouseholdDeviceFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            householdIdEqual=NotImplemented,
            deviceFamilyIdIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # The identifier of the household
        # @var int
        self.householdIdEqual = householdIdEqual

        # Device family Ids
        # @var string
        self.deviceFamilyIdIn = deviceFamilyIdIn


    PROPERTY_LOADERS = {
        'householdIdEqual': getXmlNodeInt, 
        'deviceFamilyIdIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdDeviceFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaHouseholdDeviceFilter")
        kparams.addIntIfDefined("householdIdEqual", self.householdIdEqual)
        kparams.addStringIfDefined("deviceFamilyIdIn", self.deviceFamilyIdIn)
        return kparams

    def getHouseholdIdEqual(self):
        return self.householdIdEqual

    def setHouseholdIdEqual(self, newHouseholdIdEqual):
        self.householdIdEqual = newHouseholdIdEqual

    def getDeviceFamilyIdIn(self):
        return self.deviceFamilyIdIn

    def setDeviceFamilyIdIn(self, newDeviceFamilyIdIn):
        self.deviceFamilyIdIn = newDeviceFamilyIdIn


# @package Kaltura
# @subpackage Client
class KalturaHouseholdUserFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            householdIdEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # The identifier of the household
        # @var int
        self.householdIdEqual = householdIdEqual


    PROPERTY_LOADERS = {
        'householdIdEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdUserFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaHouseholdUserFilter")
        kparams.addIntIfDefined("householdIdEqual", self.householdIdEqual)
        return kparams

    def getHouseholdIdEqual(self):
        return self.householdIdEqual

    def setHouseholdIdEqual(self, newHouseholdIdEqual):
        self.householdIdEqual = newHouseholdIdEqual


# @package Kaltura
# @subpackage Client
class KalturaConfigurationsFilter(KalturaFilter):
    """Configuration filter"""

    def __init__(self,
            orderBy=NotImplemented,
            configurationGroupIdEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # the ID of the configuration group for which to return related configurations
        # @var string
        self.configurationGroupIdEqual = configurationGroupIdEqual


    PROPERTY_LOADERS = {
        'configurationGroupIdEqual': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationsFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaConfigurationsFilter")
        kparams.addStringIfDefined("configurationGroupIdEqual", self.configurationGroupIdEqual)
        return kparams

    def getConfigurationGroupIdEqual(self):
        return self.configurationGroupIdEqual

    def setConfigurationGroupIdEqual(self, newConfigurationGroupIdEqual):
        self.configurationGroupIdEqual = newConfigurationGroupIdEqual


# @package Kaltura
# @subpackage Client
class KalturaReportFilter(KalturaFilter):
    """Report filter"""

    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaReportFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaReportFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaDeviceReportFilter(KalturaReportFilter):
    """Report filter"""

    def __init__(self,
            orderBy=NotImplemented,
            lastAccessDateGreaterThanOrEqual=NotImplemented):
        KalturaReportFilter.__init__(self,
            orderBy)

        # Filter device configuration later than specific date
        # @var int
        self.lastAccessDateGreaterThanOrEqual = lastAccessDateGreaterThanOrEqual


    PROPERTY_LOADERS = {
        'lastAccessDateGreaterThanOrEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaReportFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDeviceReportFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReportFilter.toParams(self)
        kparams.put("objectType", "KalturaDeviceReportFilter")
        kparams.addIntIfDefined("lastAccessDateGreaterThanOrEqual", self.lastAccessDateGreaterThanOrEqual)
        return kparams

    def getLastAccessDateGreaterThanOrEqual(self):
        return self.lastAccessDateGreaterThanOrEqual

    def setLastAccessDateGreaterThanOrEqual(self, newLastAccessDateGreaterThanOrEqual):
        self.lastAccessDateGreaterThanOrEqual = newLastAccessDateGreaterThanOrEqual


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupTagFilter(KalturaFilter):
    """Configuration group tag filter"""

    def __init__(self,
            orderBy=NotImplemented,
            configurationGroupIdEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # the ID of the configuration group for which to return related configurations group tags
        # @var string
        self.configurationGroupIdEqual = configurationGroupIdEqual


    PROPERTY_LOADERS = {
        'configurationGroupIdEqual': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupTagFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupTagFilter")
        kparams.addStringIfDefined("configurationGroupIdEqual", self.configurationGroupIdEqual)
        return kparams

    def getConfigurationGroupIdEqual(self):
        return self.configurationGroupIdEqual

    def setConfigurationGroupIdEqual(self, newConfigurationGroupIdEqual):
        self.configurationGroupIdEqual = newConfigurationGroupIdEqual


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupDeviceFilter(KalturaFilter):
    """Configuration group device filter"""

    def __init__(self,
            orderBy=NotImplemented,
            configurationGroupIdEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # the ID of the configuration group for which to return related configurations group devices
        # @var string
        self.configurationGroupIdEqual = configurationGroupIdEqual


    PROPERTY_LOADERS = {
        'configurationGroupIdEqual': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaConfigurationGroupDeviceFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaConfigurationGroupDeviceFilter")
        kparams.addStringIfDefined("configurationGroupIdEqual", self.configurationGroupIdEqual)
        return kparams

    def getConfigurationGroupIdEqual(self):
        return self.configurationGroupIdEqual

    def setConfigurationGroupIdEqual(self, newConfigurationGroupIdEqual):
        self.configurationGroupIdEqual = newConfigurationGroupIdEqual


# @package Kaltura
# @subpackage Client
class KalturaFavoriteFilter(KalturaFilter):
    """Favorite request filter"""

    def __init__(self,
            orderBy=NotImplemented,
            mediaTypeEqual=NotImplemented,
            mediaIdIn=NotImplemented,
            udidEqualCurrent=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Media type to filter by the favorite assets
        # @var int
        self.mediaTypeEqual = mediaTypeEqual

        # Media identifiers from which to filter the favorite assets
        # @var string
        self.mediaIdIn = mediaIdIn

        # Indicates whether the results should be filtered by origin UDID using the current
        # @var bool
        self.udidEqualCurrent = udidEqualCurrent


    PROPERTY_LOADERS = {
        'mediaTypeEqual': getXmlNodeInt, 
        'mediaIdIn': getXmlNodeText, 
        'udidEqualCurrent': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFavoriteFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaFavoriteFilter")
        kparams.addIntIfDefined("mediaTypeEqual", self.mediaTypeEqual)
        kparams.addStringIfDefined("mediaIdIn", self.mediaIdIn)
        kparams.addBoolIfDefined("udidEqualCurrent", self.udidEqualCurrent)
        return kparams

    def getMediaTypeEqual(self):
        return self.mediaTypeEqual

    def setMediaTypeEqual(self, newMediaTypeEqual):
        self.mediaTypeEqual = newMediaTypeEqual

    def getMediaIdIn(self):
        return self.mediaIdIn

    def setMediaIdIn(self, newMediaIdIn):
        self.mediaIdIn = newMediaIdIn

    def getUdidEqualCurrent(self):
        return self.udidEqualCurrent

    def setUdidEqualCurrent(self, newUdidEqualCurrent):
        self.udidEqualCurrent = newUdidEqualCurrent


# @package Kaltura
# @subpackage Client
class KalturaOTTUserFilter(KalturaFilter):
    """OTT User filter"""

    def __init__(self,
            orderBy=NotImplemented,
            usernameEqual=NotImplemented,
            externalIdEqual=NotImplemented,
            idIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Username
        # @var string
        self.usernameEqual = usernameEqual

        # User external identifier
        # @var string
        self.externalIdEqual = externalIdEqual

        # List of user identifiers separated by &#39;,&#39;
        # @var string
        self.idIn = idIn


    PROPERTY_LOADERS = {
        'usernameEqual': getXmlNodeText, 
        'externalIdEqual': getXmlNodeText, 
        'idIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOTTUserFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaOTTUserFilter")
        kparams.addStringIfDefined("usernameEqual", self.usernameEqual)
        kparams.addStringIfDefined("externalIdEqual", self.externalIdEqual)
        kparams.addStringIfDefined("idIn", self.idIn)
        return kparams

    def getUsernameEqual(self):
        return self.usernameEqual

    def setUsernameEqual(self, newUsernameEqual):
        self.usernameEqual = newUsernameEqual

    def getExternalIdEqual(self):
        return self.externalIdEqual

    def setExternalIdEqual(self, newExternalIdEqual):
        self.externalIdEqual = newExternalIdEqual

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn


# @package Kaltura
# @subpackage Client
class KalturaCollectionFilter(KalturaFilter):
    """Collection Filter"""

    def __init__(self,
            orderBy=NotImplemented,
            collectionIdIn=NotImplemented,
            mediaFileIdEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated collection IDs
        # @var string
        self.collectionIdIn = collectionIdIn

        # Media-file ID to get the subscriptions by
        # @var int
        self.mediaFileIdEqual = mediaFileIdEqual


    PROPERTY_LOADERS = {
        'collectionIdIn': getXmlNodeText, 
        'mediaFileIdEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCollectionFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaCollectionFilter")
        kparams.addStringIfDefined("collectionIdIn", self.collectionIdIn)
        kparams.addIntIfDefined("mediaFileIdEqual", self.mediaFileIdEqual)
        return kparams

    def getCollectionIdIn(self):
        return self.collectionIdIn

    def setCollectionIdIn(self, newCollectionIdIn):
        self.collectionIdIn = newCollectionIdIn

    def getMediaFileIdEqual(self):
        return self.mediaFileIdEqual

    def setMediaFileIdEqual(self, newMediaFileIdEqual):
        self.mediaFileIdEqual = newMediaFileIdEqual


# @package Kaltura
# @subpackage Client
class KalturaPricePlanFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated price plans identifiers
        # @var string
        self.idIn = idIn


    PROPERTY_LOADERS = {
        'idIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPricePlanFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaPricePlanFilter")
        kparams.addStringIfDefined("idIn", self.idIn)
        return kparams

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn


# @package Kaltura
# @subpackage Client
class KalturaPriceDetailsFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated price identifiers
        # @var string
        self.idIn = idIn


    PROPERTY_LOADERS = {
        'idIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPriceDetailsFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaPriceDetailsFilter")
        kparams.addStringIfDefined("idIn", self.idIn)
        return kparams

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSetFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented,
            subscriptionIdContains=NotImplemented,
            typeEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated identifiers
        # @var string
        self.idIn = idIn

        # Comma separated subscription identifiers
        # @var string
        self.subscriptionIdContains = subscriptionIdContains

        # Subscription Type
        # @var KalturaSubscriptionSetType
        self.typeEqual = typeEqual


    PROPERTY_LOADERS = {
        'idIn': getXmlNodeText, 
        'subscriptionIdContains': getXmlNodeText, 
        'typeEqual': (KalturaEnumsFactory.createString, "KalturaSubscriptionSetType"), 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionSetFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionSetFilter")
        kparams.addStringIfDefined("idIn", self.idIn)
        kparams.addStringIfDefined("subscriptionIdContains", self.subscriptionIdContains)
        kparams.addStringEnumIfDefined("typeEqual", self.typeEqual)
        return kparams

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn

    def getSubscriptionIdContains(self):
        return self.subscriptionIdContains

    def setSubscriptionIdContains(self, newSubscriptionIdContains):
        self.subscriptionIdContains = newSubscriptionIdContains

    def getTypeEqual(self):
        return self.typeEqual

    def setTypeEqual(self, newTypeEqual):
        self.typeEqual = newTypeEqual


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionDependencySetFilter(KalturaSubscriptionSetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented,
            subscriptionIdContains=NotImplemented,
            typeEqual=NotImplemented,
            baseSubscriptionIdIn=NotImplemented):
        KalturaSubscriptionSetFilter.__init__(self,
            orderBy,
            idIn,
            subscriptionIdContains,
            typeEqual)

        # Comma separated identifiers
        # @var string
        self.baseSubscriptionIdIn = baseSubscriptionIdIn


    PROPERTY_LOADERS = {
        'baseSubscriptionIdIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaSubscriptionSetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionDependencySetFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSubscriptionSetFilter.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionDependencySetFilter")
        kparams.addStringIfDefined("baseSubscriptionIdIn", self.baseSubscriptionIdIn)
        return kparams

    def getBaseSubscriptionIdIn(self):
        return self.baseSubscriptionIdIn

    def setBaseSubscriptionIdIn(self, newBaseSubscriptionIdIn):
        self.baseSubscriptionIdIn = newBaseSubscriptionIdIn


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            subscriptionIdIn=NotImplemented,
            mediaFileIdEqual=NotImplemented,
            externalIdIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated subscription IDs to get the subscriptions by
        # @var string
        self.subscriptionIdIn = subscriptionIdIn

        # Media-file ID to get the subscriptions by
        # @var int
        self.mediaFileIdEqual = mediaFileIdEqual

        # Comma separated subscription external IDs to get the subscriptions by
        # @var string
        self.externalIdIn = externalIdIn


    PROPERTY_LOADERS = {
        'subscriptionIdIn': getXmlNodeText, 
        'mediaFileIdEqual': getXmlNodeInt, 
        'externalIdIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSubscriptionFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSubscriptionFilter")
        kparams.addStringIfDefined("subscriptionIdIn", self.subscriptionIdIn)
        kparams.addIntIfDefined("mediaFileIdEqual", self.mediaFileIdEqual)
        kparams.addStringIfDefined("externalIdIn", self.externalIdIn)
        return kparams

    def getSubscriptionIdIn(self):
        return self.subscriptionIdIn

    def setSubscriptionIdIn(self, newSubscriptionIdIn):
        self.subscriptionIdIn = newSubscriptionIdIn

    def getMediaFileIdEqual(self):
        return self.mediaFileIdEqual

    def setMediaFileIdEqual(self, newMediaFileIdEqual):
        self.mediaFileIdEqual = newMediaFileIdEqual

    def getExternalIdIn(self):
        return self.externalIdIn

    def setExternalIdIn(self, newExternalIdIn):
        self.externalIdIn = newExternalIdIn


# @package Kaltura
# @subpackage Client
class KalturaEngagementFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            typeIn=NotImplemented,
            sendTimeGreaterThanOrEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # List of inbox message types to search within.
        # @var string
        self.typeIn = typeIn

        # SendTime GreaterThanOrEqual
        # @var int
        self.sendTimeGreaterThanOrEqual = sendTimeGreaterThanOrEqual


    PROPERTY_LOADERS = {
        'typeIn': getXmlNodeText, 
        'sendTimeGreaterThanOrEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEngagementFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaEngagementFilter")
        kparams.addStringIfDefined("typeIn", self.typeIn)
        kparams.addIntIfDefined("sendTimeGreaterThanOrEqual", self.sendTimeGreaterThanOrEqual)
        return kparams

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn

    def getSendTimeGreaterThanOrEqual(self):
        return self.sendTimeGreaterThanOrEqual

    def setSendTimeGreaterThanOrEqual(self, newSendTimeGreaterThanOrEqual):
        self.sendTimeGreaterThanOrEqual = newSendTimeGreaterThanOrEqual


# @package Kaltura
# @subpackage Client
class KalturaReminderFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaReminderFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaReminderFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaAssetReminderFilter(KalturaReminderFilter):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaReminderFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaReminderFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetReminderFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReminderFilter.toParams(self)
        kparams.put("objectType", "KalturaAssetReminderFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaSeriesReminderFilter(KalturaReminderFilter):
    def __init__(self,
            orderBy=NotImplemented,
            seriesIdIn=NotImplemented,
            epgChannelIdEqual=NotImplemented):
        KalturaReminderFilter.__init__(self,
            orderBy)

        # Comma separated series IDs
        # @var string
        self.seriesIdIn = seriesIdIn

        # EPG channel ID
        # @var int
        self.epgChannelIdEqual = epgChannelIdEqual


    PROPERTY_LOADERS = {
        'seriesIdIn': getXmlNodeText, 
        'epgChannelIdEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaReminderFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSeriesReminderFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReminderFilter.toParams(self)
        kparams.put("objectType", "KalturaSeriesReminderFilter")
        kparams.addStringIfDefined("seriesIdIn", self.seriesIdIn)
        kparams.addIntIfDefined("epgChannelIdEqual", self.epgChannelIdEqual)
        return kparams

    def getSeriesIdIn(self):
        return self.seriesIdIn

    def setSeriesIdIn(self, newSeriesIdIn):
        self.seriesIdIn = newSeriesIdIn

    def getEpgChannelIdEqual(self):
        return self.epgChannelIdEqual

    def setEpgChannelIdEqual(self, newEpgChannelIdEqual):
        self.epgChannelIdEqual = newEpgChannelIdEqual


# @package Kaltura
# @subpackage Client
class KalturaSeasonsReminderFilter(KalturaReminderFilter):
    def __init__(self,
            orderBy=NotImplemented,
            seriesIdEqual=NotImplemented,
            seasonNumberIn=NotImplemented,
            epgChannelIdEqual=NotImplemented):
        KalturaReminderFilter.__init__(self,
            orderBy)

        # Series ID
        # @var string
        self.seriesIdEqual = seriesIdEqual

        # Comma separated season numbers
        # @var string
        self.seasonNumberIn = seasonNumberIn

        # EPG channel ID
        # @var int
        self.epgChannelIdEqual = epgChannelIdEqual


    PROPERTY_LOADERS = {
        'seriesIdEqual': getXmlNodeText, 
        'seasonNumberIn': getXmlNodeText, 
        'epgChannelIdEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaReminderFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSeasonsReminderFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaReminderFilter.toParams(self)
        kparams.put("objectType", "KalturaSeasonsReminderFilter")
        kparams.addStringIfDefined("seriesIdEqual", self.seriesIdEqual)
        kparams.addStringIfDefined("seasonNumberIn", self.seasonNumberIn)
        kparams.addIntIfDefined("epgChannelIdEqual", self.epgChannelIdEqual)
        return kparams

    def getSeriesIdEqual(self):
        return self.seriesIdEqual

    def setSeriesIdEqual(self, newSeriesIdEqual):
        self.seriesIdEqual = newSeriesIdEqual

    def getSeasonNumberIn(self):
        return self.seasonNumberIn

    def setSeasonNumberIn(self, newSeasonNumberIn):
        self.seasonNumberIn = newSeasonNumberIn

    def getEpgChannelIdEqual(self):
        return self.epgChannelIdEqual

    def setEpgChannelIdEqual(self, newEpgChannelIdEqual):
        self.epgChannelIdEqual = newEpgChannelIdEqual


# @package Kaltura
# @subpackage Client
class KalturaFollowTvSeriesFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFollowTvSeriesFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaFollowTvSeriesFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaInboxMessageFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            typeIn=NotImplemented,
            createdAtGreaterThanOrEqual=NotImplemented,
            createdAtLessThanOrEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # List of inbox message types to search within.
        # @var string
        self.typeIn = typeIn

        # createdAtGreaterThanOrEqual
        # @var int
        self.createdAtGreaterThanOrEqual = createdAtGreaterThanOrEqual

        # createdAtLessThanOrEqual
        # @var int
        self.createdAtLessThanOrEqual = createdAtLessThanOrEqual


    PROPERTY_LOADERS = {
        'typeIn': getXmlNodeText, 
        'createdAtGreaterThanOrEqual': getXmlNodeInt, 
        'createdAtLessThanOrEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaInboxMessageFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaInboxMessageFilter")
        kparams.addStringIfDefined("typeIn", self.typeIn)
        kparams.addIntIfDefined("createdAtGreaterThanOrEqual", self.createdAtGreaterThanOrEqual)
        kparams.addIntIfDefined("createdAtLessThanOrEqual", self.createdAtLessThanOrEqual)
        return kparams

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn

    def getCreatedAtGreaterThanOrEqual(self):
        return self.createdAtGreaterThanOrEqual

    def setCreatedAtGreaterThanOrEqual(self, newCreatedAtGreaterThanOrEqual):
        self.createdAtGreaterThanOrEqual = newCreatedAtGreaterThanOrEqual

    def getCreatedAtLessThanOrEqual(self):
        return self.createdAtLessThanOrEqual

    def setCreatedAtLessThanOrEqual(self, newCreatedAtLessThanOrEqual):
        self.createdAtLessThanOrEqual = newCreatedAtLessThanOrEqual


# @package Kaltura
# @subpackage Client
class KalturaAnnouncementFilter(KalturaFilter):
    """order announcements"""

    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAnnouncementFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaAnnouncementFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPersonalFeedFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPersonalFeedFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaPersonalFeedFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaTopicFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTopicFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaTopicFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaAggregationCountFilter(KalturaRelatedObjectFilter):
    """Kaltura Aggregation CountFilter"""

    def __init__(self,
            orderBy=NotImplemented):
        KalturaRelatedObjectFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaRelatedObjectFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAggregationCountFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaRelatedObjectFilter.toParams(self)
        kparams.put("objectType", "KalturaAggregationCountFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPersistedFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Name for the presisted filter. If empty, no action will be done. If has value, the filter will be saved and persisted in user&#39;s search history.
        # @var string
        self.name = name


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPersistedFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaPersistedFilter")
        kparams.addStringIfDefined("name", self.name)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName


# @package Kaltura
# @subpackage Client
class KalturaDynamicOrderBy(KalturaObjectBase):
    """Kaltura Asset Order"""

    def __init__(self,
            name=NotImplemented,
            orderBy=NotImplemented):
        KalturaObjectBase.__init__(self)

        # order by name
        # @var string
        self.name = name

        # order by meta asc/desc
        # @var KalturaMetaTagOrderBy
        self.orderBy = orderBy


    PROPERTY_LOADERS = {
        'name': getXmlNodeText, 
        'orderBy': (KalturaEnumsFactory.createString, "KalturaMetaTagOrderBy"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDynamicOrderBy.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaDynamicOrderBy")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringEnumIfDefined("orderBy", self.orderBy)
        return kparams

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getOrderBy(self):
        return self.orderBy

    def setOrderBy(self, newOrderBy):
        self.orderBy = newOrderBy


# @package Kaltura
# @subpackage Client
class KalturaAssetFilter(KalturaPersistedFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented):
        KalturaPersistedFilter.__init__(self,
            orderBy,
            name)

        # dynamicOrderBy - order by Meta
        # @var KalturaDynamicOrderBy
        self.dynamicOrderBy = dynamicOrderBy


    PROPERTY_LOADERS = {
        'dynamicOrderBy': (KalturaObjectFactory.create, 'KalturaDynamicOrderBy'), 
    }

    def fromXml(self, node):
        KalturaPersistedFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPersistedFilter.toParams(self)
        kparams.put("objectType", "KalturaAssetFilter")
        kparams.addObjectIfDefined("dynamicOrderBy", self.dynamicOrderBy)
        return kparams

    def getDynamicOrderBy(self):
        return self.dynamicOrderBy

    def setDynamicOrderBy(self, newDynamicOrderBy):
        self.dynamicOrderBy = newDynamicOrderBy


# @package Kaltura
# @subpackage Client
class KalturaBaseSearchAssetFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            groupBy=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # groupBy
        # @var array of KalturaAssetGroupBy
        self.groupBy = groupBy


    PROPERTY_LOADERS = {
        'groupBy': (KalturaObjectFactory.createArray, 'KalturaAssetGroupBy'), 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBaseSearchAssetFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaBaseSearchAssetFilter")
        kparams.addArrayIfDefined("groupBy", self.groupBy)
        return kparams

    def getGroupBy(self):
        return self.groupBy

    def setGroupBy(self, newGroupBy):
        self.groupBy = newGroupBy


# @package Kaltura
# @subpackage Client
class KalturaScheduledRecordingProgramFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            recordingTypeEqual=NotImplemented,
            channelsIn=NotImplemented,
            startDateGreaterThanOrNull=NotImplemented,
            endDateLessThanOrNull=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # The type of recordings to return
        # @var KalturaScheduledRecordingAssetType
        self.recordingTypeEqual = recordingTypeEqual

        # Channels to filter by
        # @var string
        self.channelsIn = channelsIn

        # start date
        # @var int
        self.startDateGreaterThanOrNull = startDateGreaterThanOrNull

        # end date
        # @var int
        self.endDateLessThanOrNull = endDateLessThanOrNull


    PROPERTY_LOADERS = {
        'recordingTypeEqual': (KalturaEnumsFactory.createString, "KalturaScheduledRecordingAssetType"), 
        'channelsIn': getXmlNodeText, 
        'startDateGreaterThanOrNull': getXmlNodeInt, 
        'endDateLessThanOrNull': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaScheduledRecordingProgramFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaScheduledRecordingProgramFilter")
        kparams.addStringEnumIfDefined("recordingTypeEqual", self.recordingTypeEqual)
        kparams.addStringIfDefined("channelsIn", self.channelsIn)
        kparams.addIntIfDefined("startDateGreaterThanOrNull", self.startDateGreaterThanOrNull)
        kparams.addIntIfDefined("endDateLessThanOrNull", self.endDateLessThanOrNull)
        return kparams

    def getRecordingTypeEqual(self):
        return self.recordingTypeEqual

    def setRecordingTypeEqual(self, newRecordingTypeEqual):
        self.recordingTypeEqual = newRecordingTypeEqual

    def getChannelsIn(self):
        return self.channelsIn

    def setChannelsIn(self, newChannelsIn):
        self.channelsIn = newChannelsIn

    def getStartDateGreaterThanOrNull(self):
        return self.startDateGreaterThanOrNull

    def setStartDateGreaterThanOrNull(self, newStartDateGreaterThanOrNull):
        self.startDateGreaterThanOrNull = newStartDateGreaterThanOrNull

    def getEndDateLessThanOrNull(self):
        return self.endDateLessThanOrNull

    def setEndDateLessThanOrNull(self, newEndDateLessThanOrNull):
        self.endDateLessThanOrNull = newEndDateLessThanOrNull


# @package Kaltura
# @subpackage Client
class KalturaBundleFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            idEqual=NotImplemented,
            typeIn=NotImplemented,
            bundleTypeEqual=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # Bundle Id.
        # @var int
        self.idEqual = idEqual

        # Comma separated list of asset types to search within. 
        #             Possible values: 0 - EPG linear programs entries, any media type ID (according to media type IDs defined dynamically in the system).
        #             If omitted - all types should be included.
        # @var string
        self.typeIn = typeIn

        # bundleType - possible values: Subscription or Collection
        # @var KalturaBundleType
        self.bundleTypeEqual = bundleTypeEqual


    PROPERTY_LOADERS = {
        'idEqual': getXmlNodeInt, 
        'typeIn': getXmlNodeText, 
        'bundleTypeEqual': (KalturaEnumsFactory.createString, "KalturaBundleType"), 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBundleFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaBundleFilter")
        kparams.addIntIfDefined("idEqual", self.idEqual)
        kparams.addStringIfDefined("typeIn", self.typeIn)
        kparams.addStringEnumIfDefined("bundleTypeEqual", self.bundleTypeEqual)
        return kparams

    def getIdEqual(self):
        return self.idEqual

    def setIdEqual(self, newIdEqual):
        self.idEqual = newIdEqual

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn

    def getBundleTypeEqual(self):
        return self.bundleTypeEqual

    def setBundleTypeEqual(self, newBundleTypeEqual):
        self.bundleTypeEqual = newBundleTypeEqual


# @package Kaltura
# @subpackage Client
class KalturaChannelExternalFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            idEqual=NotImplemented,
            utcOffsetEqual=NotImplemented,
            freeText=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # External Channel Id.
        # @var int
        self.idEqual = idEqual

        # UtcOffsetEqual
        # @var float
        self.utcOffsetEqual = utcOffsetEqual

        # FreeTextEqual
        # @var string
        self.freeText = freeText


    PROPERTY_LOADERS = {
        'idEqual': getXmlNodeInt, 
        'utcOffsetEqual': getXmlNodeFloat, 
        'freeText': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaChannelExternalFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaChannelExternalFilter")
        kparams.addIntIfDefined("idEqual", self.idEqual)
        kparams.addFloatIfDefined("utcOffsetEqual", self.utcOffsetEqual)
        kparams.addStringIfDefined("freeText", self.freeText)
        return kparams

    def getIdEqual(self):
        return self.idEqual

    def setIdEqual(self, newIdEqual):
        self.idEqual = newIdEqual

    def getUtcOffsetEqual(self):
        return self.utcOffsetEqual

    def setUtcOffsetEqual(self, newUtcOffsetEqual):
        self.utcOffsetEqual = newUtcOffsetEqual

    def getFreeText(self):
        return self.freeText

    def setFreeText(self, newFreeText):
        self.freeText = newFreeText


# @package Kaltura
# @subpackage Client
class KalturaChannelFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            idEqual=NotImplemented,
            kSql=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # Channel Id
        # @var int
        self.idEqual = idEqual

        # Search assets using dynamic criteria. Provided collection of nested expressions with key, comparison operators, value, and logical conjunction.
        #             Possible keys: any Tag or Meta defined in the system and the following reserved keys: start_date, end_date. 
        #             epg_id, media_id - for specific asset IDs.
        #             geo_block - only valid value is &quot;true&quot;: When enabled, only assets that are not restriced to the user by geo-block rules will return.
        #             parental_rules - only valid value is &quot;true&quot;: When enabled, only assets that the user doesn&#39;t need to provide PIN code will return.
        #             user_interests - only valid value is &quot;true&quot;. When enabled, only assets that the user defined as his interests (by tags and metas) will return.
        #             epg_channel_id - the channel identifier of the EPG program.
        #             entitled_assets - valid values: &quot;free&quot;, &quot;entitled&quot;, &quot;both&quot;. free - gets only free to watch assets. entitled - only those that the user is implicitly entitled to watch.
        #             Comparison operators: for numerical fields =, &gt;, &gt;=, &lt;, &lt;=, : (in). 
        #             For alpha-numerical fields =, != (not), ~ (like), !~, ^ (any word starts with), ^= (phrase starts with), + (exists), !+ (not exists).
        #             Logical conjunction: and, or. 
        #             Search values are limited to 20 characters each.
        #             (maximum length of entire filter is 2048 characters)
        # @var string
        self.kSql = kSql


    PROPERTY_LOADERS = {
        'idEqual': getXmlNodeInt, 
        'kSql': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaChannelFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaChannelFilter")
        kparams.addIntIfDefined("idEqual", self.idEqual)
        kparams.addStringIfDefined("kSql", self.kSql)
        return kparams

    def getIdEqual(self):
        return self.idEqual

    def setIdEqual(self, newIdEqual):
        self.idEqual = newIdEqual

    def getKSql(self):
        return self.kSql

    def setKSql(self, newKSql):
        self.kSql = newKSql


# @package Kaltura
# @subpackage Client
class KalturaRelatedFilter(KalturaBaseSearchAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            groupBy=NotImplemented,
            kSql=NotImplemented,
            idEqual=NotImplemented,
            typeIn=NotImplemented):
        KalturaBaseSearchAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy,
            groupBy)

        # Search assets using dynamic criteria. Provided collection of nested expressions with key, comparison operators, value, and logical conjunction.
        #             Possible keys: any Tag or Meta defined in the system and the following reserved keys: start_date, end_date. 
        #             epg_id, media_id - for specific asset IDs.
        #             geo_block - only valid value is &quot;true&quot;: When enabled, only assets that are not restriced to the user by geo-block rules will return.
        #             parental_rules - only valid value is &quot;true&quot;: When enabled, only assets that the user doesn&#39;t need to provide PIN code will return.
        #             user_interests - only valid value is &quot;true&quot;. When enabled, only assets that the user defined as his interests (by tags and metas) will return.
        #             epg_channel_id - the channel identifier of the EPG program.
        #             entitled_assets - valid values: &quot;free&quot;, &quot;entitled&quot;, &quot;both&quot;. free - gets only free to watch assets. entitled - only those that the user is implicitly entitled to watch.
        #             Comparison operators: for numerical fields =, &gt;, &gt;=, &lt;, &lt;=, : (in). 
        #             For alpha-numerical fields =, != (not), ~ (like), !~, ^ (any word starts with), ^= (phrase starts with), + (exists), !+ (not exists).
        #             Logical conjunction: and, or. 
        #             Search values are limited to 20 characters each.
        #             (maximum length of entire filter is 2048 characters)
        # @var string
        self.kSql = kSql

        # the ID of the asset for which to return related assets
        # @var int
        self.idEqual = idEqual

        # Comma separated list of asset types to search within. 
        #             Possible values: any media type ID (according to media type IDs defined dynamically in the system).
        #             If omitted -   same type as the provided asset.
        # @var string
        self.typeIn = typeIn


    PROPERTY_LOADERS = {
        'kSql': getXmlNodeText, 
        'idEqual': getXmlNodeInt, 
        'typeIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaBaseSearchAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRelatedFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaBaseSearchAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaRelatedFilter")
        kparams.addStringIfDefined("kSql", self.kSql)
        kparams.addIntIfDefined("idEqual", self.idEqual)
        kparams.addStringIfDefined("typeIn", self.typeIn)
        return kparams

    def getKSql(self):
        return self.kSql

    def setKSql(self, newKSql):
        self.kSql = newKSql

    def getIdEqual(self):
        return self.idEqual

    def setIdEqual(self, newIdEqual):
        self.idEqual = newIdEqual

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn


# @package Kaltura
# @subpackage Client
class KalturaRelatedExternalFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            idEqual=NotImplemented,
            typeIn=NotImplemented,
            utcOffsetEqual=NotImplemented,
            freeText=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # the External ID of the asset for which to return related assets
        # @var int
        self.idEqual = idEqual

        # Comma separated list of asset types to search within. 
        #             Possible values: 0 - EPG linear programs entries, any media type ID (according to media type IDs defined dynamically in the system).
        #             If omitted - all types should be included.
        # @var string
        self.typeIn = typeIn

        # UtcOffsetEqual
        # @var int
        self.utcOffsetEqual = utcOffsetEqual

        # FreeText
        # @var string
        self.freeText = freeText


    PROPERTY_LOADERS = {
        'idEqual': getXmlNodeInt, 
        'typeIn': getXmlNodeText, 
        'utcOffsetEqual': getXmlNodeInt, 
        'freeText': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRelatedExternalFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaRelatedExternalFilter")
        kparams.addIntIfDefined("idEqual", self.idEqual)
        kparams.addStringIfDefined("typeIn", self.typeIn)
        kparams.addIntIfDefined("utcOffsetEqual", self.utcOffsetEqual)
        kparams.addStringIfDefined("freeText", self.freeText)
        return kparams

    def getIdEqual(self):
        return self.idEqual

    def setIdEqual(self, newIdEqual):
        self.idEqual = newIdEqual

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn

    def getUtcOffsetEqual(self):
        return self.utcOffsetEqual

    def setUtcOffsetEqual(self, newUtcOffsetEqual):
        self.utcOffsetEqual = newUtcOffsetEqual

    def getFreeText(self):
        return self.freeText

    def setFreeText(self, newFreeText):
        self.freeText = newFreeText


# @package Kaltura
# @subpackage Client
class KalturaSearchAssetFilter(KalturaBaseSearchAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            groupBy=NotImplemented,
            kSql=NotImplemented,
            typeIn=NotImplemented,
            idIn=NotImplemented):
        KalturaBaseSearchAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy,
            groupBy)

        # Search assets using dynamic criteria. Provided collection of nested expressions with key, comparison operators, value, and logical conjunction.
        #             Possible keys: any Tag or Meta defined in the system and the following reserved keys: start_date, end_date. 
        #             epg_id, media_id - for specific asset IDs.
        #             geo_block - only valid value is &quot;true&quot;: When enabled, only assets that are not restriced to the user by geo-block rules will return.
        #             parental_rules - only valid value is &quot;true&quot;: When enabled, only assets that the user doesn&#39;t need to provide PIN code will return.
        #             user_interests - only valid value is &quot;true&quot;. When enabled, only assets that the user defined as his interests (by tags and metas) will return.
        #             epg_channel_id - the channel identifier of the EPG program.
        #             entitled_assets - valid values: &quot;free&quot;, &quot;entitled&quot;, &quot;both&quot;. free - gets only free to watch assets. entitled - only those that the user is implicitly entitled to watch.
        #             Comparison operators: for numerical fields =, &gt;, &gt;=, &lt;, &lt;=, : (in). 
        #             For alpha-numerical fields =, != (not), ~ (like), !~, ^ (any word starts with), ^= (phrase starts with), + (exists), !+ (not exists).
        #             Logical conjunction: and, or. 
        #             Search values are limited to 20 characters each.
        #             (maximum length of entire filter is 2048 characters)
        # @var string
        self.kSql = kSql

        # Comma separated list of asset types to search within. 
        #             Possible values: 0 - EPG linear programs entries; 1 - Recordings; Any media type ID (according to media type IDs defined dynamically in the system).
        #             If omitted - all types should be included.
        # @var string
        self.typeIn = typeIn

        # Comma separated list of EPG channel ids to search within.
        # @var string
        self.idIn = idIn


    PROPERTY_LOADERS = {
        'kSql': getXmlNodeText, 
        'typeIn': getXmlNodeText, 
        'idIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaBaseSearchAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSearchAssetFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaBaseSearchAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaSearchAssetFilter")
        kparams.addStringIfDefined("kSql", self.kSql)
        kparams.addStringIfDefined("typeIn", self.typeIn)
        kparams.addStringIfDefined("idIn", self.idIn)
        return kparams

    def getKSql(self):
        return self.kSql

    def setKSql(self, newKSql):
        self.kSql = newKSql

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn


# @package Kaltura
# @subpackage Client
class KalturaSearchExternalFilter(KalturaAssetFilter):
    def __init__(self,
            orderBy=NotImplemented,
            name=NotImplemented,
            dynamicOrderBy=NotImplemented,
            query=NotImplemented,
            utcOffsetEqual=NotImplemented,
            typeIn=NotImplemented):
        KalturaAssetFilter.__init__(self,
            orderBy,
            name,
            dynamicOrderBy)

        # Query
        # @var string
        self.query = query

        # UtcOffsetEqual
        # @var int
        self.utcOffsetEqual = utcOffsetEqual

        # Comma separated list of asset types to search within. 
        #             Possible values: 0 - EPG linear programs entries, any media type ID (according to media type IDs defined dynamically in the system).
        #             If omitted - all types should be included.
        # @var string
        self.typeIn = typeIn


    PROPERTY_LOADERS = {
        'query': getXmlNodeText, 
        'utcOffsetEqual': getXmlNodeInt, 
        'typeIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaAssetFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSearchExternalFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaAssetFilter.toParams(self)
        kparams.put("objectType", "KalturaSearchExternalFilter")
        kparams.addStringIfDefined("query", self.query)
        kparams.addIntIfDefined("utcOffsetEqual", self.utcOffsetEqual)
        kparams.addStringIfDefined("typeIn", self.typeIn)
        return kparams

    def getQuery(self):
        return self.query

    def setQuery(self, newQuery):
        self.query = newQuery

    def getUtcOffsetEqual(self):
        return self.utcOffsetEqual

    def setUtcOffsetEqual(self, newUtcOffsetEqual):
        self.utcOffsetEqual = newUtcOffsetEqual

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn


# @package Kaltura
# @subpackage Client
class KalturaSeriesRecordingFilter(KalturaFilter):
    """Filtering recordings"""

    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSeriesRecordingFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSeriesRecordingFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaProductPriceFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            subscriptionIdIn=NotImplemented,
            fileIdIn=NotImplemented,
            collectionIdIn=NotImplemented,
            isLowest=NotImplemented,
            couponCodeEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated subscriptions identifiers
        # @var string
        self.subscriptionIdIn = subscriptionIdIn

        # Comma separated media files identifiers
        # @var string
        self.fileIdIn = fileIdIn

        # Comma separated collections identifiers
        # @var string
        self.collectionIdIn = collectionIdIn

        # A flag that indicates if only the lowest price of an item should return
        # @var bool
        self.isLowest = isLowest

        # Discount coupon code
        # @var string
        self.couponCodeEqual = couponCodeEqual


    PROPERTY_LOADERS = {
        'subscriptionIdIn': getXmlNodeText, 
        'fileIdIn': getXmlNodeText, 
        'collectionIdIn': getXmlNodeText, 
        'isLowest': getXmlNodeBool, 
        'couponCodeEqual': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaProductPriceFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaProductPriceFilter")
        kparams.addStringIfDefined("subscriptionIdIn", self.subscriptionIdIn)
        kparams.addStringIfDefined("fileIdIn", self.fileIdIn)
        kparams.addStringIfDefined("collectionIdIn", self.collectionIdIn)
        kparams.addBoolIfDefined("isLowest", self.isLowest)
        kparams.addStringIfDefined("couponCodeEqual", self.couponCodeEqual)
        return kparams

    def getSubscriptionIdIn(self):
        return self.subscriptionIdIn

    def setSubscriptionIdIn(self, newSubscriptionIdIn):
        self.subscriptionIdIn = newSubscriptionIdIn

    def getFileIdIn(self):
        return self.fileIdIn

    def setFileIdIn(self, newFileIdIn):
        self.fileIdIn = newFileIdIn

    def getCollectionIdIn(self):
        return self.collectionIdIn

    def setCollectionIdIn(self, newCollectionIdIn):
        self.collectionIdIn = newCollectionIdIn

    def getIsLowest(self):
        return self.isLowest

    def setIsLowest(self, newIsLowest):
        self.isLowest = newIsLowest

    def getCouponCodeEqual(self):
        return self.couponCodeEqual

    def setCouponCodeEqual(self, newCouponCodeEqual):
        self.couponCodeEqual = newCouponCodeEqual


# @package Kaltura
# @subpackage Client
class KalturaEntitlementFilter(KalturaFilter):
    """Entitlements filter"""

    def __init__(self,
            orderBy=NotImplemented,
            productTypeEqual=NotImplemented,
            entityReferenceEqual=NotImplemented,
            isExpiredEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # The type of the entitlements to return
        # @var KalturaTransactionType
        self.productTypeEqual = productTypeEqual

        # Reference type to filter by
        # @var KalturaEntityReferenceBy
        self.entityReferenceEqual = entityReferenceEqual

        # Is expired
        # @var bool
        self.isExpiredEqual = isExpiredEqual


    PROPERTY_LOADERS = {
        'productTypeEqual': (KalturaEnumsFactory.createString, "KalturaTransactionType"), 
        'entityReferenceEqual': (KalturaEnumsFactory.createString, "KalturaEntityReferenceBy"), 
        'isExpiredEqual': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEntitlementFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaEntitlementFilter")
        kparams.addStringEnumIfDefined("productTypeEqual", self.productTypeEqual)
        kparams.addStringEnumIfDefined("entityReferenceEqual", self.entityReferenceEqual)
        kparams.addBoolIfDefined("isExpiredEqual", self.isExpiredEqual)
        return kparams

    def getProductTypeEqual(self):
        return self.productTypeEqual

    def setProductTypeEqual(self, newProductTypeEqual):
        self.productTypeEqual = newProductTypeEqual

    def getEntityReferenceEqual(self):
        return self.entityReferenceEqual

    def setEntityReferenceEqual(self, newEntityReferenceEqual):
        self.entityReferenceEqual = newEntityReferenceEqual

    def getIsExpiredEqual(self):
        return self.isExpiredEqual

    def setIsExpiredEqual(self, newIsExpiredEqual):
        self.isExpiredEqual = newIsExpiredEqual


# @package Kaltura
# @subpackage Client
class KalturaTransactionHistoryFilter(KalturaFilter):
    """Transactions filter"""

    def __init__(self,
            orderBy=NotImplemented,
            entityReferenceEqual=NotImplemented,
            startDateGreaterThanOrEqual=NotImplemented,
            endDateLessThanOrEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Reference type to filter by
        # @var KalturaEntityReferenceBy
        self.entityReferenceEqual = entityReferenceEqual

        # Filter transactions later than specific date
        # @var int
        self.startDateGreaterThanOrEqual = startDateGreaterThanOrEqual

        # Filter transactions earlier than specific date
        # @var int
        self.endDateLessThanOrEqual = endDateLessThanOrEqual


    PROPERTY_LOADERS = {
        'entityReferenceEqual': (KalturaEnumsFactory.createString, "KalturaEntityReferenceBy"), 
        'startDateGreaterThanOrEqual': getXmlNodeInt, 
        'endDateLessThanOrEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTransactionHistoryFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaTransactionHistoryFilter")
        kparams.addStringEnumIfDefined("entityReferenceEqual", self.entityReferenceEqual)
        kparams.addIntIfDefined("startDateGreaterThanOrEqual", self.startDateGreaterThanOrEqual)
        kparams.addIntIfDefined("endDateLessThanOrEqual", self.endDateLessThanOrEqual)
        return kparams

    def getEntityReferenceEqual(self):
        return self.entityReferenceEqual

    def setEntityReferenceEqual(self, newEntityReferenceEqual):
        self.entityReferenceEqual = newEntityReferenceEqual

    def getStartDateGreaterThanOrEqual(self):
        return self.startDateGreaterThanOrEqual

    def setStartDateGreaterThanOrEqual(self, newStartDateGreaterThanOrEqual):
        self.startDateGreaterThanOrEqual = newStartDateGreaterThanOrEqual

    def getEndDateLessThanOrEqual(self):
        return self.endDateLessThanOrEqual

    def setEndDateLessThanOrEqual(self, newEndDateLessThanOrEqual):
        self.endDateLessThanOrEqual = newEndDateLessThanOrEqual


# @package Kaltura
# @subpackage Client
class KalturaRecordingContextFilter(KalturaFilter):
    """Filtering assets"""

    def __init__(self,
            orderBy=NotImplemented,
            assetIdIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated asset ids
        # @var string
        self.assetIdIn = assetIdIn


    PROPERTY_LOADERS = {
        'assetIdIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecordingContextFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaRecordingContextFilter")
        kparams.addStringIfDefined("assetIdIn", self.assetIdIn)
        return kparams

    def getAssetIdIn(self):
        return self.assetIdIn

    def setAssetIdIn(self, newAssetIdIn):
        self.assetIdIn = newAssetIdIn


# @package Kaltura
# @subpackage Client
class KalturaRecordingFilter(KalturaFilter):
    """Filtering recordings"""

    def __init__(self,
            orderBy=NotImplemented,
            statusIn=NotImplemented,
            filterExpression=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Recording Statuses
        # @var string
        self.statusIn = statusIn

        # KSQL expression
        # @var string
        self.filterExpression = filterExpression


    PROPERTY_LOADERS = {
        'statusIn': getXmlNodeText, 
        'filterExpression': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRecordingFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaRecordingFilter")
        kparams.addStringIfDefined("statusIn", self.statusIn)
        kparams.addStringIfDefined("filterExpression", self.filterExpression)
        return kparams

    def getStatusIn(self):
        return self.statusIn

    def setStatusIn(self, newStatusIn):
        self.statusIn = newStatusIn

    def getFilterExpression(self):
        return self.filterExpression

    def setFilterExpression(self, newFilterExpression):
        self.filterExpression = newFilterExpression


# @package Kaltura
# @subpackage Client
class KalturaAssetCommentFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            assetIdEqual=NotImplemented,
            assetTypeEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Asset Id
        # @var int
        self.assetIdEqual = assetIdEqual

        # Asset Type
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual


    PROPERTY_LOADERS = {
        'assetIdEqual': getXmlNodeInt, 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetCommentFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaAssetCommentFilter")
        kparams.addIntIfDefined("assetIdEqual", self.assetIdEqual)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        return kparams

    def getAssetIdEqual(self):
        return self.assetIdEqual

    def setAssetIdEqual(self, newAssetIdEqual):
        self.assetIdEqual = newAssetIdEqual

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual


# @package Kaltura
# @subpackage Client
class KalturaBookmarkFilter(KalturaFilter):
    """Filtering Assets requests"""

    def __init__(self,
            orderBy=NotImplemented,
            assetIdIn=NotImplemented,
            assetTypeEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated list of assets identifiers
        # @var string
        self.assetIdIn = assetIdIn

        # Asset type
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual


    PROPERTY_LOADERS = {
        'assetIdIn': getXmlNodeText, 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBookmarkFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaBookmarkFilter")
        kparams.addStringIfDefined("assetIdIn", self.assetIdIn)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        return kparams

    def getAssetIdIn(self):
        return self.assetIdIn

    def setAssetIdIn(self, newAssetIdIn):
        self.assetIdIn = newAssetIdIn

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual


# @package Kaltura
# @subpackage Client
class KalturaAssetHistoryFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            typeIn=NotImplemented,
            assetIdIn=NotImplemented,
            statusEqual=NotImplemented,
            daysLessThanOrEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated list of asset types to search within.
        #             Possible values: 0 - EPG linear programs entries, any media type ID (according to media type IDs defined dynamically in the system).
        #             If omitted - all types should be included.
        # @var string
        self.typeIn = typeIn

        # Comma separated list of asset identifiers.
        # @var string
        self.assetIdIn = assetIdIn

        # Which type of recently watched media to include in the result - those that finished watching, those that are in progress or both.
        #             If omitted or specified filter = all - return all types.
        #             Allowed values: progress - return medias that are in-progress, done - return medias that finished watching.
        # @var KalturaWatchStatus
        self.statusEqual = statusEqual

        # How many days back to return the watched media. If omitted, default to 7 days
        # @var int
        self.daysLessThanOrEqual = daysLessThanOrEqual


    PROPERTY_LOADERS = {
        'typeIn': getXmlNodeText, 
        'assetIdIn': getXmlNodeText, 
        'statusEqual': (KalturaEnumsFactory.createString, "KalturaWatchStatus"), 
        'daysLessThanOrEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetHistoryFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaAssetHistoryFilter")
        kparams.addStringIfDefined("typeIn", self.typeIn)
        kparams.addStringIfDefined("assetIdIn", self.assetIdIn)
        kparams.addStringEnumIfDefined("statusEqual", self.statusEqual)
        kparams.addIntIfDefined("daysLessThanOrEqual", self.daysLessThanOrEqual)
        return kparams

    def getTypeIn(self):
        return self.typeIn

    def setTypeIn(self, newTypeIn):
        self.typeIn = newTypeIn

    def getAssetIdIn(self):
        return self.assetIdIn

    def setAssetIdIn(self, newAssetIdIn):
        self.assetIdIn = newAssetIdIn

    def getStatusEqual(self):
        return self.statusEqual

    def setStatusEqual(self, newStatusEqual):
        self.statusEqual = newStatusEqual

    def getDaysLessThanOrEqual(self):
        return self.daysLessThanOrEqual

    def setDaysLessThanOrEqual(self, newDaysLessThanOrEqual):
        self.daysLessThanOrEqual = newDaysLessThanOrEqual


# @package Kaltura
# @subpackage Client
class KalturaCurrencyFilter(KalturaFilter):
    """Currency filter"""

    def __init__(self,
            orderBy=NotImplemented,
            codeIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Currency codes
        # @var string
        self.codeIn = codeIn


    PROPERTY_LOADERS = {
        'codeIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCurrencyFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaCurrencyFilter")
        kparams.addStringIfDefined("codeIn", self.codeIn)
        return kparams

    def getCodeIn(self):
        return self.codeIn

    def setCodeIn(self, newCodeIn):
        self.codeIn = newCodeIn


# @package Kaltura
# @subpackage Client
class KalturaLanguageFilter(KalturaFilter):
    """Language filter"""

    def __init__(self,
            orderBy=NotImplemented,
            codeIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Language codes
        # @var string
        self.codeIn = codeIn


    PROPERTY_LOADERS = {
        'codeIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLanguageFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaLanguageFilter")
        kparams.addStringIfDefined("codeIn", self.codeIn)
        return kparams

    def getCodeIn(self):
        return self.codeIn

    def setCodeIn(self, newCodeIn):
        self.codeIn = newCodeIn


# @package Kaltura
# @subpackage Client
class KalturaMetaFilter(KalturaFilter):
    """Meta filter"""

    def __init__(self,
            orderBy=NotImplemented,
            fieldNameEqual=NotImplemented,
            fieldNameNotEqual=NotImplemented,
            typeEqual=NotImplemented,
            assetTypeEqual=NotImplemented,
            featuresIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Meta system field name to filter by
        # @var KalturaMetaFieldName
        self.fieldNameEqual = fieldNameEqual

        # Meta system field name to filter by
        # @var KalturaMetaFieldName
        self.fieldNameNotEqual = fieldNameNotEqual

        # Meta type to filter by
        # @var KalturaMetaType
        self.typeEqual = typeEqual

        # Asset type to filter by
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual

        # Features
        # @var string
        self.featuresIn = featuresIn


    PROPERTY_LOADERS = {
        'fieldNameEqual': (KalturaEnumsFactory.createString, "KalturaMetaFieldName"), 
        'fieldNameNotEqual': (KalturaEnumsFactory.createString, "KalturaMetaFieldName"), 
        'typeEqual': (KalturaEnumsFactory.createString, "KalturaMetaType"), 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'featuresIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMetaFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaMetaFilter")
        kparams.addStringEnumIfDefined("fieldNameEqual", self.fieldNameEqual)
        kparams.addStringEnumIfDefined("fieldNameNotEqual", self.fieldNameNotEqual)
        kparams.addStringEnumIfDefined("typeEqual", self.typeEqual)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        kparams.addStringIfDefined("featuresIn", self.featuresIn)
        return kparams

    def getFieldNameEqual(self):
        return self.fieldNameEqual

    def setFieldNameEqual(self, newFieldNameEqual):
        self.fieldNameEqual = newFieldNameEqual

    def getFieldNameNotEqual(self):
        return self.fieldNameNotEqual

    def setFieldNameNotEqual(self, newFieldNameNotEqual):
        self.fieldNameNotEqual = newFieldNameNotEqual

    def getTypeEqual(self):
        return self.typeEqual

    def setTypeEqual(self, newTypeEqual):
        self.typeEqual = newTypeEqual

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual

    def getFeaturesIn(self):
        return self.featuresIn

    def setFeaturesIn(self, newFeaturesIn):
        self.featuresIn = newFeaturesIn


# @package Kaltura
# @subpackage Client
class KalturaCountryFilter(KalturaFilter):
    """Country filter"""

    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented,
            ipEqual=NotImplemented,
            ipEqualCurrent=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Country identifiers
        # @var string
        self.idIn = idIn

        # Ip to identify the country
        # @var string
        self.ipEqual = ipEqual

        # Indicates if to get the IP from the request
        # @var bool
        self.ipEqualCurrent = ipEqualCurrent


    PROPERTY_LOADERS = {
        'idIn': getXmlNodeText, 
        'ipEqual': getXmlNodeText, 
        'ipEqualCurrent': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCountryFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaCountryFilter")
        kparams.addStringIfDefined("idIn", self.idIn)
        kparams.addStringIfDefined("ipEqual", self.ipEqual)
        kparams.addBoolIfDefined("ipEqualCurrent", self.ipEqualCurrent)
        return kparams

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn

    def getIpEqual(self):
        return self.ipEqual

    def setIpEqual(self, newIpEqual):
        self.ipEqual = newIpEqual

    def getIpEqualCurrent(self):
        return self.ipEqualCurrent

    def setIpEqualCurrent(self, newIpEqualCurrent):
        self.ipEqualCurrent = newIpEqualCurrent


# @package Kaltura
# @subpackage Client
class KalturaSearchHistoryFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSearchHistoryFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaSearchHistoryFilter")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaRegionFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            externalIdIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # List of comma separated regions external identifiers
        # @var string
        self.externalIdIn = externalIdIn


    PROPERTY_LOADERS = {
        'externalIdIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegionFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaRegionFilter")
        kparams.addStringIfDefined("externalIdIn", self.externalIdIn)
        return kparams

    def getExternalIdIn(self):
        return self.externalIdIn

    def setExternalIdIn(self, newExternalIdIn):
        self.externalIdIn = newExternalIdIn


# @package Kaltura
# @subpackage Client
class KalturaUserAssetRuleFilter(KalturaFilter):
    """User asset rule filter"""

    def __init__(self,
            orderBy=NotImplemented,
            assetIdEqual=NotImplemented,
            assetTypeEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Asset identifier to filter by
        # @var int
        self.assetIdEqual = assetIdEqual

        # Asset type to filter by - 0 = EPG, 1 = media
        # @var int
        self.assetTypeEqual = assetTypeEqual


    PROPERTY_LOADERS = {
        'assetIdEqual': getXmlNodeInt, 
        'assetTypeEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserAssetRuleFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaUserAssetRuleFilter")
        kparams.addIntIfDefined("assetIdEqual", self.assetIdEqual)
        kparams.addIntIfDefined("assetTypeEqual", self.assetTypeEqual)
        return kparams

    def getAssetIdEqual(self):
        return self.assetIdEqual

    def setAssetIdEqual(self, newAssetIdEqual):
        self.assetIdEqual = newAssetIdEqual

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual


# @package Kaltura
# @subpackage Client
class KalturaParentalRuleFilter(KalturaFilter):
    def __init__(self,
            orderBy=NotImplemented,
            entityReferenceEqual=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Reference type to filter by
        # @var KalturaEntityReferenceBy
        self.entityReferenceEqual = entityReferenceEqual


    PROPERTY_LOADERS = {
        'entityReferenceEqual': (KalturaEnumsFactory.createString, "KalturaEntityReferenceBy"), 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaParentalRuleFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaParentalRuleFilter")
        kparams.addStringEnumIfDefined("entityReferenceEqual", self.entityReferenceEqual)
        return kparams

    def getEntityReferenceEqual(self):
        return self.entityReferenceEqual

    def setEntityReferenceEqual(self, newEntityReferenceEqual):
        self.entityReferenceEqual = newEntityReferenceEqual


# @package Kaltura
# @subpackage Client
class KalturaExportTaskFilter(KalturaFilter):
    """Bulk export tasks filter"""

    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated tasks identifiers
        # @var string
        self.idIn = idIn


    PROPERTY_LOADERS = {
        'idIn': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaExportTaskFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaExportTaskFilter")
        kparams.addStringIfDefined("idIn", self.idIn)
        return kparams

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn


# @package Kaltura
# @subpackage Client
class KalturaUserRoleFilter(KalturaFilter):
    """User roles filter"""

    def __init__(self,
            orderBy=NotImplemented,
            idIn=NotImplemented,
            currentUserRoleIdsContains=NotImplemented):
        KalturaFilter.__init__(self,
            orderBy)

        # Comma separated roles identifiers
        # @var string
        self.idIn = idIn

        # Indicates whether the results should be filtered by userId using the current
        # @var bool
        self.currentUserRoleIdsContains = currentUserRoleIdsContains


    PROPERTY_LOADERS = {
        'idIn': getXmlNodeText, 
        'currentUserRoleIdsContains': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaFilter.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserRoleFilter.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaFilter.toParams(self)
        kparams.put("objectType", "KalturaUserRoleFilter")
        kparams.addStringIfDefined("idIn", self.idIn)
        kparams.addBoolIfDefined("currentUserRoleIdsContains", self.currentUserRoleIdsContains)
        return kparams

    def getIdIn(self):
        return self.idIn

    def setIdIn(self, newIdIn):
        self.idIn = newIdIn

    def getCurrentUserRoleIdsContains(self):
        return self.currentUserRoleIdsContains

    def setCurrentUserRoleIdsContains(self, newCurrentUserRoleIdsContains):
        self.currentUserRoleIdsContains = newCurrentUserRoleIdsContains


# @package Kaltura
# @subpackage Client
class KalturaFilterPager(KalturaObjectBase):
    """The KalturaFilterPager object enables paging management to be applied upon service list actions"""

    def __init__(self,
            pageSize=NotImplemented,
            pageIndex=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The number of objects to retrieve. Possible range 1 <= value <= 50. If omitted or value &lt; 1 - will be set to 25. If a value &gt; 50 provided - will be set to 50
        # @var int
        self.pageSize = pageSize

        # The page number for which {pageSize} of objects should be retrieved
        # @var int
        self.pageIndex = pageIndex


    PROPERTY_LOADERS = {
        'pageSize': getXmlNodeInt, 
        'pageIndex': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFilterPager.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaFilterPager")
        kparams.addIntIfDefined("pageSize", self.pageSize)
        kparams.addIntIfDefined("pageIndex", self.pageIndex)
        return kparams

    def getPageSize(self):
        return self.pageSize

    def setPageSize(self, newPageSize):
        self.pageSize = newPageSize

    def getPageIndex(self):
        return self.pageIndex

    def setPageIndex(self, newPageIndex):
        self.pageIndex = newPageIndex


# @package Kaltura
# @subpackage Client
class KalturaAppToken(KalturaObjectBase):
    """Application token"""

    def __init__(self,
            id=NotImplemented,
            expiry=NotImplemented,
            partnerId=NotImplemented,
            sessionDuration=NotImplemented,
            hashType=NotImplemented,
            sessionPrivileges=NotImplemented,
            token=NotImplemented,
            sessionUserId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The id of the application token
        # @var string
        # @readonly
        self.id = id

        # Expiry time of current token (unix timestamp in seconds)
        # @var int
        self.expiry = expiry

        # Partner identifier
        # @var int
        # @readonly
        self.partnerId = partnerId

        # Expiry duration of KS (Kaltura Session) that created using the current token (in seconds)
        # @var int
        self.sessionDuration = sessionDuration

        # The hash type of the token
        # @var KalturaAppTokenHashType
        self.hashType = hashType

        # Comma separated privileges to be applied on KS (Kaltura Session) that created using the current token
        # @var string
        self.sessionPrivileges = sessionPrivileges

        # The application token
        # @var string
        # @readonly
        self.token = token

        # User id of KS (Kaltura Session) that created using the current token
        # @var string
        self.sessionUserId = sessionUserId


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'expiry': getXmlNodeInt, 
        'partnerId': getXmlNodeInt, 
        'sessionDuration': getXmlNodeInt, 
        'hashType': (KalturaEnumsFactory.createString, "KalturaAppTokenHashType"), 
        'sessionPrivileges': getXmlNodeText, 
        'token': getXmlNodeText, 
        'sessionUserId': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAppToken.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAppToken")
        kparams.addIntIfDefined("expiry", self.expiry)
        kparams.addIntIfDefined("sessionDuration", self.sessionDuration)
        kparams.addStringEnumIfDefined("hashType", self.hashType)
        kparams.addStringIfDefined("sessionPrivileges", self.sessionPrivileges)
        kparams.addStringIfDefined("sessionUserId", self.sessionUserId)
        return kparams

    def getId(self):
        return self.id

    def getExpiry(self):
        return self.expiry

    def setExpiry(self, newExpiry):
        self.expiry = newExpiry

    def getPartnerId(self):
        return self.partnerId

    def getSessionDuration(self):
        return self.sessionDuration

    def setSessionDuration(self, newSessionDuration):
        self.sessionDuration = newSessionDuration

    def getHashType(self):
        return self.hashType

    def setHashType(self, newHashType):
        self.hashType = newHashType

    def getSessionPrivileges(self):
        return self.sessionPrivileges

    def setSessionPrivileges(self, newSessionPrivileges):
        self.sessionPrivileges = newSessionPrivileges

    def getToken(self):
        return self.token

    def getSessionUserId(self):
        return self.sessionUserId

    def setSessionUserId(self, newSessionUserId):
        self.sessionUserId = newSessionUserId


# @package Kaltura
# @subpackage Client
class KalturaSession(KalturaObjectBase):
    """Kaltura Session"""

    def __init__(self,
            ks=NotImplemented,
            partnerId=NotImplemented,
            userId=NotImplemented,
            expiry=NotImplemented,
            privileges=NotImplemented,
            udid=NotImplemented,
            createDate=NotImplemented):
        KalturaObjectBase.__init__(self)

        # KS
        # @var string
        self.ks = ks

        # Partner identifier
        # @var int
        self.partnerId = partnerId

        # User identifier
        # @var string
        self.userId = userId

        # Expiry
        # @var int
        self.expiry = expiry

        # Privileges
        # @var string
        self.privileges = privileges

        # UDID
        # @var string
        self.udid = udid

        # Create date
        # @var int
        self.createDate = createDate


    PROPERTY_LOADERS = {
        'ks': getXmlNodeText, 
        'partnerId': getXmlNodeInt, 
        'userId': getXmlNodeText, 
        'expiry': getXmlNodeInt, 
        'privileges': getXmlNodeText, 
        'udid': getXmlNodeText, 
        'createDate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSession.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSession")
        kparams.addStringIfDefined("ks", self.ks)
        kparams.addIntIfDefined("partnerId", self.partnerId)
        kparams.addStringIfDefined("userId", self.userId)
        kparams.addIntIfDefined("expiry", self.expiry)
        kparams.addStringIfDefined("privileges", self.privileges)
        kparams.addStringIfDefined("udid", self.udid)
        kparams.addIntIfDefined("createDate", self.createDate)
        return kparams

    def getKs(self):
        return self.ks

    def setKs(self, newKs):
        self.ks = newKs

    def getPartnerId(self):
        return self.partnerId

    def setPartnerId(self, newPartnerId):
        self.partnerId = newPartnerId

    def getUserId(self):
        return self.userId

    def setUserId(self, newUserId):
        self.userId = newUserId

    def getExpiry(self):
        return self.expiry

    def setExpiry(self, newExpiry):
        self.expiry = newExpiry

    def getPrivileges(self):
        return self.privileges

    def setPrivileges(self, newPrivileges):
        self.privileges = newPrivileges

    def getUdid(self):
        return self.udid

    def setUdid(self, newUdid):
        self.udid = newUdid

    def getCreateDate(self):
        return self.createDate

    def setCreateDate(self, newCreateDate):
        self.createDate = newCreateDate


# @package Kaltura
# @subpackage Client
class KalturaSessionInfo(KalturaSession):
    """Kaltura Session"""

    def __init__(self,
            ks=NotImplemented,
            partnerId=NotImplemented,
            userId=NotImplemented,
            expiry=NotImplemented,
            privileges=NotImplemented,
            udid=NotImplemented,
            createDate=NotImplemented):
        KalturaSession.__init__(self,
            ks,
            partnerId,
            userId,
            expiry,
            privileges,
            udid,
            createDate)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaSession.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSessionInfo.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSession.toParams(self)
        kparams.put("objectType", "KalturaSessionInfo")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaPlaybackContextOptions(KalturaObjectBase):
    def __init__(self,
            mediaProtocol=NotImplemented,
            streamerType=NotImplemented,
            assetFileIds=NotImplemented,
            context=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Protocol of the specific media object (http / https).
        # @var string
        self.mediaProtocol = mediaProtocol

        # Playback streamer type: applehttp, mpegdash, url.
        # @var string
        self.streamerType = streamerType

        # List of comma separated media file IDs
        # @var string
        self.assetFileIds = assetFileIds

        # Playback context type
        # @var KalturaPlaybackContextType
        self.context = context


    PROPERTY_LOADERS = {
        'mediaProtocol': getXmlNodeText, 
        'streamerType': getXmlNodeText, 
        'assetFileIds': getXmlNodeText, 
        'context': (KalturaEnumsFactory.createString, "KalturaPlaybackContextType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPlaybackContextOptions.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPlaybackContextOptions")
        kparams.addStringIfDefined("mediaProtocol", self.mediaProtocol)
        kparams.addStringIfDefined("streamerType", self.streamerType)
        kparams.addStringIfDefined("assetFileIds", self.assetFileIds)
        kparams.addStringEnumIfDefined("context", self.context)
        return kparams

    def getMediaProtocol(self):
        return self.mediaProtocol

    def setMediaProtocol(self, newMediaProtocol):
        self.mediaProtocol = newMediaProtocol

    def getStreamerType(self):
        return self.streamerType

    def setStreamerType(self, newStreamerType):
        self.streamerType = newStreamerType

    def getAssetFileIds(self):
        return self.assetFileIds

    def setAssetFileIds(self, newAssetFileIds):
        self.assetFileIds = newAssetFileIds

    def getContext(self):
        return self.context

    def setContext(self, newContext):
        self.context = newContext


# @package Kaltura
# @subpackage Client
class KalturaRuleAction(KalturaObjectBase):
    def __init__(self,
            type=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The type of the action
        # @var KalturaRuleActionType
        self.type = type


    PROPERTY_LOADERS = {
        'type': (KalturaEnumsFactory.createString, "KalturaRuleActionType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRuleAction.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRuleAction")
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType


# @package Kaltura
# @subpackage Client
class KalturaAccessControlMessage(KalturaObjectBase):
    def __init__(self,
            message=NotImplemented,
            code=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Message
        # @var string
        self.message = message

        # Code
        # @var string
        self.code = code


    PROPERTY_LOADERS = {
        'message': getXmlNodeText, 
        'code': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAccessControlMessage.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAccessControlMessage")
        kparams.addStringIfDefined("message", self.message)
        kparams.addStringIfDefined("code", self.code)
        return kparams

    def getMessage(self):
        return self.message

    def setMessage(self, newMessage):
        self.message = newMessage

    def getCode(self):
        return self.code

    def setCode(self, newCode):
        self.code = newCode


# @package Kaltura
# @subpackage Client
class KalturaPlaybackContext(KalturaObjectBase):
    def __init__(self,
            sources=NotImplemented,
            actions=NotImplemented,
            messages=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Sources
        # @var array of KalturaPlaybackSource
        self.sources = sources

        # Actions
        # @var array of KalturaRuleAction
        self.actions = actions

        # Messages
        # @var array of KalturaAccessControlMessage
        self.messages = messages


    PROPERTY_LOADERS = {
        'sources': (KalturaObjectFactory.createArray, 'KalturaPlaybackSource'), 
        'actions': (KalturaObjectFactory.createArray, 'KalturaRuleAction'), 
        'messages': (KalturaObjectFactory.createArray, 'KalturaAccessControlMessage'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPlaybackContext.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPlaybackContext")
        kparams.addArrayIfDefined("sources", self.sources)
        kparams.addArrayIfDefined("actions", self.actions)
        kparams.addArrayIfDefined("messages", self.messages)
        return kparams

    def getSources(self):
        return self.sources

    def setSources(self, newSources):
        self.sources = newSources

    def getActions(self):
        return self.actions

    def setActions(self, newActions):
        self.actions = newActions

    def getMessages(self):
        return self.messages

    def setMessages(self, newMessages):
        self.messages = newMessages


# @package Kaltura
# @subpackage Client
class KalturaAccessControlBlockAction(KalturaRuleAction):
    def __init__(self,
            type=NotImplemented):
        KalturaRuleAction.__init__(self,
            type)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaRuleAction.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAccessControlBlockAction.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaRuleAction.toParams(self)
        kparams.put("objectType", "KalturaAccessControlBlockAction")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaAdsSource(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            type=NotImplemented,
            adsPolicy=NotImplemented,
            adsParam=NotImplemented):
        KalturaObjectBase.__init__(self)

        # File unique identifier
        # @var int
        # @readonly
        self.id = id

        # Device types as defined in the system
        # @var string
        self.type = type

        # Ads policy
        # @var KalturaAdsPolicy
        self.adsPolicy = adsPolicy

        # The parameters to pass to the ads server
        # @var string
        self.adsParam = adsParam


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'type': getXmlNodeText, 
        'adsPolicy': (KalturaEnumsFactory.createString, "KalturaAdsPolicy"), 
        'adsParam': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAdsSource.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAdsSource")
        kparams.addStringIfDefined("type", self.type)
        kparams.addStringEnumIfDefined("adsPolicy", self.adsPolicy)
        kparams.addStringIfDefined("adsParam", self.adsParam)
        return kparams

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getAdsPolicy(self):
        return self.adsPolicy

    def setAdsPolicy(self, newAdsPolicy):
        self.adsPolicy = newAdsPolicy

    def getAdsParam(self):
        return self.adsParam

    def setAdsParam(self, newAdsParam):
        self.adsParam = newAdsParam


# @package Kaltura
# @subpackage Client
class KalturaAdsContext(KalturaObjectBase):
    def __init__(self,
            sources=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Sources
        # @var array of KalturaAdsSource
        self.sources = sources


    PROPERTY_LOADERS = {
        'sources': (KalturaObjectFactory.createArray, 'KalturaAdsSource'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAdsContext.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAdsContext")
        kparams.addArrayIfDefined("sources", self.sources)
        return kparams

    def getSources(self):
        return self.sources

    def setSources(self, newSources):
        self.sources = newSources


# @package Kaltura
# @subpackage Client
class KalturaAssetFileContext(KalturaObjectBase):
    def __init__(self,
            viewLifeCycle=NotImplemented,
            fullLifeCycle=NotImplemented,
            isOfflinePlayBack=NotImplemented):
        KalturaObjectBase.__init__(self)

        # viewLifeCycle
        # @var string
        # @readonly
        self.viewLifeCycle = viewLifeCycle

        # fullLifeCycle
        # @var string
        # @readonly
        self.fullLifeCycle = fullLifeCycle

        # isOfflinePlayBack
        # @var bool
        # @readonly
        self.isOfflinePlayBack = isOfflinePlayBack


    PROPERTY_LOADERS = {
        'viewLifeCycle': getXmlNodeText, 
        'fullLifeCycle': getXmlNodeText, 
        'isOfflinePlayBack': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetFileContext.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetFileContext")
        return kparams

    def getViewLifeCycle(self):
        return self.viewLifeCycle

    def getFullLifeCycle(self):
        return self.fullLifeCycle

    def getIsOfflinePlayBack(self):
        return self.isOfflinePlayBack


# @package Kaltura
# @subpackage Client
class KalturaAssetStatisticsQuery(KalturaObjectBase):
    def __init__(self,
            assetIdIn=NotImplemented,
            assetTypeEqual=NotImplemented,
            startDateGreaterThanOrEqual=NotImplemented,
            endDateGreaterThanOrEqual=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Comma separated list of asset identifiers.
        # @var string
        self.assetIdIn = assetIdIn

        # Asset type
        # @var KalturaAssetType
        self.assetTypeEqual = assetTypeEqual

        # The beginning of the time window to get the statistics for (in epoch).
        # @var int
        self.startDateGreaterThanOrEqual = startDateGreaterThanOrEqual

        # /// The end of the time window to get the statistics for (in epoch).
        # @var int
        self.endDateGreaterThanOrEqual = endDateGreaterThanOrEqual


    PROPERTY_LOADERS = {
        'assetIdIn': getXmlNodeText, 
        'assetTypeEqual': (KalturaEnumsFactory.createString, "KalturaAssetType"), 
        'startDateGreaterThanOrEqual': getXmlNodeInt, 
        'endDateGreaterThanOrEqual': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaAssetStatisticsQuery.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaAssetStatisticsQuery")
        kparams.addStringIfDefined("assetIdIn", self.assetIdIn)
        kparams.addStringEnumIfDefined("assetTypeEqual", self.assetTypeEqual)
        kparams.addIntIfDefined("startDateGreaterThanOrEqual", self.startDateGreaterThanOrEqual)
        kparams.addIntIfDefined("endDateGreaterThanOrEqual", self.endDateGreaterThanOrEqual)
        return kparams

    def getAssetIdIn(self):
        return self.assetIdIn

    def setAssetIdIn(self, newAssetIdIn):
        self.assetIdIn = newAssetIdIn

    def getAssetTypeEqual(self):
        return self.assetTypeEqual

    def setAssetTypeEqual(self, newAssetTypeEqual):
        self.assetTypeEqual = newAssetTypeEqual

    def getStartDateGreaterThanOrEqual(self):
        return self.startDateGreaterThanOrEqual

    def setStartDateGreaterThanOrEqual(self, newStartDateGreaterThanOrEqual):
        self.startDateGreaterThanOrEqual = newStartDateGreaterThanOrEqual

    def getEndDateGreaterThanOrEqual(self):
        return self.endDateGreaterThanOrEqual

    def setEndDateGreaterThanOrEqual(self, newEndDateGreaterThanOrEqual):
        self.endDateGreaterThanOrEqual = newEndDateGreaterThanOrEqual


# @package Kaltura
# @subpackage Client
class KalturaCDNPartnerSettings(KalturaObjectBase):
    def __init__(self,
            defaultAdapterId=NotImplemented,
            defaultRecordingAdapterId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Default CDN adapter identifier
        # @var int
        self.defaultAdapterId = defaultAdapterId

        # Default recording CDN adapter identifier
        # @var int
        self.defaultRecordingAdapterId = defaultRecordingAdapterId


    PROPERTY_LOADERS = {
        'defaultAdapterId': getXmlNodeInt, 
        'defaultRecordingAdapterId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCDNPartnerSettings.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCDNPartnerSettings")
        kparams.addIntIfDefined("defaultAdapterId", self.defaultAdapterId)
        kparams.addIntIfDefined("defaultRecordingAdapterId", self.defaultRecordingAdapterId)
        return kparams

    def getDefaultAdapterId(self):
        return self.defaultAdapterId

    def setDefaultAdapterId(self, newDefaultAdapterId):
        self.defaultAdapterId = newDefaultAdapterId

    def getDefaultRecordingAdapterId(self):
        return self.defaultRecordingAdapterId

    def setDefaultRecordingAdapterId(self, newDefaultRecordingAdapterId):
        self.defaultRecordingAdapterId = newDefaultRecordingAdapterId


# @package Kaltura
# @subpackage Client
class KalturaCompensation(KalturaObjectBase):
    """Compensation request parameters"""

    def __init__(self,
            id=NotImplemented,
            subscriptionId=NotImplemented,
            compensationType=NotImplemented,
            amount=NotImplemented,
            totalRenewalIterations=NotImplemented,
            appliedRenewalIterations=NotImplemented,
            purchaseId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Compensation identifier
        # @var int
        # @readonly
        self.id = id

        # Subscription identifier
        # @var int
        # @readonly
        self.subscriptionId = subscriptionId

        # Compensation type
        # @var KalturaCompensationType
        self.compensationType = compensationType

        # Compensation amount
        # @var float
        self.amount = amount

        # The number of renewals for compensation
        # @var int
        self.totalRenewalIterations = totalRenewalIterations

        # The number of renewals the compensation was already applied on
        # @var int
        # @readonly
        self.appliedRenewalIterations = appliedRenewalIterations

        # Purchase identifier
        # @var int
        self.purchaseId = purchaseId


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'subscriptionId': getXmlNodeInt, 
        'compensationType': (KalturaEnumsFactory.createString, "KalturaCompensationType"), 
        'amount': getXmlNodeFloat, 
        'totalRenewalIterations': getXmlNodeInt, 
        'appliedRenewalIterations': getXmlNodeInt, 
        'purchaseId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCompensation.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCompensation")
        kparams.addStringEnumIfDefined("compensationType", self.compensationType)
        kparams.addFloatIfDefined("amount", self.amount)
        kparams.addIntIfDefined("totalRenewalIterations", self.totalRenewalIterations)
        kparams.addIntIfDefined("purchaseId", self.purchaseId)
        return kparams

    def getId(self):
        return self.id

    def getSubscriptionId(self):
        return self.subscriptionId

    def getCompensationType(self):
        return self.compensationType

    def setCompensationType(self, newCompensationType):
        self.compensationType = newCompensationType

    def getAmount(self):
        return self.amount

    def setAmount(self, newAmount):
        self.amount = newAmount

    def getTotalRenewalIterations(self):
        return self.totalRenewalIterations

    def setTotalRenewalIterations(self, newTotalRenewalIterations):
        self.totalRenewalIterations = newTotalRenewalIterations

    def getAppliedRenewalIterations(self):
        return self.appliedRenewalIterations

    def getPurchaseId(self):
        return self.purchaseId

    def setPurchaseId(self, newPurchaseId):
        self.purchaseId = newPurchaseId


# @package Kaltura
# @subpackage Client
class KalturaKeyValue(KalturaObjectBase):
    def __init__(self,
            key=NotImplemented,
            value=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Key
        # @var string
        self.key = key

        # Value
        # @var string
        self.value = value


    PROPERTY_LOADERS = {
        'key': getXmlNodeText, 
        'value': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaKeyValue.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaKeyValue")
        kparams.addStringIfDefined("key", self.key)
        kparams.addStringIfDefined("value", self.value)
        return kparams

    def getKey(self):
        return self.key

    def setKey(self, newKey):
        self.key = newKey

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


# @package Kaltura
# @subpackage Client
class KalturaEmailMessage(KalturaObjectBase):
    def __init__(self,
            templateName=NotImplemented,
            subject=NotImplemented,
            firstName=NotImplemented,
            lastName=NotImplemented,
            senderName=NotImplemented,
            senderFrom=NotImplemented,
            senderTo=NotImplemented,
            bccAddress=NotImplemented,
            extraParameters=NotImplemented):
        KalturaObjectBase.__init__(self)

        # email template name
        # @var string
        self.templateName = templateName

        # email subject
        # @var string
        self.subject = subject

        # first name
        # @var string
        self.firstName = firstName

        # last name
        # @var string
        self.lastName = lastName

        # sender name
        # @var string
        self.senderName = senderName

        # sender from
        # @var string
        self.senderFrom = senderFrom

        # sender to
        # @var string
        self.senderTo = senderTo

        # bcc address - seperated by comma
        # @var string
        self.bccAddress = bccAddress

        # extra parameters
        # @var array of KalturaKeyValue
        self.extraParameters = extraParameters


    PROPERTY_LOADERS = {
        'templateName': getXmlNodeText, 
        'subject': getXmlNodeText, 
        'firstName': getXmlNodeText, 
        'lastName': getXmlNodeText, 
        'senderName': getXmlNodeText, 
        'senderFrom': getXmlNodeText, 
        'senderTo': getXmlNodeText, 
        'bccAddress': getXmlNodeText, 
        'extraParameters': (KalturaObjectFactory.createArray, 'KalturaKeyValue'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEmailMessage.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaEmailMessage")
        kparams.addStringIfDefined("templateName", self.templateName)
        kparams.addStringIfDefined("subject", self.subject)
        kparams.addStringIfDefined("firstName", self.firstName)
        kparams.addStringIfDefined("lastName", self.lastName)
        kparams.addStringIfDefined("senderName", self.senderName)
        kparams.addStringIfDefined("senderFrom", self.senderFrom)
        kparams.addStringIfDefined("senderTo", self.senderTo)
        kparams.addStringIfDefined("bccAddress", self.bccAddress)
        kparams.addArrayIfDefined("extraParameters", self.extraParameters)
        return kparams

    def getTemplateName(self):
        return self.templateName

    def setTemplateName(self, newTemplateName):
        self.templateName = newTemplateName

    def getSubject(self):
        return self.subject

    def setSubject(self, newSubject):
        self.subject = newSubject

    def getFirstName(self):
        return self.firstName

    def setFirstName(self, newFirstName):
        self.firstName = newFirstName

    def getLastName(self):
        return self.lastName

    def setLastName(self, newLastName):
        self.lastName = newLastName

    def getSenderName(self):
        return self.senderName

    def setSenderName(self, newSenderName):
        self.senderName = newSenderName

    def getSenderFrom(self):
        return self.senderFrom

    def setSenderFrom(self, newSenderFrom):
        self.senderFrom = newSenderFrom

    def getSenderTo(self):
        return self.senderTo

    def setSenderTo(self, newSenderTo):
        self.senderTo = newSenderTo

    def getBccAddress(self):
        return self.bccAddress

    def setBccAddress(self, newBccAddress):
        self.bccAddress = newBccAddress

    def getExtraParameters(self):
        return self.extraParameters

    def setExtraParameters(self, newExtraParameters):
        self.extraParameters = newExtraParameters


# @package Kaltura
# @subpackage Client
class KalturaEntitlementRenewalBase(KalturaObjectBase):
    def __init__(self,
            price=NotImplemented,
            purchaseId=NotImplemented,
            subscriptionId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Price that is going to be paid on the renewal
        # @var float
        self.price = price

        # Puchase ID
        # @var int
        self.purchaseId = purchaseId

        # Subscription ID
        # @var int
        self.subscriptionId = subscriptionId


    PROPERTY_LOADERS = {
        'price': getXmlNodeFloat, 
        'purchaseId': getXmlNodeInt, 
        'subscriptionId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEntitlementRenewalBase.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaEntitlementRenewalBase")
        kparams.addFloatIfDefined("price", self.price)
        kparams.addIntIfDefined("purchaseId", self.purchaseId)
        kparams.addIntIfDefined("subscriptionId", self.subscriptionId)
        return kparams

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getPurchaseId(self):
        return self.purchaseId

    def setPurchaseId(self, newPurchaseId):
        self.purchaseId = newPurchaseId

    def getSubscriptionId(self):
        return self.subscriptionId

    def setSubscriptionId(self, newSubscriptionId):
        self.subscriptionId = newSubscriptionId


# @package Kaltura
# @subpackage Client
class KalturaUnifiedPaymentRenewal(KalturaObjectBase):
    def __init__(self,
            price=NotImplemented,
            date=NotImplemented,
            unifiedPaymentId=NotImplemented,
            entitlements=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Price that is going to be paid on the renewal
        # @var KalturaPrice
        self.price = price

        # Next renewal date
        # @var int
        self.date = date

        # Unified payment ID
        # @var int
        self.unifiedPaymentId = unifiedPaymentId

        # List of entitlements in this unified payment renewal
        # @var array of KalturaEntitlementRenewalBase
        self.entitlements = entitlements


    PROPERTY_LOADERS = {
        'price': (KalturaObjectFactory.create, 'KalturaPrice'), 
        'date': getXmlNodeInt, 
        'unifiedPaymentId': getXmlNodeInt, 
        'entitlements': (KalturaObjectFactory.createArray, 'KalturaEntitlementRenewalBase'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUnifiedPaymentRenewal.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUnifiedPaymentRenewal")
        kparams.addObjectIfDefined("price", self.price)
        kparams.addIntIfDefined("date", self.date)
        kparams.addIntIfDefined("unifiedPaymentId", self.unifiedPaymentId)
        kparams.addArrayIfDefined("entitlements", self.entitlements)
        return kparams

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getDate(self):
        return self.date

    def setDate(self, newDate):
        self.date = newDate

    def getUnifiedPaymentId(self):
        return self.unifiedPaymentId

    def setUnifiedPaymentId(self, newUnifiedPaymentId):
        self.unifiedPaymentId = newUnifiedPaymentId

    def getEntitlements(self):
        return self.entitlements

    def setEntitlements(self, newEntitlements):
        self.entitlements = newEntitlements


# @package Kaltura
# @subpackage Client
class KalturaNetworkActionStatus(KalturaObjectBase):
    def __init__(self,
            status=NotImplemented,
            network=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Status
        # @var KalturaSocialStatus
        self.status = status

        # Social network
        # @var KalturaSocialNetwork
        self.network = network


    PROPERTY_LOADERS = {
        'status': (KalturaEnumsFactory.createString, "KalturaSocialStatus"), 
        'network': (KalturaEnumsFactory.createString, "KalturaSocialNetwork"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaNetworkActionStatus.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaNetworkActionStatus")
        kparams.addStringEnumIfDefined("status", self.status)
        kparams.addStringEnumIfDefined("network", self.network)
        return kparams

    def getStatus(self):
        return self.status

    def setStatus(self, newStatus):
        self.status = newStatus

    def getNetwork(self):
        return self.network

    def setNetwork(self, newNetwork):
        self.network = newNetwork


# @package Kaltura
# @subpackage Client
class KalturaUserSocialActionResponse(KalturaObjectBase):
    def __init__(self,
            socialAction=NotImplemented,
            failStatus=NotImplemented):
        KalturaObjectBase.__init__(self)

        # socialAction
        # @var KalturaSocialAction
        self.socialAction = socialAction

        # List of action permission items
        # @var array of KalturaNetworkActionStatus
        self.failStatus = failStatus


    PROPERTY_LOADERS = {
        'socialAction': (KalturaObjectFactory.create, 'KalturaSocialAction'), 
        'failStatus': (KalturaObjectFactory.createArray, 'KalturaNetworkActionStatus'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserSocialActionResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserSocialActionResponse")
        kparams.addObjectIfDefined("socialAction", self.socialAction)
        kparams.addArrayIfDefined("failStatus", self.failStatus)
        return kparams

    def getSocialAction(self):
        return self.socialAction

    def setSocialAction(self, newSocialAction):
        self.socialAction = newSocialAction

    def getFailStatus(self):
        return self.failStatus

    def setFailStatus(self, newFailStatus):
        self.failStatus = newFailStatus


# @package Kaltura
# @subpackage Client
class KalturaPaymentGatewayConfiguration(KalturaObjectBase):
    def __init__(self,
            paymentGatewayConfiguration=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Payment gateway configuration
        # @var array of KalturaKeyValue
        self.paymentGatewayConfiguration = paymentGatewayConfiguration


    PROPERTY_LOADERS = {
        'paymentGatewayConfiguration': (KalturaObjectFactory.createArray, 'KalturaKeyValue'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPaymentGatewayConfiguration.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPaymentGatewayConfiguration")
        kparams.addArrayIfDefined("paymentGatewayConfiguration", self.paymentGatewayConfiguration)
        return kparams

    def getPaymentGatewayConfiguration(self):
        return self.paymentGatewayConfiguration

    def setPaymentGatewayConfiguration(self, newPaymentGatewayConfiguration):
        self.paymentGatewayConfiguration = newPaymentGatewayConfiguration


# @package Kaltura
# @subpackage Client
class KalturaHouseholdQuota(KalturaObjectBase):
    def __init__(self,
            householdId=NotImplemented,
            totalQuota=NotImplemented,
            availableQuota=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Household identifier
        # @var int
        # @readonly
        self.householdId = householdId

        # Total quota that is allocated to the household
        # @var int
        # @readonly
        self.totalQuota = totalQuota

        # Available quota that household has remaining
        # @var int
        # @readonly
        self.availableQuota = availableQuota


    PROPERTY_LOADERS = {
        'householdId': getXmlNodeInt, 
        'totalQuota': getXmlNodeInt, 
        'availableQuota': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdQuota.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdQuota")
        return kparams

    def getHouseholdId(self):
        return self.householdId

    def getTotalQuota(self):
        return self.totalQuota

    def getAvailableQuota(self):
        return self.availableQuota


# @package Kaltura
# @subpackage Client
class KalturaMessageTemplate(KalturaObjectBase):
    def __init__(self,
            message=NotImplemented,
            dateFormat=NotImplemented,
            messageType=NotImplemented,
            sound=NotImplemented,
            action=NotImplemented,
            url=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The message template with placeholders
        # @var string
        self.message = message

        # Default date format for the date &amp; time entries used in the template
        # @var string
        self.dateFormat = dateFormat

        # Template type. Possible values: Series, Reminder,Churn, SeriesReminder
        # @var KalturaMessageTemplateType
        self.messageType = messageType

        # Sound file name to play upon message arrival to the device (if supported by target device)
        # @var string
        self.sound = sound

        # an optional action
        # @var string
        self.action = action

        # URL template for deep linking. Example - /app/location/{mediaId}
        # @var string
        self.url = url


    PROPERTY_LOADERS = {
        'message': getXmlNodeText, 
        'dateFormat': getXmlNodeText, 
        'messageType': (KalturaEnumsFactory.createString, "KalturaMessageTemplateType"), 
        'sound': getXmlNodeText, 
        'action': getXmlNodeText, 
        'url': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaMessageTemplate.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaMessageTemplate")
        kparams.addStringIfDefined("message", self.message)
        kparams.addStringIfDefined("dateFormat", self.dateFormat)
        kparams.addStringEnumIfDefined("messageType", self.messageType)
        kparams.addStringIfDefined("sound", self.sound)
        kparams.addStringIfDefined("action", self.action)
        kparams.addStringIfDefined("url", self.url)
        return kparams

    def getMessage(self):
        return self.message

    def setMessage(self, newMessage):
        self.message = newMessage

    def getDateFormat(self):
        return self.dateFormat

    def setDateFormat(self, newDateFormat):
        self.dateFormat = newDateFormat

    def getMessageType(self):
        return self.messageType

    def setMessageType(self, newMessageType):
        self.messageType = newMessageType

    def getSound(self):
        return self.sound

    def setSound(self, newSound):
        self.sound = newSound

    def getAction(self):
        return self.action

    def setAction(self, newAction):
        self.action = newAction

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl


# @package Kaltura
# @subpackage Client
class KalturaPpv(KalturaObjectBase):
    """PPV details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            price=NotImplemented,
            fileTypes=NotImplemented,
            discountModule=NotImplemented,
            couponsGroup=NotImplemented,
            descriptions=NotImplemented,
            productCode=NotImplemented,
            isSubscriptionOnly=NotImplemented,
            firstDeviceLimitation=NotImplemented,
            usageModule=NotImplemented):
        KalturaObjectBase.__init__(self)

        # PPV identifier
        # @var string
        self.id = id

        # the name for the ppv
        # @var string
        self.name = name

        # The price of the ppv
        # @var KalturaPriceDetails
        self.price = price

        # A list of file types identifiers that are supported in this ppv
        # @var array of KalturaIntegerValue
        self.fileTypes = fileTypes

        # The internal discount module for the ppv
        # @var KalturaDiscountModule
        self.discountModule = discountModule

        # Coupons group for the ppv
        # @var KalturaCouponsGroup
        self.couponsGroup = couponsGroup

        # A list of the descriptions of the ppv on different languages (language code and translation)
        # @var array of KalturaTranslationToken
        self.descriptions = descriptions

        # Product code for the ppv
        # @var string
        self.productCode = productCode

        # Indicates whether or not this ppv can be purchased standalone or only as part of a subscription
        # @var bool
        self.isSubscriptionOnly = isSubscriptionOnly

        # Indicates whether or not this ppv can be consumed only on the first device
        # @var bool
        self.firstDeviceLimitation = firstDeviceLimitation

        # PPV usage module
        # @var KalturaUsageModule
        self.usageModule = usageModule


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
        'price': (KalturaObjectFactory.create, 'KalturaPriceDetails'), 
        'fileTypes': (KalturaObjectFactory.createArray, 'KalturaIntegerValue'), 
        'discountModule': (KalturaObjectFactory.create, 'KalturaDiscountModule'), 
        'couponsGroup': (KalturaObjectFactory.create, 'KalturaCouponsGroup'), 
        'descriptions': (KalturaObjectFactory.createArray, 'KalturaTranslationToken'), 
        'productCode': getXmlNodeText, 
        'isSubscriptionOnly': getXmlNodeBool, 
        'firstDeviceLimitation': getXmlNodeBool, 
        'usageModule': (KalturaObjectFactory.create, 'KalturaUsageModule'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPpv.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPpv")
        kparams.addStringIfDefined("id", self.id)
        kparams.addStringIfDefined("name", self.name)
        kparams.addObjectIfDefined("price", self.price)
        kparams.addArrayIfDefined("fileTypes", self.fileTypes)
        kparams.addObjectIfDefined("discountModule", self.discountModule)
        kparams.addObjectIfDefined("couponsGroup", self.couponsGroup)
        kparams.addArrayIfDefined("descriptions", self.descriptions)
        kparams.addStringIfDefined("productCode", self.productCode)
        kparams.addBoolIfDefined("isSubscriptionOnly", self.isSubscriptionOnly)
        kparams.addBoolIfDefined("firstDeviceLimitation", self.firstDeviceLimitation)
        kparams.addObjectIfDefined("usageModule", self.usageModule)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getFileTypes(self):
        return self.fileTypes

    def setFileTypes(self, newFileTypes):
        self.fileTypes = newFileTypes

    def getDiscountModule(self):
        return self.discountModule

    def setDiscountModule(self, newDiscountModule):
        self.discountModule = newDiscountModule

    def getCouponsGroup(self):
        return self.couponsGroup

    def setCouponsGroup(self, newCouponsGroup):
        self.couponsGroup = newCouponsGroup

    def getDescriptions(self):
        return self.descriptions

    def setDescriptions(self, newDescriptions):
        self.descriptions = newDescriptions

    def getProductCode(self):
        return self.productCode

    def setProductCode(self, newProductCode):
        self.productCode = newProductCode

    def getIsSubscriptionOnly(self):
        return self.isSubscriptionOnly

    def setIsSubscriptionOnly(self, newIsSubscriptionOnly):
        self.isSubscriptionOnly = newIsSubscriptionOnly

    def getFirstDeviceLimitation(self):
        return self.firstDeviceLimitation

    def setFirstDeviceLimitation(self, newFirstDeviceLimitation):
        self.firstDeviceLimitation = newFirstDeviceLimitation

    def getUsageModule(self):
        return self.usageModule

    def setUsageModule(self, newUsageModule):
        self.usageModule = newUsageModule


# @package Kaltura
# @subpackage Client
class KalturaLicensedUrl(KalturaObjectBase):
    def __init__(self,
            mainUrl=NotImplemented,
            altUrl=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Main licensed URL
        # @var string
        self.mainUrl = mainUrl

        # An alternate URL to use in case the main fails
        # @var string
        self.altUrl = altUrl


    PROPERTY_LOADERS = {
        'mainUrl': getXmlNodeText, 
        'altUrl': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLicensedUrl.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaLicensedUrl")
        kparams.addStringIfDefined("mainUrl", self.mainUrl)
        kparams.addStringIfDefined("altUrl", self.altUrl)
        return kparams

    def getMainUrl(self):
        return self.mainUrl

    def setMainUrl(self, newMainUrl):
        self.mainUrl = newMainUrl

    def getAltUrl(self):
        return self.altUrl

    def setAltUrl(self, newAltUrl):
        self.altUrl = newAltUrl


# @package Kaltura
# @subpackage Client
class KalturaLicensedUrlBaseRequest(KalturaObjectBase):
    def __init__(self,
            assetId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Asset identifier
        # @var string
        self.assetId = assetId


    PROPERTY_LOADERS = {
        'assetId': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLicensedUrlBaseRequest.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaLicensedUrlBaseRequest")
        kparams.addStringIfDefined("assetId", self.assetId)
        return kparams

    def getAssetId(self):
        return self.assetId

    def setAssetId(self, newAssetId):
        self.assetId = newAssetId


# @package Kaltura
# @subpackage Client
class KalturaLicensedUrlMediaRequest(KalturaLicensedUrlBaseRequest):
    def __init__(self,
            assetId=NotImplemented,
            contentId=NotImplemented,
            baseUrl=NotImplemented):
        KalturaLicensedUrlBaseRequest.__init__(self,
            assetId)

        # Identifier of the content to get the link for (file identifier)
        # @var int
        self.contentId = contentId

        # Base URL for the licensed URLs
        # @var string
        self.baseUrl = baseUrl


    PROPERTY_LOADERS = {
        'contentId': getXmlNodeInt, 
        'baseUrl': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaLicensedUrlBaseRequest.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLicensedUrlMediaRequest.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaLicensedUrlBaseRequest.toParams(self)
        kparams.put("objectType", "KalturaLicensedUrlMediaRequest")
        kparams.addIntIfDefined("contentId", self.contentId)
        kparams.addStringIfDefined("baseUrl", self.baseUrl)
        return kparams

    def getContentId(self):
        return self.contentId

    def setContentId(self, newContentId):
        self.contentId = newContentId

    def getBaseUrl(self):
        return self.baseUrl

    def setBaseUrl(self, newBaseUrl):
        self.baseUrl = newBaseUrl


# @package Kaltura
# @subpackage Client
class KalturaLicensedUrlEpgRequest(KalturaLicensedUrlMediaRequest):
    def __init__(self,
            assetId=NotImplemented,
            contentId=NotImplemented,
            baseUrl=NotImplemented,
            streamType=NotImplemented,
            startDate=NotImplemented):
        KalturaLicensedUrlMediaRequest.__init__(self,
            assetId,
            contentId,
            baseUrl)

        # The stream type to get the URL for
        # @var KalturaStreamType
        self.streamType = streamType

        # The start date of the stream (epoch)
        # @var int
        self.startDate = startDate


    PROPERTY_LOADERS = {
        'streamType': (KalturaEnumsFactory.createString, "KalturaStreamType"), 
        'startDate': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaLicensedUrlMediaRequest.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLicensedUrlEpgRequest.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaLicensedUrlMediaRequest.toParams(self)
        kparams.put("objectType", "KalturaLicensedUrlEpgRequest")
        kparams.addStringEnumIfDefined("streamType", self.streamType)
        kparams.addIntIfDefined("startDate", self.startDate)
        return kparams

    def getStreamType(self):
        return self.streamType

    def setStreamType(self, newStreamType):
        self.streamType = newStreamType

    def getStartDate(self):
        return self.startDate

    def setStartDate(self, newStartDate):
        self.startDate = newStartDate


# @package Kaltura
# @subpackage Client
class KalturaLicensedUrlRecordingRequest(KalturaLicensedUrlBaseRequest):
    def __init__(self,
            assetId=NotImplemented,
            fileType=NotImplemented):
        KalturaLicensedUrlBaseRequest.__init__(self,
            assetId)

        # The file type for the URL
        # @var string
        self.fileType = fileType


    PROPERTY_LOADERS = {
        'fileType': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaLicensedUrlBaseRequest.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLicensedUrlRecordingRequest.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaLicensedUrlBaseRequest.toParams(self)
        kparams.put("objectType", "KalturaLicensedUrlRecordingRequest")
        kparams.addStringIfDefined("fileType", self.fileType)
        return kparams

    def getFileType(self):
        return self.fileType

    def setFileType(self, newFileType):
        self.fileType = newFileType


# @package Kaltura
# @subpackage Client
class KalturaRegistryResponse(KalturaObjectBase):
    def __init__(self,
            announcementId=NotImplemented,
            key=NotImplemented,
            url=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Announcement Id
        # @var int
        self.announcementId = announcementId

        # Key
        # @var string
        self.key = key

        # URL
        # @var string
        self.url = url


    PROPERTY_LOADERS = {
        'announcementId': getXmlNodeInt, 
        'key': getXmlNodeText, 
        'url': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaRegistryResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaRegistryResponse")
        kparams.addIntIfDefined("announcementId", self.announcementId)
        kparams.addStringIfDefined("key", self.key)
        kparams.addStringIfDefined("url", self.url)
        return kparams

    def getAnnouncementId(self):
        return self.announcementId

    def setAnnouncementId(self, newAnnouncementId):
        self.announcementId = newAnnouncementId

    def getKey(self):
        return self.key

    def setKey(self, newKey):
        self.key = newKey

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl


# @package Kaltura
# @subpackage Client
class KalturaPushMessage(KalturaObjectBase):
    def __init__(self,
            message=NotImplemented,
            sound=NotImplemented,
            action=NotImplemented,
            url=NotImplemented):
        KalturaObjectBase.__init__(self)

        # The message that will be presented to the user.
        # @var string
        self.message = message

        # Optional. Can be used to change the default push sound on the user device.
        # @var string
        self.sound = sound

        # Optional. Used to change the default action of the application when a push is received.
        # @var string
        self.action = action

        # Optional. Used to direct the application to the relevant page.
        # @var string
        self.url = url


    PROPERTY_LOADERS = {
        'message': getXmlNodeText, 
        'sound': getXmlNodeText, 
        'action': getXmlNodeText, 
        'url': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPushMessage.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPushMessage")
        kparams.addStringIfDefined("message", self.message)
        kparams.addStringIfDefined("sound", self.sound)
        kparams.addStringIfDefined("action", self.action)
        kparams.addStringIfDefined("url", self.url)
        return kparams

    def getMessage(self):
        return self.message

    def setMessage(self, newMessage):
        self.message = newMessage

    def getSound(self):
        return self.sound

    def setSound(self, newSound):
        self.sound = newSound

    def getAction(self):
        return self.action

    def setAction(self, newAction):
        self.action = newAction

    def getUrl(self):
        return self.url

    def setUrl(self, newUrl):
        self.url = newUrl


# @package Kaltura
# @subpackage Client
class KalturaNotificationsPartnerSettings(KalturaObjectBase):
    def __init__(self,
            pushNotificationEnabled=NotImplemented,
            pushSystemAnnouncementsEnabled=NotImplemented,
            pushStartHour=NotImplemented,
            pushEndHour=NotImplemented,
            inboxEnabled=NotImplemented,
            messageTTLDays=NotImplemented,
            automaticIssueFollowNotification=NotImplemented,
            topicExpirationDurationDays=NotImplemented,
            reminderEnabled=NotImplemented,
            reminderOffsetSec=NotImplemented,
            pushAdapterUrl=NotImplemented,
            churnMailTemplateName=NotImplemented,
            churnMailSubject=NotImplemented,
            senderEmail=NotImplemented,
            mailSenderName=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Push notification capability is enabled for the account
        # @var bool
        self.pushNotificationEnabled = pushNotificationEnabled

        # System announcement capability is enabled for the account
        # @var bool
        self.pushSystemAnnouncementsEnabled = pushSystemAnnouncementsEnabled

        # Window start time (UTC) for send automated push messages
        # @var int
        self.pushStartHour = pushStartHour

        # Window end time (UTC) for send automated push messages
        # @var int
        self.pushEndHour = pushEndHour

        # Inbox enabled
        # @var bool
        self.inboxEnabled = inboxEnabled

        # Message TTL in days
        # @var int
        self.messageTTLDays = messageTTLDays

        # Automatic issue follow notification
        # @var bool
        self.automaticIssueFollowNotification = automaticIssueFollowNotification

        # Topic expiration duration in days
        # @var int
        self.topicExpirationDurationDays = topicExpirationDurationDays

        # Reminder enabled
        # @var bool
        self.reminderEnabled = reminderEnabled

        # Offset time (UTC) in seconds for send reminder
        # @var int
        self.reminderOffsetSec = reminderOffsetSec

        # Push adapter URL
        # @var string
        self.pushAdapterUrl = pushAdapterUrl

        # Churn mail template name
        # @var string
        self.churnMailTemplateName = churnMailTemplateName

        # Churn mail subject
        # @var string
        self.churnMailSubject = churnMailSubject

        # Sender email
        # @var string
        self.senderEmail = senderEmail

        # Mail sender name
        # @var string
        self.mailSenderName = mailSenderName


    PROPERTY_LOADERS = {
        'pushNotificationEnabled': getXmlNodeBool, 
        'pushSystemAnnouncementsEnabled': getXmlNodeBool, 
        'pushStartHour': getXmlNodeInt, 
        'pushEndHour': getXmlNodeInt, 
        'inboxEnabled': getXmlNodeBool, 
        'messageTTLDays': getXmlNodeInt, 
        'automaticIssueFollowNotification': getXmlNodeBool, 
        'topicExpirationDurationDays': getXmlNodeInt, 
        'reminderEnabled': getXmlNodeBool, 
        'reminderOffsetSec': getXmlNodeInt, 
        'pushAdapterUrl': getXmlNodeText, 
        'churnMailTemplateName': getXmlNodeText, 
        'churnMailSubject': getXmlNodeText, 
        'senderEmail': getXmlNodeText, 
        'mailSenderName': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaNotificationsPartnerSettings.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaNotificationsPartnerSettings")
        kparams.addBoolIfDefined("pushNotificationEnabled", self.pushNotificationEnabled)
        kparams.addBoolIfDefined("pushSystemAnnouncementsEnabled", self.pushSystemAnnouncementsEnabled)
        kparams.addIntIfDefined("pushStartHour", self.pushStartHour)
        kparams.addIntIfDefined("pushEndHour", self.pushEndHour)
        kparams.addBoolIfDefined("inboxEnabled", self.inboxEnabled)
        kparams.addIntIfDefined("messageTTLDays", self.messageTTLDays)
        kparams.addBoolIfDefined("automaticIssueFollowNotification", self.automaticIssueFollowNotification)
        kparams.addIntIfDefined("topicExpirationDurationDays", self.topicExpirationDurationDays)
        kparams.addBoolIfDefined("reminderEnabled", self.reminderEnabled)
        kparams.addIntIfDefined("reminderOffsetSec", self.reminderOffsetSec)
        kparams.addStringIfDefined("pushAdapterUrl", self.pushAdapterUrl)
        kparams.addStringIfDefined("churnMailTemplateName", self.churnMailTemplateName)
        kparams.addStringIfDefined("churnMailSubject", self.churnMailSubject)
        kparams.addStringIfDefined("senderEmail", self.senderEmail)
        kparams.addStringIfDefined("mailSenderName", self.mailSenderName)
        return kparams

    def getPushNotificationEnabled(self):
        return self.pushNotificationEnabled

    def setPushNotificationEnabled(self, newPushNotificationEnabled):
        self.pushNotificationEnabled = newPushNotificationEnabled

    def getPushSystemAnnouncementsEnabled(self):
        return self.pushSystemAnnouncementsEnabled

    def setPushSystemAnnouncementsEnabled(self, newPushSystemAnnouncementsEnabled):
        self.pushSystemAnnouncementsEnabled = newPushSystemAnnouncementsEnabled

    def getPushStartHour(self):
        return self.pushStartHour

    def setPushStartHour(self, newPushStartHour):
        self.pushStartHour = newPushStartHour

    def getPushEndHour(self):
        return self.pushEndHour

    def setPushEndHour(self, newPushEndHour):
        self.pushEndHour = newPushEndHour

    def getInboxEnabled(self):
        return self.inboxEnabled

    def setInboxEnabled(self, newInboxEnabled):
        self.inboxEnabled = newInboxEnabled

    def getMessageTTLDays(self):
        return self.messageTTLDays

    def setMessageTTLDays(self, newMessageTTLDays):
        self.messageTTLDays = newMessageTTLDays

    def getAutomaticIssueFollowNotification(self):
        return self.automaticIssueFollowNotification

    def setAutomaticIssueFollowNotification(self, newAutomaticIssueFollowNotification):
        self.automaticIssueFollowNotification = newAutomaticIssueFollowNotification

    def getTopicExpirationDurationDays(self):
        return self.topicExpirationDurationDays

    def setTopicExpirationDurationDays(self, newTopicExpirationDurationDays):
        self.topicExpirationDurationDays = newTopicExpirationDurationDays

    def getReminderEnabled(self):
        return self.reminderEnabled

    def setReminderEnabled(self, newReminderEnabled):
        self.reminderEnabled = newReminderEnabled

    def getReminderOffsetSec(self):
        return self.reminderOffsetSec

    def setReminderOffsetSec(self, newReminderOffsetSec):
        self.reminderOffsetSec = newReminderOffsetSec

    def getPushAdapterUrl(self):
        return self.pushAdapterUrl

    def setPushAdapterUrl(self, newPushAdapterUrl):
        self.pushAdapterUrl = newPushAdapterUrl

    def getChurnMailTemplateName(self):
        return self.churnMailTemplateName

    def setChurnMailTemplateName(self, newChurnMailTemplateName):
        self.churnMailTemplateName = newChurnMailTemplateName

    def getChurnMailSubject(self):
        return self.churnMailSubject

    def setChurnMailSubject(self, newChurnMailSubject):
        self.churnMailSubject = newChurnMailSubject

    def getSenderEmail(self):
        return self.senderEmail

    def setSenderEmail(self, newSenderEmail):
        self.senderEmail = newSenderEmail

    def getMailSenderName(self):
        return self.mailSenderName

    def setMailSenderName(self, newMailSenderName):
        self.mailSenderName = newMailSenderName


# @package Kaltura
# @subpackage Client
class KalturaNotificationsSettings(KalturaObjectBase):
    def __init__(self,
            pushNotificationEnabled=NotImplemented,
            pushFollowEnabled=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Specify if the user want to receive push notifications or not
        # @var bool
        self.pushNotificationEnabled = pushNotificationEnabled

        # Specify if the user will be notified for followed content via push. (requires push_notification_enabled to be enabled)
        # @var bool
        self.pushFollowEnabled = pushFollowEnabled


    PROPERTY_LOADERS = {
        'pushNotificationEnabled': getXmlNodeBool, 
        'pushFollowEnabled': getXmlNodeBool, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaNotificationsSettings.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaNotificationsSettings")
        kparams.addBoolIfDefined("pushNotificationEnabled", self.pushNotificationEnabled)
        kparams.addBoolIfDefined("pushFollowEnabled", self.pushFollowEnabled)
        return kparams

    def getPushNotificationEnabled(self):
        return self.pushNotificationEnabled

    def setPushNotificationEnabled(self, newPushNotificationEnabled):
        self.pushNotificationEnabled = newPushNotificationEnabled

    def getPushFollowEnabled(self):
        return self.pushFollowEnabled

    def setPushFollowEnabled(self, newPushFollowEnabled):
        self.pushFollowEnabled = newPushFollowEnabled


# @package Kaltura
# @subpackage Client
class KalturaTimeShiftedTvPartnerSettings(KalturaObjectBase):
    def __init__(self,
            catchUpEnabled=NotImplemented,
            cdvrEnabled=NotImplemented,
            startOverEnabled=NotImplemented,
            trickPlayEnabled=NotImplemented,
            recordingScheduleWindowEnabled=NotImplemented,
            protectionEnabled=NotImplemented,
            catchUpBufferLength=NotImplemented,
            trickPlayBufferLength=NotImplemented,
            recordingScheduleWindow=NotImplemented,
            paddingBeforeProgramStarts=NotImplemented,
            paddingAfterProgramEnds=NotImplemented,
            protectionPeriod=NotImplemented,
            protectionQuotaPercentage=NotImplemented,
            recordingLifetimePeriod=NotImplemented,
            cleanupNoticePeriod=NotImplemented,
            seriesRecordingEnabled=NotImplemented,
            nonEntitledChannelPlaybackEnabled=NotImplemented,
            nonExistingChannelPlaybackEnabled=NotImplemented,
            quotaOveragePolicy=NotImplemented,
            protectionPolicy=NotImplemented,
            recoveryGracePeriod=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Is catch-up enabled
        # @var bool
        self.catchUpEnabled = catchUpEnabled

        # Is c-dvr enabled
        # @var bool
        self.cdvrEnabled = cdvrEnabled

        # Is start-over enabled
        # @var bool
        self.startOverEnabled = startOverEnabled

        # Is trick-play enabled
        # @var bool
        self.trickPlayEnabled = trickPlayEnabled

        # Is recording schedule window enabled
        # @var bool
        self.recordingScheduleWindowEnabled = recordingScheduleWindowEnabled

        # Is recording protection enabled
        # @var bool
        self.protectionEnabled = protectionEnabled

        # Catch-up buffer length
        # @var int
        self.catchUpBufferLength = catchUpBufferLength

        # Trick play buffer length
        # @var int
        self.trickPlayBufferLength = trickPlayBufferLength

        # Recording schedule window. Indicates how long (in minutes) after the program starts it is allowed to schedule the recording
        # @var int
        self.recordingScheduleWindow = recordingScheduleWindow

        # Indicates how long (in seconds) before the program starts the recording will begin
        # @var int
        self.paddingBeforeProgramStarts = paddingBeforeProgramStarts

        # Indicates how long (in seconds) after the program ends the recording will end
        # @var int
        self.paddingAfterProgramEnds = paddingAfterProgramEnds

        # Specify the time in days that a recording should be protected. Start time begins at protection request.
        # @var int
        self.protectionPeriod = protectionPeriod

        # Indicates how many percent of the quota can be used for protection
        # @var int
        self.protectionQuotaPercentage = protectionQuotaPercentage

        # Specify the time in days that a recording should be kept for user. Start time begins with the program end date.
        # @var int
        self.recordingLifetimePeriod = recordingLifetimePeriod

        # The time in days before the recording lifetime is due from which the client should be able to warn user about deletion.
        # @var int
        self.cleanupNoticePeriod = cleanupNoticePeriod

        # Is recording of series enabled
        # @var bool
        self.seriesRecordingEnabled = seriesRecordingEnabled

        # Is recording playback for non-entitled channel enables
        # @var bool
        self.nonEntitledChannelPlaybackEnabled = nonEntitledChannelPlaybackEnabled

        # Is recording playback for non-existing channel enables
        # @var bool
        self.nonExistingChannelPlaybackEnabled = nonExistingChannelPlaybackEnabled

        # Quota Policy
        # @var KalturaQuotaOveragePolicy
        self.quotaOveragePolicy = quotaOveragePolicy

        # Protection Policy
        # @var KalturaProtectionPolicy
        self.protectionPolicy = protectionPolicy

        # The time in days for recovery recording that was delete by Auto Delete .
        # @var int
        self.recoveryGracePeriod = recoveryGracePeriod


    PROPERTY_LOADERS = {
        'catchUpEnabled': getXmlNodeBool, 
        'cdvrEnabled': getXmlNodeBool, 
        'startOverEnabled': getXmlNodeBool, 
        'trickPlayEnabled': getXmlNodeBool, 
        'recordingScheduleWindowEnabled': getXmlNodeBool, 
        'protectionEnabled': getXmlNodeBool, 
        'catchUpBufferLength': getXmlNodeInt, 
        'trickPlayBufferLength': getXmlNodeInt, 
        'recordingScheduleWindow': getXmlNodeInt, 
        'paddingBeforeProgramStarts': getXmlNodeInt, 
        'paddingAfterProgramEnds': getXmlNodeInt, 
        'protectionPeriod': getXmlNodeInt, 
        'protectionQuotaPercentage': getXmlNodeInt, 
        'recordingLifetimePeriod': getXmlNodeInt, 
        'cleanupNoticePeriod': getXmlNodeInt, 
        'seriesRecordingEnabled': getXmlNodeBool, 
        'nonEntitledChannelPlaybackEnabled': getXmlNodeBool, 
        'nonExistingChannelPlaybackEnabled': getXmlNodeBool, 
        'quotaOveragePolicy': (KalturaEnumsFactory.createString, "KalturaQuotaOveragePolicy"), 
        'protectionPolicy': (KalturaEnumsFactory.createString, "KalturaProtectionPolicy"), 
        'recoveryGracePeriod': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTimeShiftedTvPartnerSettings.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaTimeShiftedTvPartnerSettings")
        kparams.addBoolIfDefined("catchUpEnabled", self.catchUpEnabled)
        kparams.addBoolIfDefined("cdvrEnabled", self.cdvrEnabled)
        kparams.addBoolIfDefined("startOverEnabled", self.startOverEnabled)
        kparams.addBoolIfDefined("trickPlayEnabled", self.trickPlayEnabled)
        kparams.addBoolIfDefined("recordingScheduleWindowEnabled", self.recordingScheduleWindowEnabled)
        kparams.addBoolIfDefined("protectionEnabled", self.protectionEnabled)
        kparams.addIntIfDefined("catchUpBufferLength", self.catchUpBufferLength)
        kparams.addIntIfDefined("trickPlayBufferLength", self.trickPlayBufferLength)
        kparams.addIntIfDefined("recordingScheduleWindow", self.recordingScheduleWindow)
        kparams.addIntIfDefined("paddingBeforeProgramStarts", self.paddingBeforeProgramStarts)
        kparams.addIntIfDefined("paddingAfterProgramEnds", self.paddingAfterProgramEnds)
        kparams.addIntIfDefined("protectionPeriod", self.protectionPeriod)
        kparams.addIntIfDefined("protectionQuotaPercentage", self.protectionQuotaPercentage)
        kparams.addIntIfDefined("recordingLifetimePeriod", self.recordingLifetimePeriod)
        kparams.addIntIfDefined("cleanupNoticePeriod", self.cleanupNoticePeriod)
        kparams.addBoolIfDefined("seriesRecordingEnabled", self.seriesRecordingEnabled)
        kparams.addBoolIfDefined("nonEntitledChannelPlaybackEnabled", self.nonEntitledChannelPlaybackEnabled)
        kparams.addBoolIfDefined("nonExistingChannelPlaybackEnabled", self.nonExistingChannelPlaybackEnabled)
        kparams.addStringEnumIfDefined("quotaOveragePolicy", self.quotaOveragePolicy)
        kparams.addStringEnumIfDefined("protectionPolicy", self.protectionPolicy)
        kparams.addIntIfDefined("recoveryGracePeriod", self.recoveryGracePeriod)
        return kparams

    def getCatchUpEnabled(self):
        return self.catchUpEnabled

    def setCatchUpEnabled(self, newCatchUpEnabled):
        self.catchUpEnabled = newCatchUpEnabled

    def getCdvrEnabled(self):
        return self.cdvrEnabled

    def setCdvrEnabled(self, newCdvrEnabled):
        self.cdvrEnabled = newCdvrEnabled

    def getStartOverEnabled(self):
        return self.startOverEnabled

    def setStartOverEnabled(self, newStartOverEnabled):
        self.startOverEnabled = newStartOverEnabled

    def getTrickPlayEnabled(self):
        return self.trickPlayEnabled

    def setTrickPlayEnabled(self, newTrickPlayEnabled):
        self.trickPlayEnabled = newTrickPlayEnabled

    def getRecordingScheduleWindowEnabled(self):
        return self.recordingScheduleWindowEnabled

    def setRecordingScheduleWindowEnabled(self, newRecordingScheduleWindowEnabled):
        self.recordingScheduleWindowEnabled = newRecordingScheduleWindowEnabled

    def getProtectionEnabled(self):
        return self.protectionEnabled

    def setProtectionEnabled(self, newProtectionEnabled):
        self.protectionEnabled = newProtectionEnabled

    def getCatchUpBufferLength(self):
        return self.catchUpBufferLength

    def setCatchUpBufferLength(self, newCatchUpBufferLength):
        self.catchUpBufferLength = newCatchUpBufferLength

    def getTrickPlayBufferLength(self):
        return self.trickPlayBufferLength

    def setTrickPlayBufferLength(self, newTrickPlayBufferLength):
        self.trickPlayBufferLength = newTrickPlayBufferLength

    def getRecordingScheduleWindow(self):
        return self.recordingScheduleWindow

    def setRecordingScheduleWindow(self, newRecordingScheduleWindow):
        self.recordingScheduleWindow = newRecordingScheduleWindow

    def getPaddingBeforeProgramStarts(self):
        return self.paddingBeforeProgramStarts

    def setPaddingBeforeProgramStarts(self, newPaddingBeforeProgramStarts):
        self.paddingBeforeProgramStarts = newPaddingBeforeProgramStarts

    def getPaddingAfterProgramEnds(self):
        return self.paddingAfterProgramEnds

    def setPaddingAfterProgramEnds(self, newPaddingAfterProgramEnds):
        self.paddingAfterProgramEnds = newPaddingAfterProgramEnds

    def getProtectionPeriod(self):
        return self.protectionPeriod

    def setProtectionPeriod(self, newProtectionPeriod):
        self.protectionPeriod = newProtectionPeriod

    def getProtectionQuotaPercentage(self):
        return self.protectionQuotaPercentage

    def setProtectionQuotaPercentage(self, newProtectionQuotaPercentage):
        self.protectionQuotaPercentage = newProtectionQuotaPercentage

    def getRecordingLifetimePeriod(self):
        return self.recordingLifetimePeriod

    def setRecordingLifetimePeriod(self, newRecordingLifetimePeriod):
        self.recordingLifetimePeriod = newRecordingLifetimePeriod

    def getCleanupNoticePeriod(self):
        return self.cleanupNoticePeriod

    def setCleanupNoticePeriod(self, newCleanupNoticePeriod):
        self.cleanupNoticePeriod = newCleanupNoticePeriod

    def getSeriesRecordingEnabled(self):
        return self.seriesRecordingEnabled

    def setSeriesRecordingEnabled(self, newSeriesRecordingEnabled):
        self.seriesRecordingEnabled = newSeriesRecordingEnabled

    def getNonEntitledChannelPlaybackEnabled(self):
        return self.nonEntitledChannelPlaybackEnabled

    def setNonEntitledChannelPlaybackEnabled(self, newNonEntitledChannelPlaybackEnabled):
        self.nonEntitledChannelPlaybackEnabled = newNonEntitledChannelPlaybackEnabled

    def getNonExistingChannelPlaybackEnabled(self):
        return self.nonExistingChannelPlaybackEnabled

    def setNonExistingChannelPlaybackEnabled(self, newNonExistingChannelPlaybackEnabled):
        self.nonExistingChannelPlaybackEnabled = newNonExistingChannelPlaybackEnabled

    def getQuotaOveragePolicy(self):
        return self.quotaOveragePolicy

    def setQuotaOveragePolicy(self, newQuotaOveragePolicy):
        self.quotaOveragePolicy = newQuotaOveragePolicy

    def getProtectionPolicy(self):
        return self.protectionPolicy

    def setProtectionPolicy(self, newProtectionPolicy):
        self.protectionPolicy = newProtectionPolicy

    def getRecoveryGracePeriod(self):
        return self.recoveryGracePeriod

    def setRecoveryGracePeriod(self, newRecoveryGracePeriod):
        self.recoveryGracePeriod = newRecoveryGracePeriod


# @package Kaltura
# @subpackage Client
class KalturaUserAssetsListItem(KalturaObjectBase):
    """An item of user asset list"""

    def __init__(self,
            id=NotImplemented,
            orderIndex=NotImplemented,
            type=NotImplemented,
            userId=NotImplemented,
            listType=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Asset identifier
        # @var string
        self.id = id

        # The order index of the asset in the list
        # @var int
        self.orderIndex = orderIndex

        # The type of the asset
        # @var KalturaUserAssetsListItemType
        self.type = type

        # The identifier of the user who added the item to the list
        # @var string
        # @readonly
        self.userId = userId

        # The type of the list, all is not supported
        # @var KalturaUserAssetsListType
        self.listType = listType


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'orderIndex': getXmlNodeInt, 
        'type': (KalturaEnumsFactory.createString, "KalturaUserAssetsListItemType"), 
        'userId': getXmlNodeText, 
        'listType': (KalturaEnumsFactory.createString, "KalturaUserAssetsListType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserAssetsListItem.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserAssetsListItem")
        kparams.addStringIfDefined("id", self.id)
        kparams.addIntIfDefined("orderIndex", self.orderIndex)
        kparams.addStringEnumIfDefined("type", self.type)
        kparams.addStringEnumIfDefined("listType", self.listType)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getOrderIndex(self):
        return self.orderIndex

    def setOrderIndex(self, newOrderIndex):
        self.orderIndex = newOrderIndex

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType

    def getUserId(self):
        return self.userId

    def getListType(self):
        return self.listType

    def setListType(self, newListType):
        self.listType = newListType


# @package Kaltura
# @subpackage Client
class KalturaHouseholdLimitations(KalturaObjectBase):
    """Household limitations details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            concurrentLimit=NotImplemented,
            deviceLimit=NotImplemented,
            deviceFrequency=NotImplemented,
            deviceFrequencyDescription=NotImplemented,
            userFrequency=NotImplemented,
            userFrequencyDescription=NotImplemented,
            npvrQuotaInSeconds=NotImplemented,
            usersLimit=NotImplemented,
            deviceFamiliesLimitations=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Household limitation module identifier
        # @var int
        # @readonly
        self.id = id

        # Household limitation module name
        # @var string
        # @readonly
        self.name = name

        # Max number of streams allowed for the household
        # @var int
        # @readonly
        self.concurrentLimit = concurrentLimit

        # Max number of devices allowed for the household
        # @var int
        # @readonly
        self.deviceLimit = deviceLimit

        # Allowed device change frequency code
        # @var int
        # @readonly
        self.deviceFrequency = deviceFrequency

        # Allowed device change frequency description
        # @var string
        # @readonly
        self.deviceFrequencyDescription = deviceFrequencyDescription

        # Allowed user change frequency code
        # @var int
        # @readonly
        self.userFrequency = userFrequency

        # Allowed user change frequency description
        # @var string
        # @readonly
        self.userFrequencyDescription = userFrequencyDescription

        # Allowed NPVR Quota in Seconds
        # @var int
        # @readonly
        self.npvrQuotaInSeconds = npvrQuotaInSeconds

        # Max number of users allowed for the household
        # @var int
        # @readonly
        self.usersLimit = usersLimit

        # Device families limitations
        # @var array of KalturaHouseholdDeviceFamilyLimitations
        # @readonly
        self.deviceFamiliesLimitations = deviceFamiliesLimitations


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'concurrentLimit': getXmlNodeInt, 
        'deviceLimit': getXmlNodeInt, 
        'deviceFrequency': getXmlNodeInt, 
        'deviceFrequencyDescription': getXmlNodeText, 
        'userFrequency': getXmlNodeInt, 
        'userFrequencyDescription': getXmlNodeText, 
        'npvrQuotaInSeconds': getXmlNodeInt, 
        'usersLimit': getXmlNodeInt, 
        'deviceFamiliesLimitations': (KalturaObjectFactory.createArray, 'KalturaHouseholdDeviceFamilyLimitations'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHouseholdLimitations.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHouseholdLimitations")
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getConcurrentLimit(self):
        return self.concurrentLimit

    def getDeviceLimit(self):
        return self.deviceLimit

    def getDeviceFrequency(self):
        return self.deviceFrequency

    def getDeviceFrequencyDescription(self):
        return self.deviceFrequencyDescription

    def getUserFrequency(self):
        return self.userFrequency

    def getUserFrequencyDescription(self):
        return self.userFrequencyDescription

    def getNpvrQuotaInSeconds(self):
        return self.npvrQuotaInSeconds

    def getUsersLimit(self):
        return self.usersLimit

    def getDeviceFamiliesLimitations(self):
        return self.deviceFamiliesLimitations


# @package Kaltura
# @subpackage Client
class KalturaPartnerConfiguration(KalturaObjectBase):
    """Partner  base configuration"""

    def __init__(self):
        KalturaObjectBase.__init__(self)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPartnerConfiguration.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPartnerConfiguration")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaBillingPartnerConfig(KalturaPartnerConfiguration):
    """Partner billing configuration"""

    def __init__(self,
            value=NotImplemented,
            type=NotImplemented):
        KalturaPartnerConfiguration.__init__(self)

        # configuration value
        # @var string
        self.value = value

        # partner configuration type
        # @var KalturaPartnerConfigurationType
        self.type = type


    PROPERTY_LOADERS = {
        'value': getXmlNodeText, 
        'type': (KalturaEnumsFactory.createString, "KalturaPartnerConfigurationType"), 
    }

    def fromXml(self, node):
        KalturaPartnerConfiguration.fromXml(self, node)
        self.fromXmlImpl(node, KalturaBillingPartnerConfig.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPartnerConfiguration.toParams(self)
        kparams.put("objectType", "KalturaBillingPartnerConfig")
        kparams.addStringIfDefined("value", self.value)
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType


# @package Kaltura
# @subpackage Client
class KalturaLoginSession(KalturaObjectBase):
    """Login response"""

    def __init__(self,
            ks=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Access token in a KS format
        # @var string
        self.ks = ks


    PROPERTY_LOADERS = {
        'ks': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLoginSession.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaLoginSession")
        kparams.addStringIfDefined("ks", self.ks)
        return kparams

    def getKs(self):
        return self.ks

    def setKs(self, newKs):
        self.ks = newKs


# @package Kaltura
# @subpackage Client
class KalturaHousehold(KalturaObjectBase):
    """Household details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            description=NotImplemented,
            externalId=NotImplemented,
            householdLimitationsId=NotImplemented,
            devicesLimit=NotImplemented,
            usersLimit=NotImplemented,
            concurrentLimit=NotImplemented,
            regionId=NotImplemented,
            state=NotImplemented,
            isFrequencyEnabled=NotImplemented,
            frequencyNextDeviceAction=NotImplemented,
            frequencyNextUserAction=NotImplemented,
            restriction=NotImplemented,
            roleId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Household identifier
        # @var int
        # @readonly
        self.id = id

        # Household name
        # @var string
        self.name = name

        # Household description
        # @var string
        self.description = description

        # Household external identifier
        # @var string
        # @insertonly
        self.externalId = externalId

        # Household limitation module identifier
        # @var int
        # @readonly
        self.householdLimitationsId = householdLimitationsId

        # The max number of the devices that can be added to the household
        # @var int
        # @readonly
        self.devicesLimit = devicesLimit

        # The max number of the users that can be added to the household
        # @var int
        # @readonly
        self.usersLimit = usersLimit

        # The max number of concurrent streams in the household
        # @var int
        # @readonly
        self.concurrentLimit = concurrentLimit

        # The households region identifier
        # @var int
        # @readonly
        self.regionId = regionId

        # Household state
        # @var KalturaHouseholdState
        # @readonly
        self.state = state

        # Is household frequency enabled
        # @var bool
        # @readonly
        self.isFrequencyEnabled = isFrequencyEnabled

        # The next time a device is allowed to be removed from the household (epoch)
        # @var int
        # @readonly
        self.frequencyNextDeviceAction = frequencyNextDeviceAction

        # The next time a user is allowed to be removed from the household (epoch)
        # @var int
        # @readonly
        self.frequencyNextUserAction = frequencyNextUserAction

        # Household restriction
        # @var KalturaHouseholdRestriction
        # @readonly
        self.restriction = restriction

        # suspended roleId
        # @var int
        # @readonly
        self.roleId = roleId


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'description': getXmlNodeText, 
        'externalId': getXmlNodeText, 
        'householdLimitationsId': getXmlNodeInt, 
        'devicesLimit': getXmlNodeInt, 
        'usersLimit': getXmlNodeInt, 
        'concurrentLimit': getXmlNodeInt, 
        'regionId': getXmlNodeInt, 
        'state': (KalturaEnumsFactory.createString, "KalturaHouseholdState"), 
        'isFrequencyEnabled': getXmlNodeBool, 
        'frequencyNextDeviceAction': getXmlNodeInt, 
        'frequencyNextUserAction': getXmlNodeInt, 
        'restriction': (KalturaEnumsFactory.createString, "KalturaHouseholdRestriction"), 
        'roleId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaHousehold.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaHousehold")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("description", self.description)
        kparams.addStringIfDefined("externalId", self.externalId)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getDescription(self):
        return self.description

    def setDescription(self, newDescription):
        self.description = newDescription

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getHouseholdLimitationsId(self):
        return self.householdLimitationsId

    def getDevicesLimit(self):
        return self.devicesLimit

    def getUsersLimit(self):
        return self.usersLimit

    def getConcurrentLimit(self):
        return self.concurrentLimit

    def getRegionId(self):
        return self.regionId

    def getState(self):
        return self.state

    def getIsFrequencyEnabled(self):
        return self.isFrequencyEnabled

    def getFrequencyNextDeviceAction(self):
        return self.frequencyNextDeviceAction

    def getFrequencyNextUserAction(self):
        return self.frequencyNextUserAction

    def getRestriction(self):
        return self.restriction

    def getRoleId(self):
        return self.roleId


# @package Kaltura
# @subpackage Client
class KalturaDevicePin(KalturaObjectBase):
    """Device pin"""

    def __init__(self,
            pin=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Device pin
        # @var string
        self.pin = pin


    PROPERTY_LOADERS = {
        'pin': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaDevicePin.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaDevicePin")
        kparams.addStringIfDefined("pin", self.pin)
        return kparams

    def getPin(self):
        return self.pin

    def setPin(self, newPin):
        self.pin = newPin


# @package Kaltura
# @subpackage Client
class KalturaLoginResponse(KalturaObjectBase):
    def __init__(self,
            user=NotImplemented,
            loginSession=NotImplemented):
        KalturaObjectBase.__init__(self)

        # User
        # @var KalturaOTTUser
        self.user = user

        # Kaltura login session details
        # @var KalturaLoginSession
        self.loginSession = loginSession


    PROPERTY_LOADERS = {
        'user': (KalturaObjectFactory.create, 'KalturaOTTUser'), 
        'loginSession': (KalturaObjectFactory.create, 'KalturaLoginSession'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaLoginResponse.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaLoginResponse")
        kparams.addObjectIfDefined("user", self.user)
        kparams.addObjectIfDefined("loginSession", self.loginSession)
        return kparams

    def getUser(self):
        return self.user

    def setUser(self, newUser):
        self.user = newUser

    def getLoginSession(self):
        return self.loginSession

    def setLoginSession(self, newLoginSession):
        self.loginSession = newLoginSession


# @package Kaltura
# @subpackage Client
class KalturaPin(KalturaObjectBase):
    """PIN and its origin of definition"""

    def __init__(self,
            pin=NotImplemented,
            origin=NotImplemented,
            type=NotImplemented):
        KalturaObjectBase.__init__(self)

        # PIN code
        # @var string
        self.pin = pin

        # Where the PIN was defined at - account, household or user
        # @var KalturaRuleLevel
        self.origin = origin

        # PIN type
        # @var KalturaPinType
        self.type = type


    PROPERTY_LOADERS = {
        'pin': getXmlNodeText, 
        'origin': (KalturaEnumsFactory.createString, "KalturaRuleLevel"), 
        'type': (KalturaEnumsFactory.createString, "KalturaPinType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPin.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPin")
        kparams.addStringIfDefined("pin", self.pin)
        kparams.addStringEnumIfDefined("origin", self.origin)
        kparams.addStringEnumIfDefined("type", self.type)
        return kparams

    def getPin(self):
        return self.pin

    def setPin(self, newPin):
        self.pin = newPin

    def getOrigin(self):
        return self.origin

    def setOrigin(self, newOrigin):
        self.origin = newOrigin

    def getType(self):
        return self.type

    def setType(self, newType):
        self.type = newType


# @package Kaltura
# @subpackage Client
class KalturaPurchaseSettings(KalturaPin):
    """Purchase settings and PIN"""

    def __init__(self,
            pin=NotImplemented,
            origin=NotImplemented,
            type=NotImplemented,
            permission=NotImplemented):
        KalturaPin.__init__(self,
            pin,
            origin,
            type)

        # Purchase permission - block, ask or allow
        # @var KalturaPurchaseSettingsType
        self.permission = permission


    PROPERTY_LOADERS = {
        'permission': (KalturaEnumsFactory.createString, "KalturaPurchaseSettingsType"), 
    }

    def fromXml(self, node):
        KalturaPin.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPurchaseSettings.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPin.toParams(self)
        kparams.put("objectType", "KalturaPurchaseSettings")
        kparams.addStringEnumIfDefined("permission", self.permission)
        return kparams

    def getPermission(self):
        return self.permission

    def setPermission(self, newPermission):
        self.permission = newPermission


# @package Kaltura
# @subpackage Client
class KalturaCoupon(KalturaObjectBase):
    """Coupon details container"""

    def __init__(self,
            couponsGroup=NotImplemented,
            status=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Coupons group details
        # @var KalturaCouponsGroup
        # @readonly
        self.couponsGroup = couponsGroup

        # Coupon status
        # @var KalturaCouponStatus
        # @readonly
        self.status = status


    PROPERTY_LOADERS = {
        'couponsGroup': (KalturaObjectFactory.create, 'KalturaCouponsGroup'), 
        'status': (KalturaEnumsFactory.createString, "KalturaCouponStatus"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaCoupon.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaCoupon")
        return kparams

    def getCouponsGroup(self):
        return self.couponsGroup

    def getStatus(self):
        return self.status


# @package Kaltura
# @subpackage Client
class KalturaOTTCategory(KalturaObjectBase):
    """Category details"""

    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            parentCategoryId=NotImplemented,
            childCategories=NotImplemented,
            channels=NotImplemented,
            images=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Unique identifier for the category
        # @var int
        # @readonly
        self.id = id

        # Category name
        # @var string
        self.name = name

        # Category parent identifier
        # @var int
        self.parentCategoryId = parentCategoryId

        # Child categories
        # @var array of KalturaOTTCategory
        self.childCategories = childCategories

        # Category channels
        # @var array of KalturaChannel
        self.channels = channels

        # Category images
        # @var array of KalturaMediaImage
        self.images = images


    PROPERTY_LOADERS = {
        'id': getXmlNodeInt, 
        'name': getXmlNodeText, 
        'parentCategoryId': getXmlNodeInt, 
        'childCategories': (KalturaObjectFactory.createArray, 'KalturaObjectBase'), 
        'channels': (KalturaObjectFactory.createArray, 'KalturaChannel'), 
        'images': (KalturaObjectFactory.createArray, 'KalturaMediaImage'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOTTCategory.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaOTTCategory")
        kparams.addStringIfDefined("name", self.name)
        kparams.addIntIfDefined("parentCategoryId", self.parentCategoryId)
        kparams.addArrayIfDefined("childCategories", self.childCategories)
        kparams.addArrayIfDefined("channels", self.channels)
        kparams.addArrayIfDefined("images", self.images)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getParentCategoryId(self):
        return self.parentCategoryId

    def setParentCategoryId(self, newParentCategoryId):
        self.parentCategoryId = newParentCategoryId

    def getChildCategories(self):
        return self.childCategories

    def setChildCategories(self, newChildCategories):
        self.childCategories = newChildCategories

    def getChannels(self):
        return self.channels

    def setChannels(self, newChannels):
        self.channels = newChannels

    def getImages(self):
        return self.images

    def setImages(self, newImages):
        self.images = newImages


# @package Kaltura
# @subpackage Client
class KalturaEntitlementRenewal(KalturaObjectBase):
    def __init__(self,
            price=NotImplemented,
            date=NotImplemented,
            purchaseId=NotImplemented,
            subscriptionId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Price that is going to be paid on the renewal
        # @var KalturaPrice
        self.price = price

        # Next renewal date
        # @var int
        self.date = date

        # Puchase ID
        # @var int
        self.purchaseId = purchaseId

        # Subscription ID
        # @var int
        self.subscriptionId = subscriptionId


    PROPERTY_LOADERS = {
        'price': (KalturaObjectFactory.create, 'KalturaPrice'), 
        'date': getXmlNodeInt, 
        'purchaseId': getXmlNodeInt, 
        'subscriptionId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaEntitlementRenewal.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaEntitlementRenewal")
        kparams.addObjectIfDefined("price", self.price)
        kparams.addIntIfDefined("date", self.date)
        kparams.addIntIfDefined("purchaseId", self.purchaseId)
        kparams.addIntIfDefined("subscriptionId", self.subscriptionId)
        return kparams

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getDate(self):
        return self.date

    def setDate(self, newDate):
        self.date = newDate

    def getPurchaseId(self):
        return self.purchaseId

    def setPurchaseId(self, newPurchaseId):
        self.purchaseId = newPurchaseId

    def getSubscriptionId(self):
        return self.subscriptionId

    def setSubscriptionId(self, newSubscriptionId):
        self.subscriptionId = newSubscriptionId


# @package Kaltura
# @subpackage Client
class KalturaSocial(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            firstName=NotImplemented,
            lastName=NotImplemented,
            email=NotImplemented,
            gender=NotImplemented,
            userId=NotImplemented,
            birthday=NotImplemented,
            status=NotImplemented,
            pictureUrl=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Facebook identifier
        # @var string
        # @readonly
        self.id = id

        # Full name
        # @var string
        self.name = name

        # First name
        # @var string
        self.firstName = firstName

        # Last name
        # @var string
        self.lastName = lastName

        # User email
        # @var string
        self.email = email

        # Gender
        # @var string
        self.gender = gender

        # User identifier
        # @var string
        # @readonly
        self.userId = userId

        # User birthday
        # @var string
        self.birthday = birthday

        # User model status
        #             Possible values: UNKNOWN, OK, ERROR, NOACTION, NOTEXIST, CONFLICT, MERGE, MERGEOK, NEWUSER, MINFRIENDS, INVITEOK, INVITEERROR, ACCESSDENIED, WRONGPASSWORDORUSERNAME, UNMERGEOK, USEREMAILISMISSING
        # @var string
        # @readonly
        self.status = status

        # Profile picture URL
        # @var string
        self.pictureUrl = pictureUrl


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'name': getXmlNodeText, 
        'firstName': getXmlNodeText, 
        'lastName': getXmlNodeText, 
        'email': getXmlNodeText, 
        'gender': getXmlNodeText, 
        'userId': getXmlNodeText, 
        'birthday': getXmlNodeText, 
        'status': getXmlNodeText, 
        'pictureUrl': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocial.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSocial")
        kparams.addStringIfDefined("name", self.name)
        kparams.addStringIfDefined("firstName", self.firstName)
        kparams.addStringIfDefined("lastName", self.lastName)
        kparams.addStringIfDefined("email", self.email)
        kparams.addStringIfDefined("gender", self.gender)
        kparams.addStringIfDefined("birthday", self.birthday)
        kparams.addStringIfDefined("pictureUrl", self.pictureUrl)
        return kparams

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getFirstName(self):
        return self.firstName

    def setFirstName(self, newFirstName):
        self.firstName = newFirstName

    def getLastName(self):
        return self.lastName

    def setLastName(self, newLastName):
        self.lastName = newLastName

    def getEmail(self):
        return self.email

    def setEmail(self, newEmail):
        self.email = newEmail

    def getGender(self):
        return self.gender

    def setGender(self, newGender):
        self.gender = newGender

    def getUserId(self):
        return self.userId

    def getBirthday(self):
        return self.birthday

    def setBirthday(self, newBirthday):
        self.birthday = newBirthday

    def getStatus(self):
        return self.status

    def getPictureUrl(self):
        return self.pictureUrl

    def setPictureUrl(self, newPictureUrl):
        self.pictureUrl = newPictureUrl


# @package Kaltura
# @subpackage Client
class KalturaFacebookSocial(KalturaSocial):
    def __init__(self,
            id=NotImplemented,
            name=NotImplemented,
            firstName=NotImplemented,
            lastName=NotImplemented,
            email=NotImplemented,
            gender=NotImplemented,
            userId=NotImplemented,
            birthday=NotImplemented,
            status=NotImplemented,
            pictureUrl=NotImplemented):
        KalturaSocial.__init__(self,
            id,
            name,
            firstName,
            lastName,
            email,
            gender,
            userId,
            birthday,
            status,
            pictureUrl)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaSocial.fromXml(self, node)
        self.fromXmlImpl(node, KalturaFacebookSocial.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocial.toParams(self)
        kparams.put("objectType", "KalturaFacebookSocial")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaSocialConfig(KalturaObjectBase):
    """Returns social configuration for the partner"""

    def __init__(self):
        KalturaObjectBase.__init__(self)


    PROPERTY_LOADERS = {
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialConfig.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaSocialConfig")
        return kparams


# @package Kaltura
# @subpackage Client
class KalturaSocialFacebookConfig(KalturaSocialConfig):
    """Returns social configuration for the partner"""

    def __init__(self,
            appId=NotImplemented,
            permissions=NotImplemented):
        KalturaSocialConfig.__init__(self)

        # The application identifier
        # @var string
        self.appId = appId

        # List of application permissions
        # @var string
        self.permissions = permissions


    PROPERTY_LOADERS = {
        'appId': getXmlNodeText, 
        'permissions': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaSocialConfig.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialFacebookConfig.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialConfig.toParams(self)
        kparams.put("objectType", "KalturaSocialFacebookConfig")
        kparams.addStringIfDefined("appId", self.appId)
        kparams.addStringIfDefined("permissions", self.permissions)
        return kparams

    def getAppId(self):
        return self.appId

    def setAppId(self, newAppId):
        self.appId = newAppId

    def getPermissions(self):
        return self.permissions

    def setPermissions(self, newPermissions):
        self.permissions = newPermissions


# @package Kaltura
# @subpackage Client
class KalturaActionPermissionItem(KalturaObjectBase):
    def __init__(self,
            network=NotImplemented,
            actionPrivacy=NotImplemented,
            privacy=NotImplemented,
            action=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Social network
        # @var KalturaSocialNetwork
        self.network = network

        # Action privacy
        # @var KalturaSocialActionPrivacy
        self.actionPrivacy = actionPrivacy

        # Social privacy
        # @var KalturaSocialPrivacy
        self.privacy = privacy

        # Action - separated with comma
        # @var string
        self.action = action


    PROPERTY_LOADERS = {
        'network': (KalturaEnumsFactory.createString, "KalturaSocialNetwork"), 
        'actionPrivacy': (KalturaEnumsFactory.createString, "KalturaSocialActionPrivacy"), 
        'privacy': (KalturaEnumsFactory.createString, "KalturaSocialPrivacy"), 
        'action': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaActionPermissionItem.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaActionPermissionItem")
        kparams.addStringEnumIfDefined("network", self.network)
        kparams.addStringEnumIfDefined("actionPrivacy", self.actionPrivacy)
        kparams.addStringEnumIfDefined("privacy", self.privacy)
        kparams.addStringIfDefined("action", self.action)
        return kparams

    def getNetwork(self):
        return self.network

    def setNetwork(self, newNetwork):
        self.network = newNetwork

    def getActionPrivacy(self):
        return self.actionPrivacy

    def setActionPrivacy(self, newActionPrivacy):
        self.actionPrivacy = newActionPrivacy

    def getPrivacy(self):
        return self.privacy

    def setPrivacy(self, newPrivacy):
        self.privacy = newPrivacy

    def getAction(self):
        return self.action

    def setAction(self, newAction):
        self.action = newAction


# @package Kaltura
# @subpackage Client
class KalturaSocialUserConfig(KalturaSocialConfig):
    def __init__(self,
            actionPermissionItems=NotImplemented):
        KalturaSocialConfig.__init__(self)

        # List of action permission items
        # @var array of KalturaActionPermissionItem
        self.actionPermissionItems = actionPermissionItems


    PROPERTY_LOADERS = {
        'actionPermissionItems': (KalturaObjectFactory.createArray, 'KalturaActionPermissionItem'), 
    }

    def fromXml(self, node):
        KalturaSocialConfig.fromXml(self, node)
        self.fromXmlImpl(node, KalturaSocialUserConfig.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaSocialConfig.toParams(self)
        kparams.put("objectType", "KalturaSocialUserConfig")
        kparams.addArrayIfDefined("actionPermissionItems", self.actionPermissionItems)
        return kparams

    def getActionPermissionItems(self):
        return self.actionPermissionItems

    def setActionPermissionItems(self, newActionPermissionItems):
        self.actionPermissionItems = newActionPermissionItems


# @package Kaltura
# @subpackage Client
class KalturaPurchaseBase(KalturaObjectBase):
    def __init__(self,
            productId=NotImplemented,
            contentId=NotImplemented,
            productType=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Identifier for the package from which this content is offered
        # @var int
        self.productId = productId

        # Identifier for the content to purchase. Relevant only if Product type = PPV
        # @var int
        self.contentId = contentId

        # Package type. Possible values: PPV, Subscription, Collection
        # @var KalturaTransactionType
        self.productType = productType


    PROPERTY_LOADERS = {
        'productId': getXmlNodeInt, 
        'contentId': getXmlNodeInt, 
        'productType': (KalturaEnumsFactory.createString, "KalturaTransactionType"), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPurchaseBase.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaPurchaseBase")
        kparams.addIntIfDefined("productId", self.productId)
        kparams.addIntIfDefined("contentId", self.contentId)
        kparams.addStringEnumIfDefined("productType", self.productType)
        return kparams

    def getProductId(self):
        return self.productId

    def setProductId(self, newProductId):
        self.productId = newProductId

    def getContentId(self):
        return self.contentId

    def setContentId(self, newContentId):
        self.contentId = newContentId

    def getProductType(self):
        return self.productType

    def setProductType(self, newProductType):
        self.productType = newProductType


# @package Kaltura
# @subpackage Client
class KalturaPurchase(KalturaPurchaseBase):
    def __init__(self,
            productId=NotImplemented,
            contentId=NotImplemented,
            productType=NotImplemented,
            currency=NotImplemented,
            price=NotImplemented,
            paymentMethodId=NotImplemented,
            paymentGatewayId=NotImplemented,
            coupon=NotImplemented,
            adapterData=NotImplemented):
        KalturaPurchaseBase.__init__(self,
            productId,
            contentId,
            productType)

        # Identifier for paying currency, according to ISO 4217
        # @var string
        self.currency = currency

        # Net sum to charge - as a one-time transaction. Price must match the previously provided price for the specified content.
        # @var float
        self.price = price

        # Identifier for a pre-entered payment method. If not provided - the household's default payment method is used
        # @var int
        self.paymentMethodId = paymentMethodId

        # Identifier for a pre-associated payment gateway. If not provided - the account's default payment gateway is used
        # @var int
        self.paymentGatewayId = paymentGatewayId

        # Coupon code
        # @var string
        self.coupon = coupon

        # Additional data for the adapter
        # @var string
        self.adapterData = adapterData


    PROPERTY_LOADERS = {
        'currency': getXmlNodeText, 
        'price': getXmlNodeFloat, 
        'paymentMethodId': getXmlNodeInt, 
        'paymentGatewayId': getXmlNodeInt, 
        'coupon': getXmlNodeText, 
        'adapterData': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaPurchaseBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPurchase.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPurchaseBase.toParams(self)
        kparams.put("objectType", "KalturaPurchase")
        kparams.addStringIfDefined("currency", self.currency)
        kparams.addFloatIfDefined("price", self.price)
        kparams.addIntIfDefined("paymentMethodId", self.paymentMethodId)
        kparams.addIntIfDefined("paymentGatewayId", self.paymentGatewayId)
        kparams.addStringIfDefined("coupon", self.coupon)
        kparams.addStringIfDefined("adapterData", self.adapterData)
        return kparams

    def getCurrency(self):
        return self.currency

    def setCurrency(self, newCurrency):
        self.currency = newCurrency

    def getPrice(self):
        return self.price

    def setPrice(self, newPrice):
        self.price = newPrice

    def getPaymentMethodId(self):
        return self.paymentMethodId

    def setPaymentMethodId(self, newPaymentMethodId):
        self.paymentMethodId = newPaymentMethodId

    def getPaymentGatewayId(self):
        return self.paymentGatewayId

    def setPaymentGatewayId(self, newPaymentGatewayId):
        self.paymentGatewayId = newPaymentGatewayId

    def getCoupon(self):
        return self.coupon

    def setCoupon(self, newCoupon):
        self.coupon = newCoupon

    def getAdapterData(self):
        return self.adapterData

    def setAdapterData(self, newAdapterData):
        self.adapterData = newAdapterData


# @package Kaltura
# @subpackage Client
class KalturaPurchaseSession(KalturaPurchase):
    def __init__(self,
            productId=NotImplemented,
            contentId=NotImplemented,
            productType=NotImplemented,
            currency=NotImplemented,
            price=NotImplemented,
            paymentMethodId=NotImplemented,
            paymentGatewayId=NotImplemented,
            coupon=NotImplemented,
            adapterData=NotImplemented,
            previewModuleId=NotImplemented):
        KalturaPurchase.__init__(self,
            productId,
            contentId,
            productType,
            currency,
            price,
            paymentMethodId,
            paymentGatewayId,
            coupon,
            adapterData)

        # Preview module identifier (relevant only for subscription)
        # @var int
        self.previewModuleId = previewModuleId


    PROPERTY_LOADERS = {
        'previewModuleId': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaPurchase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaPurchaseSession.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPurchase.toParams(self)
        kparams.put("objectType", "KalturaPurchaseSession")
        kparams.addIntIfDefined("previewModuleId", self.previewModuleId)
        return kparams

    def getPreviewModuleId(self):
        return self.previewModuleId

    def setPreviewModuleId(self, newPreviewModuleId):
        self.previewModuleId = newPreviewModuleId


# @package Kaltura
# @subpackage Client
class KalturaExternalReceipt(KalturaPurchaseBase):
    def __init__(self,
            productId=NotImplemented,
            contentId=NotImplemented,
            productType=NotImplemented,
            receiptId=NotImplemented,
            paymentGatewayName=NotImplemented):
        KalturaPurchaseBase.__init__(self,
            productId,
            contentId,
            productType)

        # A unique identifier that was provided by the In-App billing service to validate the purchase
        # @var string
        self.receiptId = receiptId

        # The payment gateway name for the In-App billing service to be used. Possible values: Google/Apple
        # @var string
        self.paymentGatewayName = paymentGatewayName


    PROPERTY_LOADERS = {
        'receiptId': getXmlNodeText, 
        'paymentGatewayName': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaPurchaseBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaExternalReceipt.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaPurchaseBase.toParams(self)
        kparams.put("objectType", "KalturaExternalReceipt")
        kparams.addStringIfDefined("receiptId", self.receiptId)
        kparams.addStringIfDefined("paymentGatewayName", self.paymentGatewayName)
        return kparams

    def getReceiptId(self):
        return self.receiptId

    def setReceiptId(self, newReceiptId):
        self.receiptId = newReceiptId

    def getPaymentGatewayName(self):
        return self.paymentGatewayName

    def setPaymentGatewayName(self, newPaymentGatewayName):
        self.paymentGatewayName = newPaymentGatewayName


# @package Kaltura
# @subpackage Client
class KalturaTransaction(KalturaObjectBase):
    def __init__(self,
            id=NotImplemented,
            paymentGatewayReferenceId=NotImplemented,
            paymentGatewayResponseId=NotImplemented,
            state=NotImplemented,
            failReasonCode=NotImplemented,
            createdAt=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Kaltura unique ID representing the transaction
        # @var string
        self.id = id

        # Transaction reference ID received from the payment gateway. 
        #             Value is available only if the payment gateway provides this information.
        # @var string
        self.paymentGatewayReferenceId = paymentGatewayReferenceId

        # Response ID received from by the payment gateway. 
        #             Value is available only if the payment gateway provides this information.
        # @var string
        self.paymentGatewayResponseId = paymentGatewayResponseId

        # Transaction state: OK/Pending/Failed
        # @var string
        self.state = state

        # Adapter failure reason code
        #             Insufficient funds = 20, Invalid account = 21, User unknown = 22, Reason unknown = 23, Unknown payment gateway response = 24,
        #             No response from payment gateway = 25, Exceeded retry limit = 26, Illegal client request = 27, Expired = 28
        # @var int
        self.failReasonCode = failReasonCode

        # Entitlement creation date
        # @var int
        self.createdAt = createdAt


    PROPERTY_LOADERS = {
        'id': getXmlNodeText, 
        'paymentGatewayReferenceId': getXmlNodeText, 
        'paymentGatewayResponseId': getXmlNodeText, 
        'state': getXmlNodeText, 
        'failReasonCode': getXmlNodeInt, 
        'createdAt': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTransaction.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaTransaction")
        kparams.addStringIfDefined("id", self.id)
        kparams.addStringIfDefined("paymentGatewayReferenceId", self.paymentGatewayReferenceId)
        kparams.addStringIfDefined("paymentGatewayResponseId", self.paymentGatewayResponseId)
        kparams.addStringIfDefined("state", self.state)
        kparams.addIntIfDefined("failReasonCode", self.failReasonCode)
        kparams.addIntIfDefined("createdAt", self.createdAt)
        return kparams

    def getId(self):
        return self.id

    def setId(self, newId):
        self.id = newId

    def getPaymentGatewayReferenceId(self):
        return self.paymentGatewayReferenceId

    def setPaymentGatewayReferenceId(self, newPaymentGatewayReferenceId):
        self.paymentGatewayReferenceId = newPaymentGatewayReferenceId

    def getPaymentGatewayResponseId(self):
        return self.paymentGatewayResponseId

    def setPaymentGatewayResponseId(self, newPaymentGatewayResponseId):
        self.paymentGatewayResponseId = newPaymentGatewayResponseId

    def getState(self):
        return self.state

    def setState(self, newState):
        self.state = newState

    def getFailReasonCode(self):
        return self.failReasonCode

    def setFailReasonCode(self, newFailReasonCode):
        self.failReasonCode = newFailReasonCode

    def getCreatedAt(self):
        return self.createdAt

    def setCreatedAt(self, newCreatedAt):
        self.createdAt = newCreatedAt


# @package Kaltura
# @subpackage Client
class KalturaTransactionStatus(KalturaObjectBase):
    def __init__(self,
            adapterTransactionStatus=NotImplemented,
            externalId=NotImplemented,
            externalStatus=NotImplemented,
            externalMessage=NotImplemented,
            failReason=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Payment gateway adapter application state for the transaction to update
        # @var KalturaTransactionAdapterStatus
        self.adapterTransactionStatus = adapterTransactionStatus

        # External transaction identifier
        # @var string
        self.externalId = externalId

        # Payment gateway transaction status
        # @var string
        self.externalStatus = externalStatus

        # Payment gateway message
        # @var string
        self.externalMessage = externalMessage

        # The reason the transaction failed
        # @var int
        self.failReason = failReason


    PROPERTY_LOADERS = {
        'adapterTransactionStatus': (KalturaEnumsFactory.createString, "KalturaTransactionAdapterStatus"), 
        'externalId': getXmlNodeText, 
        'externalStatus': getXmlNodeText, 
        'externalMessage': getXmlNodeText, 
        'failReason': getXmlNodeInt, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaTransactionStatus.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaTransactionStatus")
        kparams.addStringEnumIfDefined("adapterTransactionStatus", self.adapterTransactionStatus)
        kparams.addStringIfDefined("externalId", self.externalId)
        kparams.addStringIfDefined("externalStatus", self.externalStatus)
        kparams.addStringIfDefined("externalMessage", self.externalMessage)
        kparams.addIntIfDefined("failReason", self.failReason)
        return kparams

    def getAdapterTransactionStatus(self):
        return self.adapterTransactionStatus

    def setAdapterTransactionStatus(self, newAdapterTransactionStatus):
        self.adapterTransactionStatus = newAdapterTransactionStatus

    def getExternalId(self):
        return self.externalId

    def setExternalId(self, newExternalId):
        self.externalId = newExternalId

    def getExternalStatus(self):
        return self.externalStatus

    def setExternalStatus(self, newExternalStatus):
        self.externalStatus = newExternalStatus

    def getExternalMessage(self):
        return self.externalMessage

    def setExternalMessage(self, newExternalMessage):
        self.externalMessage = newExternalMessage

    def getFailReason(self):
        return self.failReason

    def setFailReason(self, newFailReason):
        self.failReason = newFailReason


# @package Kaltura
# @subpackage Client
class KalturaUserLoginPin(KalturaObjectBase):
    """Log in pin code details"""

    def __init__(self,
            pinCode=NotImplemented,
            expirationTime=NotImplemented,
            userId=NotImplemented):
        KalturaObjectBase.__init__(self)

        # Generated login pin code
        # @var string
        self.pinCode = pinCode

        # Login pin expiration time (epoch)
        # @var int
        self.expirationTime = expirationTime

        # User Identifier
        # @var string
        # @readonly
        self.userId = userId


    PROPERTY_LOADERS = {
        'pinCode': getXmlNodeText, 
        'expirationTime': getXmlNodeInt, 
        'userId': getXmlNodeText, 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaUserLoginPin.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaUserLoginPin")
        kparams.addStringIfDefined("pinCode", self.pinCode)
        kparams.addIntIfDefined("expirationTime", self.expirationTime)
        return kparams

    def getPinCode(self):
        return self.pinCode

    def setPinCode(self, newPinCode):
        self.pinCode = newPinCode

    def getExpirationTime(self):
        return self.expirationTime

    def setExpirationTime(self, newExpirationTime):
        self.expirationTime = newExpirationTime

    def getUserId(self):
        return self.userId


# @package Kaltura
# @subpackage Client
class KalturaOTTUserDynamicData(KalturaObjectBase):
    """User dynamic data"""

    def __init__(self,
            userId=NotImplemented,
            key=NotImplemented,
            value=NotImplemented):
        KalturaObjectBase.__init__(self)

        # User identifier
        # @var string
        # @readonly
        self.userId = userId

        # Key
        # @var string
        self.key = key

        # Value
        # @var KalturaStringValue
        self.value = value


    PROPERTY_LOADERS = {
        'userId': getXmlNodeText, 
        'key': getXmlNodeText, 
        'value': (KalturaObjectFactory.create, 'KalturaStringValue'), 
    }

    def fromXml(self, node):
        KalturaObjectBase.fromXml(self, node)
        self.fromXmlImpl(node, KalturaOTTUserDynamicData.PROPERTY_LOADERS)

    def toParams(self):
        kparams = KalturaObjectBase.toParams(self)
        kparams.put("objectType", "KalturaOTTUserDynamicData")
        kparams.addStringIfDefined("key", self.key)
        kparams.addObjectIfDefined("value", self.value)
        return kparams

    def getUserId(self):
        return self.userId

    def getKey(self):
        return self.key

    def setKey(self, newKey):
        self.key = newKey

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        self.value = newValue


########## services ##########

# @package Kaltura
# @subpackage Client
class KalturaAnnouncementService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, announcement):
        """Add a new future scheduled system announcement push notification"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("announcement", announcement)
        self.client.queueServiceActionCall("announcement", "add", "KalturaAnnouncement", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAnnouncement')

    def delete(self, id):
        """Delete an existing announcing. Announcement cannot be delete while being sent."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("announcement", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def enableSystemAnnouncements(self):
        """Enable system announcements"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("announcement", "enableSystemAnnouncements", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter, pager = NotImplemented):
        """Lists all announcements in the system."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("announcement", "list", "KalturaAnnouncementListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAnnouncementListResponse')

    def update(self, announcementId, announcement):
        """Update an existing future system announcement push notification. Announcement can only be updated only before sending"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("announcementId", announcementId);
        kparams.addObjectIfDefined("announcement", announcement)
        self.client.queueServiceActionCall("announcement", "update", "KalturaAnnouncement", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAnnouncement')

    def updateStatus(self, id, status):
        """Update a system announcement status"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addBoolIfDefined("status", status);
        self.client.queueServiceActionCall("announcement", "updateStatus", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaAppTokenService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, appToken):
        """Add new application authentication token"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("appToken", appToken)
        self.client.queueServiceActionCall("apptoken", "add", "KalturaAppToken", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAppToken')

    def delete(self, id):
        """Delete application authentication token by id"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("apptoken", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Get application authentication token by id"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("apptoken", "get", "KalturaAppToken", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAppToken')

    def startSession(self, id, tokenHash, userId = NotImplemented, expiry = NotImplemented, udid = NotImplemented):
        """Starts a new KS (Kaltura Session) based on application authentication token id"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addStringIfDefined("tokenHash", tokenHash)
        kparams.addStringIfDefined("userId", userId)
        kparams.addIntIfDefined("expiry", expiry);
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("apptoken", "startSession", "KalturaSessionInfo", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSessionInfo')


# @package Kaltura
# @subpackage Client
class KalturaAssetCommentService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, comment):
        """Add asset comments by asset id"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("comment", comment)
        self.client.queueServiceActionCall("assetcomment", "add", "KalturaAssetComment", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetComment')

    def list(self, filter, pager = NotImplemented):
        """Returns asset comments by asset id"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("assetcomment", "list", "KalturaAssetCommentListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetCommentListResponse')


# @package Kaltura
# @subpackage Client
class KalturaAssetService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def count(self, filter = NotImplemented):
        """Returns a group-by result for media or EPG according to given filter. Lists values of each field and their respective count."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("asset", "count", "KalturaAssetCount", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetCount')

    def get(self, id, assetReferenceType):
        """Returns media or EPG asset by media / EPG internal or external identifier"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addStringIfDefined("assetReferenceType", assetReferenceType)
        self.client.queueServiceActionCall("asset", "get", "KalturaAsset", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAsset')

    def getAdsContext(self, assetId, assetType, contextDataParams):
        """Returns the data for ads control"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("assetId", assetId)
        kparams.addStringIfDefined("assetType", assetType)
        kparams.addObjectIfDefined("contextDataParams", contextDataParams)
        self.client.queueServiceActionCall("asset", "getAdsContext", "KalturaAdsContext", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAdsContext')

    def getPlaybackContext(self, assetId, assetType, contextDataParams):
        """This action delivers all data relevant for player"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("assetId", assetId)
        kparams.addStringIfDefined("assetType", assetType)
        kparams.addObjectIfDefined("contextDataParams", contextDataParams)
        self.client.queueServiceActionCall("asset", "getPlaybackContext", "KalturaPlaybackContext", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPlaybackContext')

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Returns media or EPG assets. Filters by media identifiers or by EPG internal or external identifier."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("asset", "list", "KalturaAssetListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetListResponse')


# @package Kaltura
# @subpackage Client
class KalturaAssetFileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def getContext(self, id, contextType):
        """get KalturaAssetFileContext"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addStringIfDefined("contextType", contextType)
        self.client.queueServiceActionCall("assetfile", "getContext", "KalturaAssetFileContext", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetFileContext')

    def playManifest(self, partnerId, assetId, assetType, assetFileId, contextType, ks = NotImplemented):
        """Redirects to play manifest"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("assetId", assetId)
        kparams.addStringIfDefined("assetType", assetType)
        kparams.addIntIfDefined("assetFileId", assetFileId);
        kparams.addStringIfDefined("contextType", contextType)
        kparams.addStringIfDefined("ks", ks)
        self.client.queueServiceActionCall("assetfile", "playManifest", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()


# @package Kaltura
# @subpackage Client
class KalturaAssetHistoryService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def clean(self, filter = NotImplemented):
        """Clean the user's viewing history"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("assethistory", "clean", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Get recently watched media for user, ordered by recently watched first."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("assethistory", "list", "KalturaAssetHistoryListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetHistoryListResponse')


# @package Kaltura
# @subpackage Client
class KalturaAssetStatisticsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def query(self, query):
        """Returns statistics for given list of assets by type and / or time period"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("query", query)
        self.client.queueServiceActionCall("assetstatistics", "query", "KalturaAssetStatisticsListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaAssetStatisticsListResponse')


# @package Kaltura
# @subpackage Client
class KalturaBookmarkService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, bookmark):
        """Report player position and action for the user on the watched asset. Player position is used to later allow resume watching."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("bookmark", bookmark)
        self.client.queueServiceActionCall("bookmark", "add", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter):
        """Returns player position record/s for the requested asset and the requesting user. 
                    If default user makes the request - player position records are provided for all of the users in the household.
                    If non-default user makes the request - player position records are provided for the requesting user and the default user of the household."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("bookmark", "list", "KalturaBookmarkListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaBookmarkListResponse')


# @package Kaltura
# @subpackage Client
class KalturaCdnAdapterProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, adapter):
        """Insert new CDN adapter for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("adapter", adapter)
        self.client.queueServiceActionCall("cdnadapterprofile", "add", "KalturaCDNAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDNAdapterProfile')

    def delete(self, adapterId):
        """Delete CDN adapter by CDN adapter id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("adapterId", adapterId);
        self.client.queueServiceActionCall("cdnadapterprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generateSharedSecret(self, adapterId):
        """Generate CDN adapter shared secret"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("adapterId", adapterId);
        self.client.queueServiceActionCall("cdnadapterprofile", "generateSharedSecret", "KalturaCDNAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDNAdapterProfile')

    def list(self):
        """Returns all CDN adapters for partner"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("cdnadapterprofile", "list", "KalturaCDNAdapterProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDNAdapterProfileListResponse')

    def update(self, adapterId, adapter):
        """Update CDN adapter details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("adapterId", adapterId);
        kparams.addObjectIfDefined("adapter", adapter)
        self.client.queueServiceActionCall("cdnadapterprofile", "update", "KalturaCDNAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDNAdapterProfile')


# @package Kaltura
# @subpackage Client
class KalturaCdnPartnerSettingsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self):
        """Retrieve the partner's CDN settings (default adapters)"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("cdnpartnersettings", "get", "KalturaCDNPartnerSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDNPartnerSettings')

    def update(self, settings):
        """Configure the partner's CDN settings (default adapters)"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("settings", settings)
        self.client.queueServiceActionCall("cdnpartnersettings", "update", "KalturaCDNPartnerSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDNPartnerSettings')


# @package Kaltura
# @subpackage Client
class KalturaCDVRAdapterProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, adapter):
        """Insert new C-DVR adapter for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("adapter", adapter)
        self.client.queueServiceActionCall("cdvradapterprofile", "add", "KalturaCDVRAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDVRAdapterProfile')

    def delete(self, adapterId):
        """Delete C-DVR adapter by C-DVR adapter id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("adapterId", adapterId);
        self.client.queueServiceActionCall("cdvradapterprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generateSharedSecret(self, adapterId):
        """Generate C-DVR adapter shared secret"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("adapterId", adapterId);
        self.client.queueServiceActionCall("cdvradapterprofile", "generateSharedSecret", "KalturaCDVRAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDVRAdapterProfile')

    def list(self):
        """Returns all C-DVR adapters for partner"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("cdvradapterprofile", "list", "KalturaCDVRAdapterProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDVRAdapterProfileListResponse')

    def update(self, adapterId, adapter):
        """Update C-DVR adapter details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("adapterId", adapterId);
        kparams.addObjectIfDefined("adapter", adapter)
        self.client.queueServiceActionCall("cdvradapterprofile", "update", "KalturaCDVRAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCDVRAdapterProfile')


# @package Kaltura
# @subpackage Client
class KalturaChannelService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, channel):
        """Insert new channel for partner. Currently supports only KSQL channel"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("channel", channel)
        self.client.queueServiceActionCall("channel", "add", "KalturaChannel", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaChannel')

    def delete(self, channelId):
        """Delete channel by its channel id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("channelId", channelId);
        self.client.queueServiceActionCall("channel", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Returns channel info"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("channel", "get", "KalturaChannel", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaChannel')

    def update(self, channelId, channel):
        """Update channel details. Currently supports only KSQL channel"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("channelId", channelId);
        kparams.addObjectIfDefined("channel", channel)
        self.client.queueServiceActionCall("channel", "update", "KalturaChannel", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaChannel')


# @package Kaltura
# @subpackage Client
class KalturaCollectionService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Returns a list of subscriptions requested by Subscription ID or file ID"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("collection", "list", "KalturaCollectionListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCollectionListResponse')


# @package Kaltura
# @subpackage Client
class KalturaCompensationService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, compensation):
        """Adds a new compensation for a household for a given number of iterations of a subscription renewal for a fixed amount / percentage of the renewal price."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("compensation", compensation)
        self.client.queueServiceActionCall("compensation", "add", "KalturaCompensation", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCompensation')

    def delete(self, id):
        """Delete a compensation by identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("compensation", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()

    def get(self, id):
        """Get a compensation by identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("compensation", "get", "KalturaCompensation", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCompensation')


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, configurationGroup):
        """Add a new configuration group"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("configurationGroup", configurationGroup)
        self.client.queueServiceActionCall("configurationgroup", "add", "KalturaConfigurationGroup", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroup')

    def delete(self, id):
        """Remove a configuration group, including its tags, device configurations and devices associations"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("configurationgroup", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Return the configuration group details, including group identifiers, tags, and number of associated devices, and list of device configuration"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("configurationgroup", "get", "KalturaConfigurationGroup", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroup')

    def list(self):
        """Return the list of configuration groups"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("configurationgroup", "list", "KalturaConfigurationGroupListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroupListResponse')

    def update(self, id, configurationGroup):
        """Update configuration group name"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addObjectIfDefined("configurationGroup", configurationGroup)
        self.client.queueServiceActionCall("configurationgroup", "update", "KalturaConfigurationGroup", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroup')


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupDeviceService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, configurationGroupDevice):
        """Associate a collection of devices to a configuration group. If a device is already associated to another group - old association is replaced"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("configurationGroupDevice", configurationGroupDevice)
        self.client.queueServiceActionCall("configurationgroupdevice", "add", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def delete(self, udid):
        """Remove a device association"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("configurationgroupdevice", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, udid):
        """Return the configuration group to which a specific device is associated to"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("configurationgroupdevice", "get", "KalturaConfigurationGroupDevice", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroupDevice')

    def list(self, filter, pager = NotImplemented):
        """Return the list of associated devices for a given configuration group"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("configurationgroupdevice", "list", "KalturaConfigurationGroupDeviceListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroupDeviceListResponse')


# @package Kaltura
# @subpackage Client
class KalturaConfigurationGroupTagService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, configurationGroupTag):
        """Add a new tag to a configuration group. If this tag is already associated to another group, request fails"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("configurationGroupTag", configurationGroupTag)
        self.client.queueServiceActionCall("configurationgrouptag", "add", "KalturaConfigurationGroupTag", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroupTag')

    def delete(self, tag):
        """Remove a tag association from configuration group"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("tag", tag)
        self.client.queueServiceActionCall("configurationgrouptag", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, tag):
        """Return the configuration group the tag is associated to"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("tag", tag)
        self.client.queueServiceActionCall("configurationgrouptag", "get", "KalturaConfigurationGroupTag", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroupTag')

    def list(self, filter):
        """Return list of tags for a configuration group"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("configurationgrouptag", "list", "KalturaConfigurationGroupTagListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationGroupTagListResponse')


# @package Kaltura
# @subpackage Client
class KalturaConfigurationsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, configurations):
        """Add a new device configuration to a configuration group"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("configurations", configurations)
        self.client.queueServiceActionCall("configurations", "add", "KalturaConfigurations", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurations')

    def delete(self, id):
        """Delete a device configuration"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("configurations", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Return the device configuration"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("configurations", "get", "KalturaConfigurations", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurations')

    def list(self, filter):
        """Return a list of device configurations of a configuration group"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("configurations", "list", "KalturaConfigurationsListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurationsListResponse')

    def serveByDevice(self, applicationName, clientVersion, platform, udid, tag, partnerId = 0):
        """Return a device configuration applicable for a specific device (UDID), app name, software version, platform and optionally a configuration group's tag"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("applicationName", applicationName)
        kparams.addStringIfDefined("clientVersion", clientVersion)
        kparams.addStringIfDefined("platform", platform)
        kparams.addStringIfDefined("udid", udid)
        kparams.addStringIfDefined("tag", tag)
        kparams.addIntIfDefined("partnerId", partnerId);
        self.client.queueServiceActionCall('configurations', 'serveByDevice', None ,kparams)
        return self.client.getServeUrl()

    def update(self, id, configurations):
        """Update device configuration"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addObjectIfDefined("configurations", configurations)
        self.client.queueServiceActionCall("configurations", "update", "KalturaConfigurations", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaConfigurations')


# @package Kaltura
# @subpackage Client
class KalturaCountryService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Get the list of countries for the partner with option to filter by countries identifiers"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("country", "list", "KalturaCountryListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCountryListResponse')


# @package Kaltura
# @subpackage Client
class KalturaCouponService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, code):
        """Returns information about a coupon"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("code", code)
        self.client.queueServiceActionCall("coupon", "get", "KalturaCoupon", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCoupon')


# @package Kaltura
# @subpackage Client
class KalturaCurrencyService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Get the list of currencies for the partner with option to filter by currency codes"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("currency", "list", "KalturaCurrencyListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCurrencyListResponse')


# @package Kaltura
# @subpackage Client
class KalturaDeviceBrandService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self):
        """Return a list of the available device brands."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("devicebrand", "list", "KalturaDeviceBrandListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaDeviceBrandListResponse')


# @package Kaltura
# @subpackage Client
class KalturaDeviceFamilyService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self):
        """Return a list of the available device families."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("devicefamily", "list", "KalturaDeviceFamilyListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaDeviceFamilyListResponse')


# @package Kaltura
# @subpackage Client
class KalturaEmailService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def send(self, emailMessage):
        """Sends email notification"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("emailMessage", emailMessage)
        self.client.queueServiceActionCall("email", "send", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaEngagementAdapterService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, engagementAdapter):
        """Insert new Engagement adapter for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("engagementAdapter", engagementAdapter)
        self.client.queueServiceActionCall("engagementadapter", "add", "KalturaEngagementAdapter", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagementAdapter')

    def delete(self, id):
        """Delete Engagement adapter by Engagement adapter id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("engagementadapter", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generateSharedSecret(self, id):
        """Generate engagement adapter shared secret"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("engagementadapter", "generateSharedSecret", "KalturaEngagementAdapter", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagementAdapter')

    def get(self, id):
        """Returns all Engagement adapters for partner : id + name"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("engagementadapter", "get", "KalturaEngagementAdapter", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagementAdapter')

    def list(self):
        """Returns all Engagement adapters for partner : id + name"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("engagementadapter", "list", "KalturaEngagementAdapterListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagementAdapterListResponse')

    def update(self, id, engagementAdapter):
        """Update Engagement adapter details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addObjectIfDefined("engagementAdapter", engagementAdapter)
        self.client.queueServiceActionCall("engagementadapter", "update", "KalturaEngagementAdapter", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagementAdapter')


# @package Kaltura
# @subpackage Client
class KalturaEngagementService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, engagement):
        """Insert new Engagement for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("engagement", engagement)
        self.client.queueServiceActionCall("engagement", "add", "KalturaEngagement", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagement')

    def delete(self, id):
        """Delete engagement by engagement adapter id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("engagement", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Return engagement"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("engagement", "get", "KalturaEngagement", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagement')

    def list(self, filter):
        """Returns all Engagement for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("engagement", "list", "KalturaEngagementListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEngagementListResponse')


# @package Kaltura
# @subpackage Client
class KalturaEntitlementService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def cancel(self, assetId, productType):
        """Immediately cancel a subscription, PPV or collection. Cancel is possible only if within cancellation window and content not already consumed"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("assetId", assetId);
        kparams.addStringIfDefined("productType", productType)
        self.client.queueServiceActionCall("entitlement", "cancel", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def cancelRenewal(self, subscriptionId):
        """Cancel a household service subscription at the next renewal. The subscription stays valid till the next renewal."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("subscriptionId", subscriptionId)
        self.client.queueServiceActionCall("entitlement", "cancelRenewal", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()

    def cancelScheduledSubscription(self, scheduledSubscriptionId):
        """Cancel Scheduled Subscription"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("scheduledSubscriptionId", scheduledSubscriptionId);
        self.client.queueServiceActionCall("entitlement", "cancelScheduledSubscription", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def externalReconcile(self):
        """Reconcile the user household&#39;s entitlements with an external entitlements source. This request is frequency protected to avoid too frequent calls per household."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("entitlement", "externalReconcile", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def forceCancel(self, assetId, productType):
        """Immediately cancel a subscription, PPV or collection. Cancel applies regardless of cancellation window and content consumption status"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("assetId", assetId);
        kparams.addStringIfDefined("productType", productType)
        self.client.queueServiceActionCall("entitlement", "forceCancel", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def getNextRenewal(self, id):
        """Returns the data about the next renewal"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("entitlement", "getNextRenewal", "KalturaEntitlementRenewal", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEntitlementRenewal')

    def grant(self, productId, productType, history, contentId = 0):
        """Grant household for an entitlement for a PPV or Subscription."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("productId", productId);
        kparams.addStringIfDefined("productType", productType)
        kparams.addBoolIfDefined("history", history);
        kparams.addIntIfDefined("contentId", contentId);
        self.client.queueServiceActionCall("entitlement", "grant", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter, pager = NotImplemented):
        """Gets all the entitled media items for a household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("entitlement", "list", "KalturaEntitlementListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEntitlementListResponse')

    def swap(self, currentProductId, newProductId, history):
        """Swap current entitlement (subscription) with new entitlement (subscription) - only Grant"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("currentProductId", currentProductId);
        kparams.addIntIfDefined("newProductId", newProductId);
        kparams.addBoolIfDefined("history", history);
        self.client.queueServiceActionCall("entitlement", "swap", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def update(self, id, entitlement):
        """Update Kaltura Entitelment by Purchase id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addObjectIfDefined("entitlement", entitlement)
        self.client.queueServiceActionCall("entitlement", "update", "KalturaEntitlement", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaEntitlement')


# @package Kaltura
# @subpackage Client
class KalturaExportTaskService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, task):
        """Adds a new bulk export task"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("task", task)
        self.client.queueServiceActionCall("exporttask", "add", "KalturaExportTask", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExportTask')

    def delete(self, id):
        """Deletes an existing bulk export task by task identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("exporttask", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Gets an existing bulk export task by task identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("exporttask", "get", "KalturaExportTask", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExportTask')

    def list(self, filter = NotImplemented):
        """Returns bulk export tasks by tasks identifiers"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("exporttask", "list", "KalturaExportTaskListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExportTaskListResponse')

    def update(self, id, task):
        """Updates an existing bulk export task by task identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addObjectIfDefined("task", task)
        self.client.queueServiceActionCall("exporttask", "update", "KalturaExportTask", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExportTask')


# @package Kaltura
# @subpackage Client
class KalturaExternalChannelProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, externalChannel):
        """Insert new External channel for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("externalChannel", externalChannel)
        self.client.queueServiceActionCall("externalchannelprofile", "add", "KalturaExternalChannelProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExternalChannelProfile')

    def delete(self, externalChannelId):
        """Delete External channel by External channel id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("externalChannelId", externalChannelId);
        self.client.queueServiceActionCall("externalchannelprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self):
        """Returns all External channels for partner"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("externalchannelprofile", "list", "KalturaExternalChannelProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExternalChannelProfileListResponse')

    def update(self, externalChannelId, externalChannel):
        """Update External channel details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("externalChannelId", externalChannelId);
        kparams.addObjectIfDefined("externalChannel", externalChannel)
        self.client.queueServiceActionCall("externalchannelprofile", "update", "KalturaExternalChannelProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaExternalChannelProfile')


# @package Kaltura
# @subpackage Client
class KalturaFavoriteService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, favorite):
        """Add media to user&#39;s favorite list"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("favorite", favorite)
        self.client.queueServiceActionCall("favorite", "add", "KalturaFavorite", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaFavorite')

    def delete(self, id):
        """Remove media from user&#39;s favorite list"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("favorite", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter = NotImplemented):
        """Retrieving users&#39; favorites"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("favorite", "list", "KalturaFavoriteListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaFavoriteListResponse')


# @package Kaltura
# @subpackage Client
class KalturaFollowTvSeriesService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, followTvSeries):
        """Add a user&#39;s tv series follow.
                    Possible status codes: UserAlreadyFollowing = 8013, NotFound = 500007, InvalidAssetId = 4024"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("followTvSeries", followTvSeries)
        self.client.queueServiceActionCall("followtvseries", "add", "KalturaFollowTvSeries", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaFollowTvSeries')

    def delete(self, assetId):
        """Delete a user&#39;s tv series follow.
                    Possible status codes: UserNotFollowing = 8012, NotFound = 500007, InvalidAssetId = 4024, AnnouncementNotFound = 8006"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("assetId", assetId);
        self.client.queueServiceActionCall("followtvseries", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter, pager = NotImplemented):
        """List user&#39;s tv series follows.
                    Possible status codes:"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("followtvseries", "list", "KalturaFollowTvSeriesListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaFollowTvSeriesListResponse')


# @package Kaltura
# @subpackage Client
class KalturaHomeNetworkService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, homeNetwork):
        """Add a new home network to a household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("homeNetwork", homeNetwork)
        self.client.queueServiceActionCall("homenetwork", "add", "KalturaHomeNetwork", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHomeNetwork')

    def delete(self, externalId):
        """Delete household's existing home network"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("externalId", externalId)
        self.client.queueServiceActionCall("homenetwork", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self):
        """Retrieve the household's home networks"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("homenetwork", "list", "KalturaHomeNetworkListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHomeNetworkListResponse')

    def update(self, externalId, homeNetwork):
        """Update and existing home network for a household"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("externalId", externalId)
        kparams.addObjectIfDefined("homeNetwork", homeNetwork)
        self.client.queueServiceActionCall("homenetwork", "update", "KalturaHomeNetwork", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHomeNetwork')


# @package Kaltura
# @subpackage Client
class KalturaHouseholdService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, household):
        """Creates a household for the user"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("household", household)
        self.client.queueServiceActionCall("household", "add", "KalturaHousehold", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHousehold')

    def delete(self, id = NotImplemented):
        """Fully delete a household. Delete all of the household information, including users, devices, entitlements, payment methods and notification date."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("household", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id = NotImplemented):
        """Returns the household model"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("household", "get", "KalturaHousehold", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHousehold')

    def purge(self, id):
        """Purge a household. Delete all of the household information, including users, devices, entitlements, payment methods and notification date."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("household", "purge", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def resetFrequency(self, frequencyType):
        """Reset a household's time limitation for removing user or device"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("frequencyType", frequencyType)
        self.client.queueServiceActionCall("household", "resetFrequency", "KalturaHousehold", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHousehold')

    def resume(self):
        """Resumed a given household service to its previous service settings"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("household", "resume", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def suspend(self, roleId = NotImplemented):
        """Suspend a given household service. Sets the household status to "suspended&quot;.The household service settings are maintained for later resume"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("roleId", roleId);
        self.client.queueServiceActionCall("household", "suspend", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def update(self, household):
        """Update the household name and description"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("household", household)
        self.client.queueServiceActionCall("household", "update", "KalturaHousehold", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHousehold')


# @package Kaltura
# @subpackage Client
class KalturaHouseholdDeviceService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, device):
        """Add device to household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("device", device)
        self.client.queueServiceActionCall("householddevice", "add", "KalturaHouseholdDevice", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdDevice')

    def addByPin(self, deviceName, pin):
        """Registers a device to a household using pin code"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("deviceName", deviceName)
        kparams.addStringIfDefined("pin", pin)
        self.client.queueServiceActionCall("householddevice", "addByPin", "KalturaHouseholdDevice", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdDevice')

    def delete(self, udid):
        """Removes a device from household"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("householddevice", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generatePin(self, udid, brandId):
        """Generates device pin to use when adding a device to household by pin"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        kparams.addIntIfDefined("brandId", brandId);
        self.client.queueServiceActionCall("householddevice", "generatePin", "KalturaDevicePin", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaDevicePin')

    def get(self):
        """Returns device registration status to the supplied household"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("householddevice", "get", "KalturaHouseholdDevice", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdDevice')

    def list(self, filter = NotImplemented):
        """Returns the devices within the household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("householddevice", "list", "KalturaHouseholdDeviceListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdDeviceListResponse')

    def loginWithPin(self, partnerId, pin, udid = NotImplemented):
        """User sign-in via a time-expired sign-in PIN."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("pin", pin)
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("householddevice", "loginWithPin", "KalturaLoginResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLoginResponse')

    def update(self, udid, device):
        """Update the name of the device by UDID"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        kparams.addObjectIfDefined("device", device)
        self.client.queueServiceActionCall("householddevice", "update", "KalturaHouseholdDevice", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdDevice')

    def updateStatus(self, udid, status):
        """Update the name of the device by UDID"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        kparams.addStringIfDefined("status", status)
        self.client.queueServiceActionCall("householddevice", "updateStatus", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaHouseholdLimitationsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, id):
        """Get the limitation module by id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("householdlimitations", "get", "KalturaHouseholdLimitations", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdLimitations')


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentGatewayService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def disable(self, paymentGatewayId):
        """Disable payment-gateway on the household"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        self.client.queueServiceActionCall("householdpaymentgateway", "disable", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def enable(self, paymentGatewayId):
        """Enable a payment-gateway provider for the household."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        self.client.queueServiceActionCall("householdpaymentgateway", "enable", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def getChargeID(self, paymentGatewayExternalId):
        """Get a household's billing account identifier (charge ID) for a given payment gateway"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("paymentGatewayExternalId", paymentGatewayExternalId)
        self.client.queueServiceActionCall("householdpaymentgateway", "getChargeID", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeText(resultNode)

    def invoke(self, paymentGatewayId, intent, extraParameters):
        """Gets the Payment Gateway Configuration for the payment gateway identifier given"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        kparams.addStringIfDefined("intent", intent)
        kparams.addArrayIfDefined("extraParameters", extraParameters)
        self.client.queueServiceActionCall("householdpaymentgateway", "invoke", "KalturaPaymentGatewayConfiguration", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentGatewayConfiguration')

    def list(self):
        """Get a list of all configured Payment Gateways providers available for the account. For each payment is provided with the household associated payment methods."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("householdpaymentgateway", "list", "KalturaHouseholdPaymentGatewayListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdPaymentGatewayListResponse')

    def resume(self, paymentGatewayId):
        """Resumes all the entitlements of the given payment gateway"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        self.client.queueServiceActionCall("householdpaymentgateway", "resume", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()

    def setChargeID(self, paymentGatewayExternalId, chargeId):
        """Set user billing account identifier (charge ID), for a specific household and a specific payment gateway"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("paymentGatewayExternalId", paymentGatewayExternalId)
        kparams.addStringIfDefined("chargeId", chargeId)
        self.client.queueServiceActionCall("householdpaymentgateway", "setChargeID", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def suspend(self, paymentGatewayId):
        """Suspends all the entitlements of the given payment gateway"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        self.client.queueServiceActionCall("householdpaymentgateway", "suspend", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPaymentMethodService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, householdPaymentMethod):
        """Add a new payment method for household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("householdPaymentMethod", householdPaymentMethod)
        self.client.queueServiceActionCall("householdpaymentmethod", "add", "KalturaHouseholdPaymentMethod", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdPaymentMethod')

    def forceRemove(self, paymentGatewayId, paymentMethodId):
        """Force remove of a payment method of the household."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        kparams.addIntIfDefined("paymentMethodId", paymentMethodId);
        self.client.queueServiceActionCall("householdpaymentmethod", "forceRemove", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self):
        """Get a list of all payment methods of the household."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("householdpaymentmethod", "list", "KalturaHouseholdPaymentMethodListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdPaymentMethodListResponse')

    def remove(self, paymentGatewayId, paymentMethodId):
        """Removes a payment method of the household."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        kparams.addIntIfDefined("paymentMethodId", paymentMethodId);
        self.client.queueServiceActionCall("householdpaymentmethod", "remove", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def setAsDefault(self, paymentGatewayId, paymentMethodId):
        """Set a payment method as default for the household."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        kparams.addIntIfDefined("paymentMethodId", paymentMethodId);
        self.client.queueServiceActionCall("householdpaymentmethod", "setAsDefault", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaHouseholdPremiumServiceService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self):
        """Returns all the premium services allowed for the household"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("householdpremiumservice", "list", "KalturaHouseholdPremiumServiceListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdPremiumServiceListResponse')


# @package Kaltura
# @subpackage Client
class KalturaHouseholdQuotaService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self):
        """Returns the household&#39;s quota data"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("householdquota", "get", "KalturaHouseholdQuota", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdQuota')


# @package Kaltura
# @subpackage Client
class KalturaHouseholdUserService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, householdUser):
        """Adds a user to household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("householdUser", householdUser)
        self.client.queueServiceActionCall("householduser", "add", "KalturaHouseholdUser", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdUser')

    def delete(self, id):
        """Removes a user from household"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("householduser", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter = NotImplemented):
        """Returns the users within the household"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("householduser", "list", "KalturaHouseholdUserListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaHouseholdUserListResponse')


# @package Kaltura
# @subpackage Client
class KalturaInboxMessageService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, id):
        """TBD"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("inboxmessage", "get", "KalturaInboxMessage", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaInboxMessage')

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """List inbox messages"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("inboxmessage", "list", "KalturaInboxMessageListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaInboxMessageListResponse')

    def updateStatus(self, id, status):
        """Updates the message status."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addStringIfDefined("status", status)
        self.client.queueServiceActionCall("inboxmessage", "updateStatus", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaLanguageService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Get the list of languages for the partner with option to filter by language codes"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("language", "list", "KalturaLanguageListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLanguageListResponse')


# @package Kaltura
# @subpackage Client
class KalturaLicensedUrlService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, request):
        """Get the URL for playing an asset - program, media or recording"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("request", request)
        self.client.queueServiceActionCall("licensedurl", "get", "KalturaLicensedUrl", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLicensedUrl')


# @package Kaltura
# @subpackage Client
class KalturaMessageTemplateService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, messageType):
        """Retrieve a message template used in push notifications and inbox"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("messageType", messageType)
        self.client.queueServiceActionCall("messagetemplate", "get", "KalturaMessageTemplate", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaMessageTemplate')

    def update(self, messageType, template):
        """Set the account's push notifications and inbox messages templates"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("messageType", messageType)
        kparams.addObjectIfDefined("template", template)
        self.client.queueServiceActionCall("messagetemplate", "update", "KalturaMessageTemplate", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaMessageTemplate')


# @package Kaltura
# @subpackage Client
class KalturaMetaService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter = NotImplemented):
        """Get the list of meta mappings for the partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("meta", "list", "KalturaMetaListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaMetaListResponse')

    def update(self, id, meta):
        """Update meta&#39;s user interest"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        kparams.addObjectIfDefined("meta", meta)
        self.client.queueServiceActionCall("meta", "update", "KalturaMeta", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaMeta')


# @package Kaltura
# @subpackage Client
class KalturaNotificationService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def register(self, identifier, type):
        """TBD"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("identifier", identifier)
        kparams.addStringIfDefined("type", type)
        self.client.queueServiceActionCall("notification", "register", "KalturaRegistryResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRegistryResponse')

    def sendPush(self, userId, pushMessage):
        """Sends push notification to user devices"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("userId", userId);
        kparams.addObjectIfDefined("pushMessage", pushMessage)
        self.client.queueServiceActionCall("notification", "sendPush", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def setDevicePushToken(self, pushToken):
        """Registers the device push token to the push service"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("pushToken", pushToken)
        self.client.queueServiceActionCall("notification", "setDevicePushToken", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaNotificationsPartnerSettingsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self):
        """Retrieve the partner notification settings."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("notificationspartnersettings", "get", "KalturaNotificationsPartnerSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaNotificationsPartnerSettings')

    def update(self, settings):
        """Update the account notification settings"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("settings", settings)
        self.client.queueServiceActionCall("notificationspartnersettings", "update", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaNotificationsSettingsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self):
        """Retrieve the user's notification settings."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("notificationssettings", "get", "KalturaNotificationsSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaNotificationsSettings')

    def update(self, settings):
        """Update the user's notification settings."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("settings", settings)
        self.client.queueServiceActionCall("notificationssettings", "update", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaOssAdapterProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, ossAdapter):
        """Insert new OSS adapter for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("ossAdapter", ossAdapter)
        self.client.queueServiceActionCall("ossadapterprofile", "add", "KalturaOSSAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOSSAdapterProfile')

    def delete(self, ossAdapterId):
        """Delete OSS adapter by OSS adapter id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("ossAdapterId", ossAdapterId);
        self.client.queueServiceActionCall("ossadapterprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generateSharedSecret(self, ossAdapterId):
        """Generate oss adapter shared secret"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("ossAdapterId", ossAdapterId);
        self.client.queueServiceActionCall("ossadapterprofile", "generateSharedSecret", "KalturaOSSAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOSSAdapterProfile')

    def get(self, id):
        """Returns all OSS adapters for partner : id + name"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("ossadapterprofile", "get", "KalturaOSSAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOSSAdapterProfile')

    def list(self):
        """Returns all OSS adapters for partner : id + name"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("ossadapterprofile", "list", "KalturaOSSAdapterProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOSSAdapterProfileListResponse')

    def update(self, ossAdapterId, ossAdapter):
        """Update OSS adapter details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("ossAdapterId", ossAdapterId);
        kparams.addObjectIfDefined("ossAdapter", ossAdapter)
        self.client.queueServiceActionCall("ossadapterprofile", "update", "KalturaOSSAdapterProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOSSAdapterProfile')


# @package Kaltura
# @subpackage Client
class KalturaOttCategoryService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, id):
        """Retrieve the list of categories (hierarchical) and their associated channels"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("ottcategory", "get", "KalturaOTTCategory", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTCategory')


# @package Kaltura
# @subpackage Client
class KalturaOttUserService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def activate(self, partnerId, username, activationToken):
        """Activate the account by activation token"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("username", username)
        kparams.addStringIfDefined("activationToken", activationToken)
        self.client.queueServiceActionCall("ottuser", "activate", "KalturaOTTUser", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUser')

    def addRole(self, roleId):
        """Edit user details."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("roleId", roleId);
        self.client.queueServiceActionCall("ottuser", "addRole", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def anonymousLogin(self, partnerId, udid = NotImplemented):
        """Returns tokens (KS and refresh token) for anonymous access"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("ottuser", "anonymousLogin", "KalturaLoginSession", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLoginSession')

    def delete(self):
        """Permanently delete a user. User to delete cannot be an exclusive household master, and cannot be default user."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("ottuser", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self):
        """Retrieving users&#39; data"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("ottuser", "get", "KalturaOTTUser", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUser')

    def getEncryptedUserId(self):
        """Returns the identifier of the user encrypted with SHA1 using configured key"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("ottuser", "getEncryptedUserId", "KalturaStringValue", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaStringValue')

    def list(self, filter = NotImplemented):
        """Retrieve user by external identifier or username or if filter is null all user in the master or the user itself"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("ottuser", "list", "KalturaOTTUserListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUserListResponse')

    def login(self, partnerId, username = NotImplemented, password = NotImplemented, extraParams = NotImplemented, udid = NotImplemented):
        """login with user name and password."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("username", username)
        kparams.addStringIfDefined("password", password)
        kparams.addMapIfDefined("extraParams", extraParams)
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("ottuser", "login", "KalturaLoginResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLoginResponse')

    def loginWithPin(self, partnerId, pin, udid = NotImplemented, secret = NotImplemented):
        """User sign-in via a time-expired sign-in PIN."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("pin", pin)
        kparams.addStringIfDefined("udid", udid)
        kparams.addStringIfDefined("secret", secret)
        self.client.queueServiceActionCall("ottuser", "loginWithPin", "KalturaLoginResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLoginResponse')

    def logout(self):
        """Logout the calling user."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("ottuser", "logout", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def register(self, partnerId, user, password):
        """Sign up a new user."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addObjectIfDefined("user", user)
        kparams.addStringIfDefined("password", password)
        self.client.queueServiceActionCall("ottuser", "register", "KalturaOTTUser", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUser')

    def resendActivationToken(self, partnerId, username):
        """Resend the activation token to a user"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("username", username)
        self.client.queueServiceActionCall("ottuser", "resendActivationToken", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def resetPassword(self, partnerId, username):
        """Send an e-mail with URL to enable the user to set new password."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("username", username)
        self.client.queueServiceActionCall("ottuser", "resetPassword", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def setInitialPassword(self, partnerId, token, password):
        """Renew the user&#39;s password after validating the token that sent as part of URL in e-mail."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("token", token)
        kparams.addStringIfDefined("password", password)
        self.client.queueServiceActionCall("ottuser", "setInitialPassword", "KalturaOTTUser", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUser')

    def update(self, user, id = NotImplemented):
        """Update user information"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("user", user)
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("ottuser", "update", "KalturaOTTUser", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUser')

    def updateDynamicData(self, key, value):
        """Update user dynamic data"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("key", key)
        kparams.addObjectIfDefined("value", value)
        self.client.queueServiceActionCall("ottuser", "updateDynamicData", "KalturaOTTUserDynamicData", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaOTTUserDynamicData')

    def updateLoginData(self, username, oldPassword, newPassword):
        """Given a user name and existing password, change to a new password."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("username", username)
        kparams.addStringIfDefined("oldPassword", oldPassword)
        kparams.addStringIfDefined("newPassword", newPassword)
        self.client.queueServiceActionCall("ottuser", "updateLoginData", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def updatePassword(self, userId, password):
        """Update the user&#39;s existing password."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("userId", userId);
        kparams.addStringIfDefined("password", password)
        self.client.queueServiceActionCall("ottuser", "updatePassword", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()


# @package Kaltura
# @subpackage Client
class KalturaParentalRuleService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def disable(self, ruleId, entityReference):
        """Disables a parental rule that was previously defined by the household master. Disable can be at specific user or household level."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("ruleId", ruleId);
        kparams.addStringIfDefined("entityReference", entityReference)
        self.client.queueServiceActionCall("parentalrule", "disable", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def disableDefault(self, entityReference):
        """Disables a parental rule that was defined at account level. Disable can be at specific user or household level."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("entityReference", entityReference)
        self.client.queueServiceActionCall("parentalrule", "disableDefault", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def enable(self, ruleId, entityReference):
        """Enable a parental rules for a user"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("ruleId", ruleId);
        kparams.addStringIfDefined("entityReference", entityReference)
        self.client.queueServiceActionCall("parentalrule", "enable", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter):
        """Return the parental rules that applies for the user or household. Can include rules that have been associated in account, household, or user level.
                    Association level is also specified in the response."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("parentalrule", "list", "KalturaParentalRuleListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaParentalRuleListResponse')


# @package Kaltura
# @subpackage Client
class KalturaPartnerConfigurationService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def update(self, configuration):
        """Update Partner Configuration"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("configuration", configuration)
        self.client.queueServiceActionCall("partnerconfiguration", "update", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaPaymentGatewayProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, paymentGateway):
        """Insert new payment gateway for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("paymentGateway", paymentGateway)
        self.client.queueServiceActionCall("paymentgatewayprofile", "add", "KalturaPaymentGatewayProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentGatewayProfile')

    def delete(self, paymentGatewayId):
        """Delete payment gateway by payment gateway id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        self.client.queueServiceActionCall("paymentgatewayprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generateSharedSecret(self, paymentGatewayId):
        """Generate payment gateway shared secret"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        self.client.queueServiceActionCall("paymentgatewayprofile", "generateSharedSecret", "KalturaPaymentGatewayProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentGatewayProfile')

    def getConfiguration(self, alias, intent, extraParameters):
        """Gets the Payment Gateway Configuration for the payment gateway identifier given"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("alias", alias)
        kparams.addStringIfDefined("intent", intent)
        kparams.addArrayIfDefined("extraParameters", extraParameters)
        self.client.queueServiceActionCall("paymentgatewayprofile", "getConfiguration", "KalturaPaymentGatewayConfiguration", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentGatewayConfiguration')

    def list(self):
        """Returns all payment gateways for partner : id + name"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("paymentgatewayprofile", "list", "KalturaPaymentGatewayProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentGatewayProfileListResponse')

    def update(self, paymentGatewayId, paymentGateway):
        """Update payment gateway details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentGatewayId", paymentGatewayId);
        kparams.addObjectIfDefined("paymentGateway", paymentGateway)
        self.client.queueServiceActionCall("paymentgatewayprofile", "update", "KalturaPaymentGatewayProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentGatewayProfile')


# @package Kaltura
# @subpackage Client
class KalturaPaymentMethodProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, paymentMethod):
        """TBD"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("paymentMethod", paymentMethod)
        self.client.queueServiceActionCall("paymentmethodprofile", "add", "KalturaPaymentMethodProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentMethodProfile')

    def delete(self, paymentMethodId):
        """Delete payment method profile"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentMethodId", paymentMethodId);
        self.client.queueServiceActionCall("paymentmethodprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter):
        """TBD"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("paymentmethodprofile", "list", "KalturaPaymentMethodProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentMethodProfileListResponse')

    def update(self, paymentMethodId, paymentMethod):
        """Update payment method"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("paymentMethodId", paymentMethodId);
        kparams.addObjectIfDefined("paymentMethod", paymentMethod)
        self.client.queueServiceActionCall("paymentmethodprofile", "update", "KalturaPaymentMethodProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPaymentMethodProfile')


# @package Kaltura
# @subpackage Client
class KalturaPersonalFeedService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter, pager = NotImplemented):
        """List user&#39;s feeds.
                    Possible status codes:"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("personalfeed", "list", "KalturaPersonalFeedListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPersonalFeedListResponse')


# @package Kaltura
# @subpackage Client
class KalturaPinService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, by, type, ruleId = NotImplemented):
        """Retrieve the parental or purchase PIN that applies for the household or user. Includes specification of where the PIN was defined at - account, household or user  level"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("by", by)
        kparams.addStringIfDefined("type", type)
        kparams.addIntIfDefined("ruleId", ruleId);
        self.client.queueServiceActionCall("pin", "get", "KalturaPin", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPin')

    def update(self, by, type, pin, ruleId = NotImplemented):
        """Set the parental or purchase PIN that applies for the user or the household."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("by", by)
        kparams.addStringIfDefined("type", type)
        kparams.addObjectIfDefined("pin", pin)
        kparams.addIntIfDefined("ruleId", ruleId);
        self.client.queueServiceActionCall("pin", "update", "KalturaPin", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPin')

    def validate(self, pin, type, ruleId = NotImplemented):
        """Validate a purchase or parental PIN for a user."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("pin", pin)
        kparams.addStringIfDefined("type", type)
        kparams.addIntIfDefined("ruleId", ruleId);
        self.client.queueServiceActionCall("pin", "validate", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaPpvService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, id):
        """Returns ppv object by internal identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("ppv", "get", "KalturaPpv", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPpv')


# @package Kaltura
# @subpackage Client
class KalturaPriceDetailsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter = NotImplemented):
        """Returns the list of available prices, can be filtered by price IDs"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("pricedetails", "list", "KalturaPriceDetailsListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPriceDetailsListResponse')


# @package Kaltura
# @subpackage Client
class KalturaPricePlanService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter = NotImplemented):
        """Returns a list of price plans by IDs"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("priceplan", "list", "KalturaPricePlanListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPricePlanListResponse')

    def update(self, id, pricePlan):
        """Updates a price plan"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addObjectIfDefined("pricePlan", pricePlan)
        self.client.queueServiceActionCall("priceplan", "update", "KalturaPricePlan", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPricePlan')


# @package Kaltura
# @subpackage Client
class KalturaProductPriceService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Returns a price and a purchase status for each subscription or/and media file, for a given user (if passed) and with the consideration of a coupon code (if passed)."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("productprice", "list", "KalturaProductPriceListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaProductPriceListResponse')


# @package Kaltura
# @subpackage Client
class KalturaPurchaseSettingsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, by):
        """Retrieve the purchase settings.
                    Includes specification of where these settings were defined - account, household or user"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("by", by)
        self.client.queueServiceActionCall("purchasesettings", "get", "KalturaPurchaseSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPurchaseSettings')

    def update(self, entityReference, settings):
        """Set a purchase PIN for the household or user"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("entityReference", entityReference)
        kparams.addObjectIfDefined("settings", settings)
        self.client.queueServiceActionCall("purchasesettings", "update", "KalturaPurchaseSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaPurchaseSettings')


# @package Kaltura
# @subpackage Client
class KalturaRecommendationProfileService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, recommendationEngine):
        """Insert new recommendation engine for partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("recommendationEngine", recommendationEngine)
        self.client.queueServiceActionCall("recommendationprofile", "add", "KalturaRecommendationProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecommendationProfile')

    def delete(self, id):
        """Delete recommendation engine by recommendation engine id"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("recommendationprofile", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def generateSharedSecret(self, recommendationEngineId):
        """Generate recommendation engine  shared secret"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("recommendationEngineId", recommendationEngineId);
        self.client.queueServiceActionCall("recommendationprofile", "generateSharedSecret", "KalturaRecommendationProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecommendationProfile')

    def list(self):
        """Returns all recommendation engines for partner"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("recommendationprofile", "list", "KalturaRecommendationProfileListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecommendationProfileListResponse')

    def update(self, recommendationEngineId, recommendationEngine):
        """Update recommendation engine details"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("recommendationEngineId", recommendationEngineId);
        kparams.addObjectIfDefined("recommendationEngine", recommendationEngine)
        self.client.queueServiceActionCall("recommendationprofile", "update", "KalturaRecommendationProfile", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecommendationProfile')


# @package Kaltura
# @subpackage Client
class KalturaRecordingService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, recording):
        """Issue a record request for a program"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("recording", recording)
        self.client.queueServiceActionCall("recording", "add", "KalturaRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecording')

    def cancel(self, id):
        """Cancel a previously requested recording. Cancel recording can be called for recording in status Scheduled or Recording Only"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("recording", "cancel", "KalturaRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecording')

    def delete(self, id):
        """Delete one or more user recording(s). Delete recording can be called only for recordings in status Recorded"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("recording", "delete", "KalturaRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecording')

    def get(self, id):
        """Returns recording object by internal identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("recording", "get", "KalturaRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecording')

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Return a list of recordings for the household with optional filter by status and KSQL."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("recording", "list", "KalturaRecordingListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecordingListResponse')

    def protect(self, id):
        """Protects an existing recording from the cleanup process for the defined protection period"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("recording", "protect", "KalturaRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRecording')


# @package Kaltura
# @subpackage Client
class KalturaRegionService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Returns all regions for the partner"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("region", "list", "KalturaRegionListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRegionListResponse')


# @package Kaltura
# @subpackage Client
class KalturaRegistrySettingsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self):
        """Retrieve the registry settings."""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("registrysettings", "list", "KalturaRegistrySettingsListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaRegistrySettingsListResponse')


# @package Kaltura
# @subpackage Client
class KalturaReminderService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, reminder):
        """Add a new future reminder"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("reminder", reminder)
        self.client.queueServiceActionCall("reminder", "add", "KalturaReminder", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaReminder')

    def delete(self, id, type):
        """Delete a reminder. Reminder cannot be delete while being sent."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addStringIfDefined("type", type)
        self.client.queueServiceActionCall("reminder", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter, pager = NotImplemented):
        """Return a list of reminders with optional filter by KSQL."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("reminder", "list", "KalturaReminderListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaReminderListResponse')


# @package Kaltura
# @subpackage Client
class KalturaReportService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, udid):
        """Return a device configuration retrieval log request for a specific device."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("report", "get", "KalturaReport", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaReport')

    def list(self, filter, pager = NotImplemented):
        """Return device configurations retrieval log. Supports paging and can be filtered with the parameter &quot;FromData&quot;."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("report", "list", "KalturaReportListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaReportListResponse')


# @package Kaltura
# @subpackage Client
class KalturaSearchHistoryService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def clean(self, filter = NotImplemented):
        """Clean the user's search history"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("searchhistory", "clean", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def delete(self, id):
        """Delete a specific search history.
                    Possible error code: 2032 - ItemNotFound"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("searchhistory", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Get user&#39;s last search requests"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("searchhistory", "list", "KalturaSearchHistoryListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSearchHistoryListResponse')


# @package Kaltura
# @subpackage Client
class KalturaSeriesRecordingService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, recording):
        """Issue a record request for a complete season or series"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("recording", recording)
        self.client.queueServiceActionCall("seriesrecording", "add", "KalturaSeriesRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecording')

    def cancel(self, id):
        """Cancel a previously requested series recording. Cancel series recording can be called for recording in status Scheduled or Recording Only"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("seriesrecording", "cancel", "KalturaSeriesRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecording')

    def cancelByEpgId(self, id, epgId):
        """Cancel EPG recording that was recorded as part of series"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addIntIfDefined("epgId", epgId);
        self.client.queueServiceActionCall("seriesrecording", "cancelByEpgId", "KalturaSeriesRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecording')

    def cancelBySeasonNumber(self, id, seasonNumber):
        """Cancel Season recording epgs that was recorded as part of series"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addIntIfDefined("seasonNumber", seasonNumber);
        self.client.queueServiceActionCall("seriesrecording", "cancelBySeasonNumber", "KalturaSeriesRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecording')

    def delete(self, id):
        """Delete series recording(s). Delete series recording can be called recordings in any status"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("seriesrecording", "delete", "KalturaSeriesRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecording')

    def deleteBySeasonNumber(self, id, seasonNumber):
        """Delete Season recording epgs that was recorded as part of series"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addIntIfDefined("seasonNumber", seasonNumber);
        self.client.queueServiceActionCall("seriesrecording", "deleteBySeasonNumber", "KalturaSeriesRecording", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecording')

    def list(self, filter = NotImplemented):
        """Return a list of series recordings for the household with optional filter by status and KSQL."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("seriesrecording", "list", "KalturaSeriesRecordingListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSeriesRecordingListResponse')


# @package Kaltura
# @subpackage Client
class KalturaSessionService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, session = NotImplemented):
        """Parses KS"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("session", session)
        self.client.queueServiceActionCall("session", "get", "KalturaSession", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSession')

    def revoke(self):
        """Revokes all the sessions (KS) of a given user"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("session", "revoke", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def switchUser(self, userIdToSwitch):
        """Switching the user in the session by generating a new session for a new user within the same household"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("userIdToSwitch", userIdToSwitch)
        self.client.queueServiceActionCall("session", "switchUser", "KalturaLoginSession", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLoginSession')


# @package Kaltura
# @subpackage Client
class KalturaSocialActionService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, socialAction):
        """Insert new user social action"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("socialAction", socialAction)
        self.client.queueServiceActionCall("socialaction", "add", "KalturaUserSocialActionResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserSocialActionResponse')

    def delete(self, id):
        """delete user social action"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("socialaction", "delete", "KalturaNetworkActionStatus", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.createArray(resultNode, 'KalturaNetworkActionStatus')

    def list(self, filter, pager = NotImplemented):
        """Get list of user social actions"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("socialaction", "list", "KalturaSocialActionListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocialActionListResponse')


# @package Kaltura
# @subpackage Client
class KalturaSocialCommentService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter, pager = NotImplemented):
        """Get a list of all social comments filtered by asset ID and social platform"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("socialcomment", "list", "KalturaSocialCommentListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocialCommentListResponse')


# @package Kaltura
# @subpackage Client
class KalturaSocialService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self, type):
        """List social accounts"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("type", type)
        self.client.queueServiceActionCall("social", "get", "KalturaSocial", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocial')

    def getByToken(self, partnerId, token, type):
        """Return the user object with social information according to a provided external social token"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("token", token)
        kparams.addStringIfDefined("type", type)
        self.client.queueServiceActionCall("social", "getByToken", "KalturaSocial", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocial')

    def getConfiguration(self, type, partnerId = NotImplemented):
        """Retrieve the social network's configuration information"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("type", type)
        kparams.addIntIfDefined("partnerId", partnerId);
        self.client.queueServiceActionCall("social", "getConfiguration", "KalturaSocialConfig", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocialConfig')

    def login(self, partnerId, token, type, udid = NotImplemented):
        """Login using social token"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("token", token)
        kparams.addStringIfDefined("type", type)
        kparams.addStringIfDefined("udid", udid)
        self.client.queueServiceActionCall("social", "login", "KalturaLoginResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaLoginResponse')

    def merge(self, token, type):
        """Connect an existing user in the system to an external social network user"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("token", token)
        kparams.addStringIfDefined("type", type)
        self.client.queueServiceActionCall("social", "merge", "KalturaSocial", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocial')

    def register(self, partnerId, token, type, email = NotImplemented):
        """Create a new user in the system using a provided external social token"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("partnerId", partnerId);
        kparams.addStringIfDefined("token", token)
        kparams.addStringIfDefined("type", type)
        kparams.addStringIfDefined("email", email)
        self.client.queueServiceActionCall("social", "register", "KalturaSocial", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocial')

    def unmerge(self, type):
        """Disconnect an existing user in the system from its external social network user"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("type", type)
        self.client.queueServiceActionCall("social", "unmerge", "KalturaSocial", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocial')

    def UpdateConfiguration(self, configuration):
        """Set the user social network's configuration information"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("configuration", configuration)
        self.client.queueServiceActionCall("social", "UpdateConfiguration", "KalturaSocialConfig", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocialConfig')


# @package Kaltura
# @subpackage Client
class KalturaSocialFriendActivityService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Get a list of the social friends activity for a user"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("socialfriendactivity", "list", "KalturaSocialFriendActivityListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSocialFriendActivityListResponse')


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Returns a list of subscriptions requested by Subscription ID or file ID"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("subscription", "list", "KalturaSubscriptionListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSubscriptionListResponse')

    def validateCoupon(self, id, code):
        """Returns information about a coupon for subscription"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addStringIfDefined("code", code)
        self.client.queueServiceActionCall("subscription", "validateCoupon", "KalturaCoupon", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaCoupon')


# @package Kaltura
# @subpackage Client
class KalturaSubscriptionSetService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, subscriptionSet):
        """Add a new subscriptionSet"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("subscriptionSet", subscriptionSet)
        self.client.queueServiceActionCall("subscriptionset", "add", "KalturaSubscriptionSet", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSubscriptionSet')

    def delete(self, id):
        """Delete a subscriptionSet"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("subscriptionset", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Get the subscriptionSet according to the Identifier"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("subscriptionset", "get", "KalturaSubscriptionSet", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSubscriptionSet')

    def list(self, filter = NotImplemented):
        """Returns a list of subscriptionSets requested by ids or subscription ids"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("subscriptionset", "list", "KalturaSubscriptionSetListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSubscriptionSetListResponse')

    def update(self, id, subscriptionSet):
        """Update the subscriptionSet"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addObjectIfDefined("subscriptionSet", subscriptionSet)
        self.client.queueServiceActionCall("subscriptionset", "update", "KalturaSubscriptionSet", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaSubscriptionSet')


# @package Kaltura
# @subpackage Client
class KalturaSystemService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def getTime(self):
        """Returns current server timestamp"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("system", "getTime", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeInt(resultNode)

    def getVersion(self):
        """Returns current server version"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("system", "getVersion", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeText(resultNode)

    def ping(self):
        """Returns true"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("system", "ping", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaTimeShiftedTvPartnerSettingsService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def get(self):
        """Retrieve the account's time-shifted TV settings (catch-up and C-DVR, Trick-play, Start-over)"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("timeshiftedtvpartnersettings", "get", "KalturaTimeShiftedTvPartnerSettings", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaTimeShiftedTvPartnerSettings')

    def update(self, settings):
        """Configure the account's time-shifted TV settings (catch-up and C-DVR, Trick-play, Start-over)"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("settings", settings)
        self.client.queueServiceActionCall("timeshiftedtvpartnersettings", "update", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaTopicService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def delete(self, id):
        """Deleted a topic"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("topic", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, id):
        """Gets a topic"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("topic", "get", "KalturaTopic", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaTopic')

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Get list of topics"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("topic", "list", "KalturaTopicListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaTopicListResponse')

    def updateStatus(self, id, automaticIssueNotification):
        """Updates a topic &quot;automatic issue notification&quot; behavior."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addStringIfDefined("automaticIssueNotification", automaticIssueNotification)
        self.client.queueServiceActionCall("topic", "updateStatus", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)


# @package Kaltura
# @subpackage Client
class KalturaTransactionService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def downgrade(self, purchase):
        """downgrade specific subscription for a household. entitlements will be updated on the existing subscription end date."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("purchase", purchase)
        self.client.queueServiceActionCall("transaction", "downgrade", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()

    def getPurchaseSessionId(self, purchaseSession):
        """Retrieve the purchase session identifier"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("purchaseSession", purchaseSession)
        self.client.queueServiceActionCall("transaction", "getPurchaseSessionId", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeInt(resultNode)

    def purchase(self, purchase):
        """Purchase specific product or subscription for a household. Upon successful charge entitlements to use the requested product or subscription are granted."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("purchase", purchase)
        self.client.queueServiceActionCall("transaction", "purchase", "KalturaTransaction", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaTransaction')

    def setWaiver(self, assetId, transactionType):
        """This method shall set the waiver flag on the user entitlement table and the waiver date field to the current date."""

        kparams = KalturaParams()
        kparams.addIntIfDefined("assetId", assetId);
        kparams.addStringIfDefined("transactionType", transactionType)
        self.client.queueServiceActionCall("transaction", "setWaiver", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def updateStatus(self, paymentGatewayId, externalTransactionId, signature, status):
        """Updates a pending purchase transaction state."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("paymentGatewayId", paymentGatewayId)
        kparams.addStringIfDefined("externalTransactionId", externalTransactionId)
        kparams.addStringIfDefined("signature", signature)
        kparams.addObjectIfDefined("status", status)
        self.client.queueServiceActionCall("transaction", "updateStatus", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()

    def upgrade(self, purchase):
        """upgrade specific subscription for a household. Upon successful charge entitlements to use the requested product or subscription are granted."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("purchase", purchase)
        self.client.queueServiceActionCall("transaction", "upgrade", "KalturaTransaction", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaTransaction')

    def validateReceipt(self, externalReceipt):
        """Verifies PPV/Subscription/Collection client purchase (such as InApp) and entitles the user."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("externalReceipt", externalReceipt)
        self.client.queueServiceActionCall("transaction", "validateReceipt", "KalturaTransaction", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaTransaction')


# @package Kaltura
# @subpackage Client
class KalturaTransactionHistoryService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter = NotImplemented, pager = NotImplemented):
        """Gets user or household transaction history."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        kparams.addObjectIfDefined("pager", pager)
        self.client.queueServiceActionCall("transactionhistory", "list", "KalturaBillingTransactionListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaBillingTransactionListResponse')


# @package Kaltura
# @subpackage Client
class KalturaUnifiedPaymentService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def getNextRenewal(self, id):
        """Returns the data about the next renewal"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("unifiedpayment", "getNextRenewal", "KalturaUnifiedPaymentRenewal", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUnifiedPaymentRenewal')


# @package Kaltura
# @subpackage Client
class KalturaUserAssetRuleService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def list(self, filter):
        """Retrieve all the rules (parental, geo, device or user-type) that applies for this user and asset."""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("userassetrule", "list", "KalturaUserAssetRuleListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserAssetRuleListResponse')


# @package Kaltura
# @subpackage Client
class KalturaUserAssetsListItemService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, userAssetsListItem):
        """Adds a new item to user's private asset list"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("userAssetsListItem", userAssetsListItem)
        self.client.queueServiceActionCall("userassetslistitem", "add", "KalturaUserAssetsListItem", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserAssetsListItem')

    def delete(self, assetId, listType):
        """Deletes an item from user's private asset list"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("assetId", assetId)
        kparams.addStringIfDefined("listType", listType)
        self.client.queueServiceActionCall("userassetslistitem", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def get(self, assetId, listType, itemType):
        """Get an item from user's private asset list"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("assetId", assetId)
        kparams.addStringIfDefined("listType", listType)
        kparams.addStringIfDefined("itemType", itemType)
        self.client.queueServiceActionCall("userassetslistitem", "get", "KalturaUserAssetsListItem", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserAssetsListItem')


# @package Kaltura
# @subpackage Client
class KalturaUserInterestService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, userInterest):
        """Insert new user interest for partner user"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("userInterest", userInterest)
        self.client.queueServiceActionCall("userinterest", "add", "KalturaUserInterest", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserInterest')

    def delete(self, id):
        """Delete new user interest for partner user"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("id", id)
        self.client.queueServiceActionCall("userinterest", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self):
        """Returns all Engagement for partner"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("userinterest", "list", "KalturaUserInterestListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserInterestListResponse')


# @package Kaltura
# @subpackage Client
class KalturaUserLoginPinService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, secret = NotImplemented):
        """Generate a time and usage expiry login-PIN that can allow a single login per PIN. If an active login-PIN already exists. Calling this API again for same user will add another login-PIN"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("secret", secret)
        self.client.queueServiceActionCall("userloginpin", "add", "KalturaUserLoginPin", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserLoginPin')

    def delete(self, pinCode):
        """Immediately deletes a given pre set login pin code for the user."""

        kparams = KalturaParams()
        kparams.addStringIfDefined("pinCode", pinCode)
        self.client.queueServiceActionCall("userloginpin", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def deleteAll(self):
        """Immediately expire all active login-PINs for a user"""

        kparams = KalturaParams()
        self.client.queueServiceActionCall("userloginpin", "deleteAll", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def update(self, pinCode, secret = NotImplemented):
        """Set a time and usage expiry login-PIN that can allow a single login per PIN. If an active login-PIN already exists. Calling this API again for same user will add another login-PIN"""

        kparams = KalturaParams()
        kparams.addStringIfDefined("pinCode", pinCode)
        kparams.addStringIfDefined("secret", secret)
        self.client.queueServiceActionCall("userloginpin", "update", "KalturaUserLoginPin", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserLoginPin')


# @package Kaltura
# @subpackage Client
class KalturaUserRoleService(KalturaServiceBase):
    def __init__(self, client = None):
        KalturaServiceBase.__init__(self, client)

    def add(self, role):
        """Creates a new role"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("role", role)
        self.client.queueServiceActionCall("userrole", "add", "KalturaUserRole", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserRole')

    def delete(self, id):
        """Delete role"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        self.client.queueServiceActionCall("userrole", "delete", "None", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return getXmlNodeBool(resultNode)

    def list(self, filter = NotImplemented):
        """Retrieving user roles by identifiers, if filter is empty, returns all partner roles"""

        kparams = KalturaParams()
        kparams.addObjectIfDefined("filter", filter)
        self.client.queueServiceActionCall("userrole", "list", "KalturaUserRoleListResponse", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserRoleListResponse')

    def update(self, id, role):
        """Update role"""

        kparams = KalturaParams()
        kparams.addIntIfDefined("id", id);
        kparams.addObjectIfDefined("role", role)
        self.client.queueServiceActionCall("userrole", "update", "KalturaUserRole", kparams)
        if self.client.isMultiRequest():
            return self.client.getMultiRequestResult()
        resultNode = self.client.doQueue()
        return KalturaObjectFactory.create(resultNode, 'KalturaUserRole')

########## main ##########
class KalturaCoreClient(KalturaClientPlugin):
    # KalturaCoreClient
    instance = None

    # @return KalturaCoreClient
    @staticmethod
    def get():
        if KalturaCoreClient.instance == None:
            KalturaCoreClient.instance = KalturaCoreClient()
        return KalturaCoreClient.instance

    # @return array<KalturaServiceBase>
    def getServices(self):
        return {
            'announcement': KalturaAnnouncementService,
            'appToken': KalturaAppTokenService,
            'assetComment': KalturaAssetCommentService,
            'asset': KalturaAssetService,
            'assetFile': KalturaAssetFileService,
            'assetHistory': KalturaAssetHistoryService,
            'assetStatistics': KalturaAssetStatisticsService,
            'bookmark': KalturaBookmarkService,
            'cdnAdapterProfile': KalturaCdnAdapterProfileService,
            'cdnPartnerSettings': KalturaCdnPartnerSettingsService,
            'cDVRAdapterProfile': KalturaCDVRAdapterProfileService,
            'channel': KalturaChannelService,
            'collection': KalturaCollectionService,
            'compensation': KalturaCompensationService,
            'configurationGroup': KalturaConfigurationGroupService,
            'configurationGroupDevice': KalturaConfigurationGroupDeviceService,
            'configurationGroupTag': KalturaConfigurationGroupTagService,
            'configurations': KalturaConfigurationsService,
            'country': KalturaCountryService,
            'coupon': KalturaCouponService,
            'currency': KalturaCurrencyService,
            'deviceBrand': KalturaDeviceBrandService,
            'deviceFamily': KalturaDeviceFamilyService,
            'email': KalturaEmailService,
            'engagementAdapter': KalturaEngagementAdapterService,
            'engagement': KalturaEngagementService,
            'entitlement': KalturaEntitlementService,
            'exportTask': KalturaExportTaskService,
            'externalChannelProfile': KalturaExternalChannelProfileService,
            'favorite': KalturaFavoriteService,
            'followTvSeries': KalturaFollowTvSeriesService,
            'homeNetwork': KalturaHomeNetworkService,
            'household': KalturaHouseholdService,
            'householdDevice': KalturaHouseholdDeviceService,
            'householdLimitations': KalturaHouseholdLimitationsService,
            'householdPaymentGateway': KalturaHouseholdPaymentGatewayService,
            'householdPaymentMethod': KalturaHouseholdPaymentMethodService,
            'householdPremiumService': KalturaHouseholdPremiumServiceService,
            'householdQuota': KalturaHouseholdQuotaService,
            'householdUser': KalturaHouseholdUserService,
            'inboxMessage': KalturaInboxMessageService,
            'language': KalturaLanguageService,
            'licensedUrl': KalturaLicensedUrlService,
            'messageTemplate': KalturaMessageTemplateService,
            'meta': KalturaMetaService,
            'notification': KalturaNotificationService,
            'notificationsPartnerSettings': KalturaNotificationsPartnerSettingsService,
            'notificationsSettings': KalturaNotificationsSettingsService,
            'ossAdapterProfile': KalturaOssAdapterProfileService,
            'ottCategory': KalturaOttCategoryService,
            'ottUser': KalturaOttUserService,
            'parentalRule': KalturaParentalRuleService,
            'partnerConfiguration': KalturaPartnerConfigurationService,
            'paymentGatewayProfile': KalturaPaymentGatewayProfileService,
            'paymentMethodProfile': KalturaPaymentMethodProfileService,
            'personalFeed': KalturaPersonalFeedService,
            'pin': KalturaPinService,
            'ppv': KalturaPpvService,
            'priceDetails': KalturaPriceDetailsService,
            'pricePlan': KalturaPricePlanService,
            'productPrice': KalturaProductPriceService,
            'purchaseSettings': KalturaPurchaseSettingsService,
            'recommendationProfile': KalturaRecommendationProfileService,
            'recording': KalturaRecordingService,
            'region': KalturaRegionService,
            'registrySettings': KalturaRegistrySettingsService,
            'reminder': KalturaReminderService,
            'report': KalturaReportService,
            'searchHistory': KalturaSearchHistoryService,
            'seriesRecording': KalturaSeriesRecordingService,
            'session': KalturaSessionService,
            'socialAction': KalturaSocialActionService,
            'socialComment': KalturaSocialCommentService,
            'social': KalturaSocialService,
            'socialFriendActivity': KalturaSocialFriendActivityService,
            'subscription': KalturaSubscriptionService,
            'subscriptionSet': KalturaSubscriptionSetService,
            'system': KalturaSystemService,
            'timeShiftedTvPartnerSettings': KalturaTimeShiftedTvPartnerSettingsService,
            'topic': KalturaTopicService,
            'transaction': KalturaTransactionService,
            'transactionHistory': KalturaTransactionHistoryService,
            'unifiedPayment': KalturaUnifiedPaymentService,
            'userAssetRule': KalturaUserAssetRuleService,
            'userAssetsListItem': KalturaUserAssetsListItemService,
            'userInterest': KalturaUserInterestService,
            'userLoginPin': KalturaUserLoginPinService,
            'userRole': KalturaUserRoleService,
        }

    def getEnums(self):
        return {
            'KalturaAdsPolicy': KalturaAdsPolicy,
            'KalturaAggregationCountOrderBy': KalturaAggregationCountOrderBy,
            'KalturaAnnouncementOrderBy': KalturaAnnouncementOrderBy,
            'KalturaAnnouncementRecipientsType': KalturaAnnouncementRecipientsType,
            'KalturaAnnouncementStatus': KalturaAnnouncementStatus,
            'KalturaAppTokenHashType': KalturaAppTokenHashType,
            'KalturaAssetCommentOrderBy': KalturaAssetCommentOrderBy,
            'KalturaAssetHistoryOrderBy': KalturaAssetHistoryOrderBy,
            'KalturaAssetOrderBy': KalturaAssetOrderBy,
            'KalturaAssetReferenceType': KalturaAssetReferenceType,
            'KalturaAssetReminderOrderBy': KalturaAssetReminderOrderBy,
            'KalturaAssetType': KalturaAssetType,
            'KalturaBillingAction': KalturaBillingAction,
            'KalturaBillingItemsType': KalturaBillingItemsType,
            'KalturaBillingPriceType': KalturaBillingPriceType,
            'KalturaBookmarkActionType': KalturaBookmarkActionType,
            'KalturaBookmarkOrderBy': KalturaBookmarkOrderBy,
            'KalturaBundleType': KalturaBundleType,
            'KalturaChannelEnrichment': KalturaChannelEnrichment,
            'KalturaCollectionOrderBy': KalturaCollectionOrderBy,
            'KalturaCompensationType': KalturaCompensationType,
            'KalturaConfigurationGroupDeviceOrderBy': KalturaConfigurationGroupDeviceOrderBy,
            'KalturaConfigurationGroupTagOrderBy': KalturaConfigurationGroupTagOrderBy,
            'KalturaConfigurationsOrderBy': KalturaConfigurationsOrderBy,
            'KalturaContextType': KalturaContextType,
            'KalturaCountryOrderBy': KalturaCountryOrderBy,
            'KalturaCouponGroupType': KalturaCouponGroupType,
            'KalturaCouponStatus': KalturaCouponStatus,
            'KalturaCurrencyOrderBy': KalturaCurrencyOrderBy,
            'KalturaDeviceStatus': KalturaDeviceStatus,
            'KalturaDrmSchemeName': KalturaDrmSchemeName,
            'KalturaEngagementOrderBy': KalturaEngagementOrderBy,
            'KalturaEngagementType': KalturaEngagementType,
            'KalturaEntitlementOrderBy': KalturaEntitlementOrderBy,
            'KalturaEntityReferenceBy': KalturaEntityReferenceBy,
            'KalturaExportDataType': KalturaExportDataType,
            'KalturaExportTaskOrderBy': KalturaExportTaskOrderBy,
            'KalturaExportType': KalturaExportType,
            'KalturaFavoriteOrderBy': KalturaFavoriteOrderBy,
            'KalturaFollowTvSeriesOrderBy': KalturaFollowTvSeriesOrderBy,
            'KalturaGroupByField': KalturaGroupByField,
            'KalturaHouseholdDeviceOrderBy': KalturaHouseholdDeviceOrderBy,
            'KalturaHouseholdFrequencyType': KalturaHouseholdFrequencyType,
            'KalturaHouseholdPaymentGatewaySelectedBy': KalturaHouseholdPaymentGatewaySelectedBy,
            'KalturaHouseholdRestriction': KalturaHouseholdRestriction,
            'KalturaHouseholdState': KalturaHouseholdState,
            'KalturaHouseholdSuspensionState': KalturaHouseholdSuspensionState,
            'KalturaHouseholdUserOrderBy': KalturaHouseholdUserOrderBy,
            'KalturaHouseholdUserStatus': KalturaHouseholdUserStatus,
            'KalturaInboxMessageOrderBy': KalturaInboxMessageOrderBy,
            'KalturaInboxMessageStatus': KalturaInboxMessageStatus,
            'KalturaInboxMessageType': KalturaInboxMessageType,
            'KalturaLanguageOrderBy': KalturaLanguageOrderBy,
            'KalturaMessageTemplateType': KalturaMessageTemplateType,
            'KalturaMetaFieldName': KalturaMetaFieldName,
            'KalturaMetaOrderBy': KalturaMetaOrderBy,
            'KalturaMetaTagOrderBy': KalturaMetaTagOrderBy,
            'KalturaMetaType': KalturaMetaType,
            'KalturaNotificationType': KalturaNotificationType,
            'KalturaOTTUserOrderBy': KalturaOTTUserOrderBy,
            'KalturaParentalRuleOrderBy': KalturaParentalRuleOrderBy,
            'KalturaParentalRuleType': KalturaParentalRuleType,
            'KalturaPartnerConfigurationType': KalturaPartnerConfigurationType,
            'KalturaPaymentMethodProfileOrderBy': KalturaPaymentMethodProfileOrderBy,
            'KalturaPaymentMethodType': KalturaPaymentMethodType,
            'KalturaPersonalFeedOrderBy': KalturaPersonalFeedOrderBy,
            'KalturaPinType': KalturaPinType,
            'KalturaPlatform': KalturaPlatform,
            'KalturaPlaybackContextType': KalturaPlaybackContextType,
            'KalturaPositionOwner': KalturaPositionOwner,
            'KalturaPriceDetailsOrderBy': KalturaPriceDetailsOrderBy,
            'KalturaPricePlanOrderBy': KalturaPricePlanOrderBy,
            'KalturaProductPriceOrderBy': KalturaProductPriceOrderBy,
            'KalturaProtectionPolicy': KalturaProtectionPolicy,
            'KalturaPurchaseSettingsType': KalturaPurchaseSettingsType,
            'KalturaPurchaseStatus': KalturaPurchaseStatus,
            'KalturaQuotaOveragePolicy': KalturaQuotaOveragePolicy,
            'KalturaRecordingContextOrderBy': KalturaRecordingContextOrderBy,
            'KalturaRecordingOrderBy': KalturaRecordingOrderBy,
            'KalturaRecordingStatus': KalturaRecordingStatus,
            'KalturaRecordingType': KalturaRecordingType,
            'KalturaRegionOrderBy': KalturaRegionOrderBy,
            'KalturaReminderType': KalturaReminderType,
            'KalturaReportOrderBy': KalturaReportOrderBy,
            'KalturaRuleActionType': KalturaRuleActionType,
            'KalturaRuleLevel': KalturaRuleLevel,
            'KalturaRuleType': KalturaRuleType,
            'KalturaScheduledRecordingAssetType': KalturaScheduledRecordingAssetType,
            'KalturaSearchHistoryOrderBy': KalturaSearchHistoryOrderBy,
            'KalturaSeriesRecordingOrderBy': KalturaSeriesRecordingOrderBy,
            'KalturaSeriesReminderOrderBy': KalturaSeriesReminderOrderBy,
            'KalturaSocialActionOrderBy': KalturaSocialActionOrderBy,
            'KalturaSocialActionPrivacy': KalturaSocialActionPrivacy,
            'KalturaSocialActionType': KalturaSocialActionType,
            'KalturaSocialCommentOrderBy': KalturaSocialCommentOrderBy,
            'KalturaSocialFriendActivityOrderBy': KalturaSocialFriendActivityOrderBy,
            'KalturaSocialNetwork': KalturaSocialNetwork,
            'KalturaSocialPlatform': KalturaSocialPlatform,
            'KalturaSocialPrivacy': KalturaSocialPrivacy,
            'KalturaSocialStatus': KalturaSocialStatus,
            'KalturaStreamType': KalturaStreamType,
            'KalturaSubscriptionDependencyType': KalturaSubscriptionDependencyType,
            'KalturaSubscriptionOrderBy': KalturaSubscriptionOrderBy,
            'KalturaSubscriptionSetOrderBy': KalturaSubscriptionSetOrderBy,
            'KalturaSubscriptionSetType': KalturaSubscriptionSetType,
            'KalturaTopicAutomaticIssueNotification': KalturaTopicAutomaticIssueNotification,
            'KalturaTopicOrderBy': KalturaTopicOrderBy,
            'KalturaTransactionAdapterStatus': KalturaTransactionAdapterStatus,
            'KalturaTransactionHistoryOrderBy': KalturaTransactionHistoryOrderBy,
            'KalturaTransactionType': KalturaTransactionType,
            'KalturaUserAssetRuleOrderBy': KalturaUserAssetRuleOrderBy,
            'KalturaUserAssetsListItemType': KalturaUserAssetsListItemType,
            'KalturaUserAssetsListType': KalturaUserAssetsListType,
            'KalturaUserRoleOrderBy': KalturaUserRoleOrderBy,
            'KalturaUserState': KalturaUserState,
            'KalturaWatchStatus': KalturaWatchStatus,
        }

    def getTypes(self):
        return {
            'KalturaListResponse': KalturaListResponse,
            'KalturaApiExceptionArg': KalturaApiExceptionArg,
            'KalturaSocialComment': KalturaSocialComment,
            'KalturaSocialCommentListResponse': KalturaSocialCommentListResponse,
            'KalturaSocialNetworkComment': KalturaSocialNetworkComment,
            'KalturaTwitterTwit': KalturaTwitterTwit,
            'KalturaFacebookPost': KalturaFacebookPost,
            'KalturaAssetComment': KalturaAssetComment,
            'KalturaSocialAction': KalturaSocialAction,
            'KalturaSocialFriendActivity': KalturaSocialFriendActivity,
            'KalturaSocialFriendActivityListResponse': KalturaSocialFriendActivityListResponse,
            'KalturaSocialActionRate': KalturaSocialActionRate,
            'KalturaSocialActionListResponse': KalturaSocialActionListResponse,
            'KalturaHouseholdPaymentMethod': KalturaHouseholdPaymentMethod,
            'KalturaHouseholdPaymentMethodListResponse': KalturaHouseholdPaymentMethodListResponse,
            'KalturaPaymentMethodProfile': KalturaPaymentMethodProfile,
            'KalturaPaymentMethodProfileListResponse': KalturaPaymentMethodProfileListResponse,
            'KalturaHouseholdPaymentGateway': KalturaHouseholdPaymentGateway,
            'KalturaHouseholdPaymentGatewayListResponse': KalturaHouseholdPaymentGatewayListResponse,
            'KalturaPaymentGatewayBaseProfile': KalturaPaymentGatewayBaseProfile,
            'KalturaValue': KalturaValue,
            'KalturaStringValue': KalturaStringValue,
            'KalturaPaymentGatewayProfile': KalturaPaymentGatewayProfile,
            'KalturaPaymentGatewayProfileListResponse': KalturaPaymentGatewayProfileListResponse,
            'KalturaTranslationToken': KalturaTranslationToken,
            'KalturaMultilingualStringValue': KalturaMultilingualStringValue,
            'KalturaLongValue': KalturaLongValue,
            'KalturaDoubleValue': KalturaDoubleValue,
            'KalturaBooleanValue': KalturaBooleanValue,
            'KalturaIntegerValue': KalturaIntegerValue,
            'KalturaPluginData': KalturaPluginData,
            'KalturaDrmPlaybackPluginData': KalturaDrmPlaybackPluginData,
            'KalturaCustomDrmPlaybackPluginData': KalturaCustomDrmPlaybackPluginData,
            'KalturaHouseholdDevice': KalturaHouseholdDevice,
            'KalturaHouseholdDeviceListResponse': KalturaHouseholdDeviceListResponse,
            'KalturaFairPlayPlaybackPluginData': KalturaFairPlayPlaybackPluginData,
            'KalturaHouseholdUser': KalturaHouseholdUser,
            'KalturaHouseholdUserListResponse': KalturaHouseholdUserListResponse,
            'KalturaHomeNetwork': KalturaHomeNetwork,
            'KalturaHomeNetworkListResponse': KalturaHomeNetworkListResponse,
            'KalturaConfigurations': KalturaConfigurations,
            'KalturaConfigurationsListResponse': KalturaConfigurationsListResponse,
            'KalturaConfigurationGroupDevice': KalturaConfigurationGroupDevice,
            'KalturaConfigurationGroupDeviceListResponse': KalturaConfigurationGroupDeviceListResponse,
            'KalturaConfigurationGroupTag': KalturaConfigurationGroupTag,
            'KalturaConfigurationGroupTagListResponse': KalturaConfigurationGroupTagListResponse,
            'KalturaConfigurationIdentifier': KalturaConfigurationIdentifier,
            'KalturaConfigurationGroup': KalturaConfigurationGroup,
            'KalturaConfigurationGroupListResponse': KalturaConfigurationGroupListResponse,
            'KalturaUserInterestTopic': KalturaUserInterestTopic,
            'KalturaUserInterest': KalturaUserInterest,
            'KalturaUserInterestListResponse': KalturaUserInterestListResponse,
            'KalturaMediaImage': KalturaMediaImage,
            'KalturaMediaFile': KalturaMediaFile,
            'KalturaBuzzScore': KalturaBuzzScore,
            'KalturaAssetStatistics': KalturaAssetStatistics,
            'KalturaMultilingualStringValueArray': KalturaMultilingualStringValueArray,
            'KalturaFavorite': KalturaFavorite,
            'KalturaFavoriteListResponse': KalturaFavoriteListResponse,
            'KalturaPlaybackSource': KalturaPlaybackSource,
            'KalturaBaseOTTUser': KalturaBaseOTTUser,
            'KalturaCountry': KalturaCountry,
            'KalturaOTTUserType': KalturaOTTUserType,
            'KalturaOTTUser': KalturaOTTUser,
            'KalturaOTTUserListResponse': KalturaOTTUserListResponse,
            'KalturaBaseChannel': KalturaBaseChannel,
            'KalturaDiscountModule': KalturaDiscountModule,
            'KalturaUsageModule': KalturaUsageModule,
            'KalturaCouponsGroup': KalturaCouponsGroup,
            'KalturaProductCode': KalturaProductCode,
            'KalturaCollection': KalturaCollection,
            'KalturaCollectionListResponse': KalturaCollectionListResponse,
            'KalturaAssetGroupBy': KalturaAssetGroupBy,
            'KalturaChannel': KalturaChannel,
            'KalturaAssetMetaOrTagGroupBy': KalturaAssetMetaOrTagGroupBy,
            'KalturaAssetFieldGroupBy': KalturaAssetFieldGroupBy,
            'KalturaPricePlan': KalturaPricePlan,
            'KalturaSubscriptionSet': KalturaSubscriptionSet,
            'KalturaSubscriptionSetListResponse': KalturaSubscriptionSetListResponse,
            'KalturaSubscriptionDependencySet': KalturaSubscriptionDependencySet,
            'KalturaSubscriptionSwitchSet': KalturaSubscriptionSwitchSet,
            'KalturaPrice': KalturaPrice,
            'KalturaProductPrice': KalturaProductPrice,
            'KalturaProductPriceListResponse': KalturaProductPriceListResponse,
            'KalturaCollectionPrice': KalturaCollectionPrice,
            'KalturaPpvPrice': KalturaPpvPrice,
            'KalturaSubscriptionPrice': KalturaSubscriptionPrice,
            'KalturaPriceDetails': KalturaPriceDetails,
            'KalturaPriceDetailsListResponse': KalturaPriceDetailsListResponse,
            'KalturaPricePlanListResponse': KalturaPricePlanListResponse,
            'KalturaPreviewModule': KalturaPreviewModule,
            'KalturaPremiumService': KalturaPremiumService,
            'KalturaSubscription': KalturaSubscription,
            'KalturaSubscriptionListResponse': KalturaSubscriptionListResponse,
            'KalturaNpvrPremiumService': KalturaNpvrPremiumService,
            'KalturaHouseholdPremiumService': KalturaHouseholdPremiumService,
            'KalturaProductsPriceListResponse': KalturaProductsPriceListResponse,
            'KalturaEngagement': KalturaEngagement,
            'KalturaEngagementListResponse': KalturaEngagementListResponse,
            'KalturaEngagementAdapterBase': KalturaEngagementAdapterBase,
            'KalturaEngagementAdapter': KalturaEngagementAdapter,
            'KalturaEngagementAdapterListResponse': KalturaEngagementAdapterListResponse,
            'KalturaReminder': KalturaReminder,
            'KalturaReminderListResponse': KalturaReminderListResponse,
            'KalturaSeriesReminder': KalturaSeriesReminder,
            'KalturaAssetReminder': KalturaAssetReminder,
            'KalturaInboxMessage': KalturaInboxMessage,
            'KalturaInboxMessageListResponse': KalturaInboxMessageListResponse,
            'KalturaFollowDataBase': KalturaFollowDataBase,
            'KalturaFollowTvSeries': KalturaFollowTvSeries,
            'KalturaFollowTvSeriesListResponse': KalturaFollowTvSeriesListResponse,
            'KalturaAnnouncement': KalturaAnnouncement,
            'KalturaAnnouncementListResponse': KalturaAnnouncementListResponse,
            'KalturaFeed': KalturaFeed,
            'KalturaPersonalFeed': KalturaPersonalFeed,
            'KalturaPersonalFeedListResponse': KalturaPersonalFeedListResponse,
            'KalturaTopic': KalturaTopic,
            'KalturaTopicListResponse': KalturaTopicListResponse,
            'KalturaIntegerValueListResponse': KalturaIntegerValueListResponse,
            'KalturaReport': KalturaReport,
            'KalturaReportListResponse': KalturaReportListResponse,
            'KalturaPushParams': KalturaPushParams,
            'KalturaDeviceReport': KalturaDeviceReport,
            'KalturaSeriesRecording': KalturaSeriesRecording,
            'KalturaSeriesRecordingListResponse': KalturaSeriesRecordingListResponse,
            'KalturaHouseholdPremiumServiceListResponse': KalturaHouseholdPremiumServiceListResponse,
            'KalturaCDVRAdapterProfile': KalturaCDVRAdapterProfile,
            'KalturaCDVRAdapterProfileListResponse': KalturaCDVRAdapterProfileListResponse,
            'KalturaRecording': KalturaRecording,
            'KalturaRecordingListResponse': KalturaRecordingListResponse,
            'KalturaBillingTransaction': KalturaBillingTransaction,
            'KalturaBillingTransactionListResponse': KalturaBillingTransactionListResponse,
            'KalturaEntitlement': KalturaEntitlement,
            'KalturaEntitlementListResponse': KalturaEntitlementListResponse,
            'KalturaCollectionEntitlement': KalturaCollectionEntitlement,
            'KalturaPpvEntitlement': KalturaPpvEntitlement,
            'KalturaSubscriptionEntitlement': KalturaSubscriptionEntitlement,
            'KalturaAssetCount': KalturaAssetCount,
            'KalturaAssetsCount': KalturaAssetsCount,
            'KalturaAssetCountListResponse': KalturaAssetCountListResponse,
            'KalturaSlimAsset': KalturaSlimAsset,
            'KalturaBookmarkPlayerData': KalturaBookmarkPlayerData,
            'KalturaBookmark': KalturaBookmark,
            'KalturaBookmarkListResponse': KalturaBookmarkListResponse,
            'KalturaAsset': KalturaAsset,
            'KalturaAssetListResponse': KalturaAssetListResponse,
            'KalturaProgramAsset': KalturaProgramAsset,
            'KalturaRecordingAsset': KalturaRecordingAsset,
            'KalturaMediaAsset': KalturaMediaAsset,
            'KalturaAssetCommentListResponse': KalturaAssetCommentListResponse,
            'KalturaAssetStatisticsListResponse': KalturaAssetStatisticsListResponse,
            'KalturaAssetHistory': KalturaAssetHistory,
            'KalturaAssetHistoryListResponse': KalturaAssetHistoryListResponse,
            'KalturaCurrency': KalturaCurrency,
            'KalturaCurrencyListResponse': KalturaCurrencyListResponse,
            'KalturaLanguage': KalturaLanguage,
            'KalturaLanguageListResponse': KalturaLanguageListResponse,
            'KalturaMeta': KalturaMeta,
            'KalturaMetaListResponse': KalturaMetaListResponse,
            'KalturaDeviceBrand': KalturaDeviceBrand,
            'KalturaDeviceBrandListResponse': KalturaDeviceBrandListResponse,
            'KalturaCountryListResponse': KalturaCountryListResponse,
            'KalturaOSSAdapterBaseProfile': KalturaOSSAdapterBaseProfile,
            'KalturaOSSAdapterProfile': KalturaOSSAdapterProfile,
            'KalturaOSSAdapterProfileListResponse': KalturaOSSAdapterProfileListResponse,
            'KalturaSearchHistory': KalturaSearchHistory,
            'KalturaSearchHistoryListResponse': KalturaSearchHistoryListResponse,
            'KalturaDeviceFamilyBase': KalturaDeviceFamilyBase,
            'KalturaDeviceFamily': KalturaDeviceFamily,
            'KalturaDeviceFamilyListResponse': KalturaDeviceFamilyListResponse,
            'KalturaHouseholdDeviceFamilyLimitations': KalturaHouseholdDeviceFamilyLimitations,
            'KalturaRegionalChannel': KalturaRegionalChannel,
            'KalturaRegion': KalturaRegion,
            'KalturaRegionListResponse': KalturaRegionListResponse,
            'KalturaUserAssetRule': KalturaUserAssetRule,
            'KalturaUserAssetRuleListResponse': KalturaUserAssetRuleListResponse,
            'KalturaCDNAdapterProfile': KalturaCDNAdapterProfile,
            'KalturaCDNAdapterProfileListResponse': KalturaCDNAdapterProfileListResponse,
            'KalturaExportTask': KalturaExportTask,
            'KalturaExportTaskListResponse': KalturaExportTaskListResponse,
            'KalturaChannelEnrichmentHolder': KalturaChannelEnrichmentHolder,
            'KalturaExternalChannelProfile': KalturaExternalChannelProfile,
            'KalturaExternalChannelProfileListResponse': KalturaExternalChannelProfileListResponse,
            'KalturaRecommendationProfile': KalturaRecommendationProfile,
            'KalturaRecommendationProfileListResponse': KalturaRecommendationProfileListResponse,
            'KalturaRegistrySettings': KalturaRegistrySettings,
            'KalturaRegistrySettingsListResponse': KalturaRegistrySettingsListResponse,
            'KalturaParentalRule': KalturaParentalRule,
            'KalturaParentalRuleListResponse': KalturaParentalRuleListResponse,
            'KalturaUserRole': KalturaUserRole,
            'KalturaUserRoleListResponse': KalturaUserRoleListResponse,
            'KalturaClientConfiguration': KalturaClientConfiguration,
            'KalturaBaseResponseProfile': KalturaBaseResponseProfile,
            'KalturaRequestConfiguration': KalturaRequestConfiguration,
            'KalturaFilter': KalturaFilter,
            'KalturaDetachedResponseProfile': KalturaDetachedResponseProfile,
            'KalturaRelatedObjectFilter': KalturaRelatedObjectFilter,
            'KalturaSocialCommentFilter': KalturaSocialCommentFilter,
            'KalturaSocialFriendActivityFilter': KalturaSocialFriendActivityFilter,
            'KalturaSocialActionFilter': KalturaSocialActionFilter,
            'KalturaPaymentMethodProfileFilter': KalturaPaymentMethodProfileFilter,
            'KalturaHouseholdDeviceFilter': KalturaHouseholdDeviceFilter,
            'KalturaHouseholdUserFilter': KalturaHouseholdUserFilter,
            'KalturaConfigurationsFilter': KalturaConfigurationsFilter,
            'KalturaReportFilter': KalturaReportFilter,
            'KalturaDeviceReportFilter': KalturaDeviceReportFilter,
            'KalturaConfigurationGroupTagFilter': KalturaConfigurationGroupTagFilter,
            'KalturaConfigurationGroupDeviceFilter': KalturaConfigurationGroupDeviceFilter,
            'KalturaFavoriteFilter': KalturaFavoriteFilter,
            'KalturaOTTUserFilter': KalturaOTTUserFilter,
            'KalturaCollectionFilter': KalturaCollectionFilter,
            'KalturaPricePlanFilter': KalturaPricePlanFilter,
            'KalturaPriceDetailsFilter': KalturaPriceDetailsFilter,
            'KalturaSubscriptionSetFilter': KalturaSubscriptionSetFilter,
            'KalturaSubscriptionDependencySetFilter': KalturaSubscriptionDependencySetFilter,
            'KalturaSubscriptionFilter': KalturaSubscriptionFilter,
            'KalturaEngagementFilter': KalturaEngagementFilter,
            'KalturaReminderFilter': KalturaReminderFilter,
            'KalturaAssetReminderFilter': KalturaAssetReminderFilter,
            'KalturaSeriesReminderFilter': KalturaSeriesReminderFilter,
            'KalturaSeasonsReminderFilter': KalturaSeasonsReminderFilter,
            'KalturaFollowTvSeriesFilter': KalturaFollowTvSeriesFilter,
            'KalturaInboxMessageFilter': KalturaInboxMessageFilter,
            'KalturaAnnouncementFilter': KalturaAnnouncementFilter,
            'KalturaPersonalFeedFilter': KalturaPersonalFeedFilter,
            'KalturaTopicFilter': KalturaTopicFilter,
            'KalturaAggregationCountFilter': KalturaAggregationCountFilter,
            'KalturaPersistedFilter': KalturaPersistedFilter,
            'KalturaDynamicOrderBy': KalturaDynamicOrderBy,
            'KalturaAssetFilter': KalturaAssetFilter,
            'KalturaBaseSearchAssetFilter': KalturaBaseSearchAssetFilter,
            'KalturaScheduledRecordingProgramFilter': KalturaScheduledRecordingProgramFilter,
            'KalturaBundleFilter': KalturaBundleFilter,
            'KalturaChannelExternalFilter': KalturaChannelExternalFilter,
            'KalturaChannelFilter': KalturaChannelFilter,
            'KalturaRelatedFilter': KalturaRelatedFilter,
            'KalturaRelatedExternalFilter': KalturaRelatedExternalFilter,
            'KalturaSearchAssetFilter': KalturaSearchAssetFilter,
            'KalturaSearchExternalFilter': KalturaSearchExternalFilter,
            'KalturaSeriesRecordingFilter': KalturaSeriesRecordingFilter,
            'KalturaProductPriceFilter': KalturaProductPriceFilter,
            'KalturaEntitlementFilter': KalturaEntitlementFilter,
            'KalturaTransactionHistoryFilter': KalturaTransactionHistoryFilter,
            'KalturaRecordingContextFilter': KalturaRecordingContextFilter,
            'KalturaRecordingFilter': KalturaRecordingFilter,
            'KalturaAssetCommentFilter': KalturaAssetCommentFilter,
            'KalturaBookmarkFilter': KalturaBookmarkFilter,
            'KalturaAssetHistoryFilter': KalturaAssetHistoryFilter,
            'KalturaCurrencyFilter': KalturaCurrencyFilter,
            'KalturaLanguageFilter': KalturaLanguageFilter,
            'KalturaMetaFilter': KalturaMetaFilter,
            'KalturaCountryFilter': KalturaCountryFilter,
            'KalturaSearchHistoryFilter': KalturaSearchHistoryFilter,
            'KalturaRegionFilter': KalturaRegionFilter,
            'KalturaUserAssetRuleFilter': KalturaUserAssetRuleFilter,
            'KalturaParentalRuleFilter': KalturaParentalRuleFilter,
            'KalturaExportTaskFilter': KalturaExportTaskFilter,
            'KalturaUserRoleFilter': KalturaUserRoleFilter,
            'KalturaFilterPager': KalturaFilterPager,
            'KalturaAppToken': KalturaAppToken,
            'KalturaSession': KalturaSession,
            'KalturaSessionInfo': KalturaSessionInfo,
            'KalturaPlaybackContextOptions': KalturaPlaybackContextOptions,
            'KalturaRuleAction': KalturaRuleAction,
            'KalturaAccessControlMessage': KalturaAccessControlMessage,
            'KalturaPlaybackContext': KalturaPlaybackContext,
            'KalturaAccessControlBlockAction': KalturaAccessControlBlockAction,
            'KalturaAdsSource': KalturaAdsSource,
            'KalturaAdsContext': KalturaAdsContext,
            'KalturaAssetFileContext': KalturaAssetFileContext,
            'KalturaAssetStatisticsQuery': KalturaAssetStatisticsQuery,
            'KalturaCDNPartnerSettings': KalturaCDNPartnerSettings,
            'KalturaCompensation': KalturaCompensation,
            'KalturaKeyValue': KalturaKeyValue,
            'KalturaEmailMessage': KalturaEmailMessage,
            'KalturaEntitlementRenewalBase': KalturaEntitlementRenewalBase,
            'KalturaUnifiedPaymentRenewal': KalturaUnifiedPaymentRenewal,
            'KalturaNetworkActionStatus': KalturaNetworkActionStatus,
            'KalturaUserSocialActionResponse': KalturaUserSocialActionResponse,
            'KalturaPaymentGatewayConfiguration': KalturaPaymentGatewayConfiguration,
            'KalturaHouseholdQuota': KalturaHouseholdQuota,
            'KalturaMessageTemplate': KalturaMessageTemplate,
            'KalturaPpv': KalturaPpv,
            'KalturaLicensedUrl': KalturaLicensedUrl,
            'KalturaLicensedUrlBaseRequest': KalturaLicensedUrlBaseRequest,
            'KalturaLicensedUrlMediaRequest': KalturaLicensedUrlMediaRequest,
            'KalturaLicensedUrlEpgRequest': KalturaLicensedUrlEpgRequest,
            'KalturaLicensedUrlRecordingRequest': KalturaLicensedUrlRecordingRequest,
            'KalturaRegistryResponse': KalturaRegistryResponse,
            'KalturaPushMessage': KalturaPushMessage,
            'KalturaNotificationsPartnerSettings': KalturaNotificationsPartnerSettings,
            'KalturaNotificationsSettings': KalturaNotificationsSettings,
            'KalturaTimeShiftedTvPartnerSettings': KalturaTimeShiftedTvPartnerSettings,
            'KalturaUserAssetsListItem': KalturaUserAssetsListItem,
            'KalturaHouseholdLimitations': KalturaHouseholdLimitations,
            'KalturaPartnerConfiguration': KalturaPartnerConfiguration,
            'KalturaBillingPartnerConfig': KalturaBillingPartnerConfig,
            'KalturaLoginSession': KalturaLoginSession,
            'KalturaHousehold': KalturaHousehold,
            'KalturaDevicePin': KalturaDevicePin,
            'KalturaLoginResponse': KalturaLoginResponse,
            'KalturaPin': KalturaPin,
            'KalturaPurchaseSettings': KalturaPurchaseSettings,
            'KalturaCoupon': KalturaCoupon,
            'KalturaOTTCategory': KalturaOTTCategory,
            'KalturaEntitlementRenewal': KalturaEntitlementRenewal,
            'KalturaSocial': KalturaSocial,
            'KalturaFacebookSocial': KalturaFacebookSocial,
            'KalturaSocialConfig': KalturaSocialConfig,
            'KalturaSocialFacebookConfig': KalturaSocialFacebookConfig,
            'KalturaActionPermissionItem': KalturaActionPermissionItem,
            'KalturaSocialUserConfig': KalturaSocialUserConfig,
            'KalturaPurchaseBase': KalturaPurchaseBase,
            'KalturaPurchase': KalturaPurchase,
            'KalturaPurchaseSession': KalturaPurchaseSession,
            'KalturaExternalReceipt': KalturaExternalReceipt,
            'KalturaTransaction': KalturaTransaction,
            'KalturaTransactionStatus': KalturaTransactionStatus,
            'KalturaUserLoginPin': KalturaUserLoginPin,
            'KalturaOTTUserDynamicData': KalturaOTTUserDynamicData,
        }

    # @return string
    def getName(self):
        return ''

