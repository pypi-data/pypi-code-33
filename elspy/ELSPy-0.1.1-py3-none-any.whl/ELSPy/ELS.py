"""
ELSPy ELS module

:copyright: (c) 2019 by Miikka Värri
:license: MIT, see LICENSE for more details.
"""
from zeep import Client, xsd

class ELS:
  
  __username    = None
  __password    = None
  __systemname  = None
  __client      = None

  """
  Init ELS class
  """
  def __init__(self, wsdl='', username='', password=''):
    self.__username   = username
    self.__password   = password
    self.loginguid    = None
    self.wsdl         = wsdl

  """
  Returns xsd:String with value passed
  """
  def __str_obj(self, val):
    return xsd.AnyObject(xsd.String(), val)

  """
  Returns list of bookings between date range
  """
  def __get_booking_calendar_days(self, start_date, end_date):

    return self.__get_client().GetBookingCalendarDays(
      loginguid = self.__get_loginguid(), 
      endDate = self.__str_obj(end_date),
      startDate = self.__str_obj(start_date))

  """
  Sets user prechoise (SetBookPrechoises)
  """
  def __set_book_prechoises(self, choise=0):
    return self.__get_client().SetBookPrechoises(
      loginguid=self.__get_loginguid(), 
      prechoiseindex=self.__str_obj(choise))

  """
  Returns existing or a new SOAP client
  """
  def __get_client(self):
    # Create a new client and bind to service 
    # and port if doesn't exist
    if self.__client is None :
      client = Client(wsdl=self.wsdl)
      self.__client = client.bind('VisionMobile', 
        'VisionMobileSoap')
    return self.__client

  """
  Returns user data (GetUserData)
  """
  def __get_user_data(self):
    result = self.__get_client().GetUserData(
      loginguid=self.__get_loginguid())
    return result

  """
  Gets and sets self.__systemname from (GetSystemName)
  """
  def __get_set_systemname(self):
    self.__systemname = self.__get_client().GetSystemName()

  """
  Returns system name
  """
  def __get_systemname(self):
    if not self.__systemname:
      self.__get_set_systemname()
    return self.__systemname

  """
  Returns loginguid by username and password (Login)
  """
  def __get_loginguid(self):

    if not self.loginguid:
      result = self.__get_client().Login(
        timeout=1200, 
        username = self.__str_obj(self.__username), 
        Password = self.__str_obj(self.__password), 
        systemname = self.__str_obj(self.__get_systemname()))
      self.loginguid = result
    return self.__str_obj(self.loginguid)

  """
  Returns bookable items with their name and index.
  """
  def get_choises(self):
    user_data = self.__get_user_data()[1]['Units']['MobileUnit']
    return user_data[0]['PreChoises']['MobilePreChoise']

  """
  Returns bookings for choise between daterange
  """
  def get_bookings(self, choise, start_date_str, end_date_str):
    # Set choise to WS
    self.__set_book_prechoises(choise)
    # Return bookings info from WS
    return self.__get_booking_calendar_days(start_date_str, 
      end_date_str)
