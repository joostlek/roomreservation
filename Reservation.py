from aenum import Enum, NoAlias

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from datetime import date, time

from Option import Option

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


def validate_start_time(start_time: time) -> time:
    if start_time.minute != 0 and start_time.minute != 30:
        raise Exception
    if start_time.hour < 8 or start_time.hour > 21:
        raise Exception
    return start_time


def validate_duration(duration: time) -> time:
    if duration.hour == 0 and duration.minute != 30:
        raise Exception
    if duration.hour < 0 or duration.hour > 4:
        raise Exception
    if duration.minute != 0 and duration.minute != 30:
        raise Exception
    return duration


def format_time(time_to_format: time) -> str:
    res = ''
    res += str(time_to_format.hour)
    res += ':'
    if time_to_format.minute == 0:
        res += '00'
    else:
        res += '30'
    return res


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

    def find_available_rooms(self, date_of_reservation: date, seats: int, start_time: time, duration: time) -> list:
        start_time = validate_start_time(start_time)
        duration = validate_duration(duration)

        self.browser.find_element_by_id('ctl00_Main_PageMenu1_BookRoomLink').click()

        seat_form = Select(self.browser.find_element_by_id('ctl00_Main_Room1_ReqSize'))
        seat_form.select_by_value(str(seats))

        location_select = Select(self.browser.find_element_by_id('ctl00_Main_Room1_ZoneList'))
        location_select.select_by_visible_text(self.location.name)

        self.browser.find_element_by_link_text(str(date_of_reservation.day)).click()

        start_time_select = Select(self.browser.find_element_by_id('startTimeTemp'))
        start_time_select.select_by_visible_text(format_time(start_time))

        duration_select = Select(self.browser.find_element_by_id('durTemp'))
        duration_select.select_by_visible_text(format_time(duration))

        self.browser.implicitly_wait(100)

        self.browser.find_element_by_id('ctl00_Main_ShowOptionsBtn').click()
        table = self.browser.find_element_by_id('ctl00_Main_OptionSelector_OptionsGrid')
        rows = table.find_elements_by_class_name('GridItem')
        rows.extend(table.find_elements_by_class_name('GridAlternateItem'))

        options = []

        for row in rows:
            time_string = row.find_element_by_class_name('OptionTimeColumn').text
            room = row.find_element_by_class_name('OptionLocationNameColumn').text
            seats = int(row.find_element_by_class_name('OptionCapacityColumn').text)
            description = row.find_element_by_class_name('OptionLocationDescriptionColumn').text
            radio_button_class_name = row.find_element_by_xpath(
                "//td[contains(@class, 'OptionSelectColumn')]/input").get_attribute('id')
            option = Option(time_string, room, seats, description, radio_button_class_name=radio_button_class_name)
            options.append(option)

        return options

    def book(self, date_of_reservation: date, seats: int, start_time: time, duration: time):
        available_rooms = self.find_available_rooms(date_of_reservation, seats, start_time, duration)
        best_room = self.choose_best_room(available_rooms)
        self.reserve(best_room)

    def reserve(self, option: Option):
        self.browser.find_element_by_id(option.radio_button_class_name).click()
        self.browser.find_element_by_name('ctl00$Main$SelectOptionButton').click()
        if not self.debug:
            self.browser.find_element_by_name('ctl00$Main$MakeBookingBtn').click()

    def choose_best_room(self, options: list) -> Option:
        return options[0]
