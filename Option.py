from datetime import time


def convert_times_string(time_string):
    times = time_string.split('-')
    return convert_time_string(times[0]), convert_time_string(times[1])


def convert_time_string(time_string):
    hour = int(time_string[:-3:])
    minute = int(time_string[-2:])
    return time(hour=hour, minute=minute)


class Option:
    def __init__(self, time_string: str, room: str, seats: int, description: str, radio_button_class_name: str = ''):
        self.start_time, self.end_time = convert_times_string(time_string)
        self.room = room
        self.seats = seats
        self.description = description
        self.radio_button_class_name = radio_button_class_name
