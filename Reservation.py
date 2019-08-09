from aenum import Enum, NoAlias

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

RUIMTE_RESERVEREN_URL = "https://www.ruimtereserveren.hu.nl"


class Location(Enum, settings=NoAlias):
    HL7 = 'HEIDELBERGLAAN'
    HL15 = 'HEIDELBERGLAAN'
    NP21 = 'AMERSFOORT'
    PL97 = 'PADUALAAN'
    PL99 = 'PADUALAAN'
    PL101 = 'PADUALAAN'
    BL101 = 'BOLOGNALAAN/DALTONLAAN'
    DL200 = 'BOLOGNALAAN/DALTONLAAN'


def to_time(time: int) -> str:
    return str(time)[:-2:] + ':' + str(time)[-2:]


class Reservation:
    def __init__(self, arguments: dict, debug: bool = False):
        options = Options()
        options.headless = not debug
        self.debug = debug
        self.browser = Chrome(options=options)
        self.location = arguments['location']
        self.setup(arguments)

    def setup(self, arguments: dict):
        self.select_location()
        self.login(arguments['username'], arguments['password'])

    def select_location(self):
        self.browser.get(RUIMTE_RESERVEREN_URL)
        self.browser.find_element_by_link_text(self.location.value).click()
        print('Selected location: ' + self.location.name)

    def login(self, username: str, password: str):
        username_field = self.browser.find_element_by_id('ContentPlaceHolder1_user')
        username_field.send_keys(username)

        self.browser.find_element_by_id('ContentPlaceHolder1_password').click()
        password_field = self.browser.find_element_by_id('ContentPlaceHolder1_password')
        password_field.send_keys(password)

        self.browser.find_element_by_id('ContentPlaceHolder1_logon').click()
        print('Logged in')

    def book(self, date: dict, seats: int, start_time: int, duration: int):
        self.browser.find_element_by_id('ctl00_Main_PageMenu1_BookRoomLink').click()
        start_time = to_time(start_time)
        duration = to_time(duration)

        seat_form = Select(self.browser.find_element_by_id('ctl00_Main_Room1_ReqSize'))
        seat_form.select_by_value(str(seats))

        location_select = Select(self.browser.find_element_by_id('ctl00_Main_Room1_ZoneList'))
        location_select.select_by_visible_text(self.location.name)

        self.browser.find_element_by_link_text(str(date['day'])).click()

        start_time_select = Select(self.browser.find_element_by_id('startTimeTemp'))
        start_time_select.select_by_visible_text(start_time)

        duration_select = Select(self.browser.find_element_by_id('durTemp'))
        duration_select.select_by_visible_text(duration)

        self.browser.implicitly_wait(100)

        self.browser.find_element_by_id('ctl00_Main_ShowOptionsBtn').click()

        self.browser.find_element_by_id('ctl00_Main_OptionSelector_OptionsGrid_ctl02_rdoSingle').click()

        self.browser.find_element_by_id('ctl00_Main_SelectOptionButton').click()

        print(self.browser.find_element_by_id('ctl00_Main_BookingForm1_bkg_location').get_attribute('value'))
        print(self.browser.find_element_by_id('ctl00_Main_BookingForm1_bkg_date').get_attribute('value'))
        print(self.browser.find_element_by_id('ctl00_Main_BookingForm1_bkg_start').get_attribute(
            'value') + '-' + self.browser.find_element_by_id('ctl00_Main_BookingForm1_bkg_end').get_attribute('value'))

        if not self.debug:
            self.browser.find_element_by_id('ctl00_Main_MakeBookingBtn').click()
