from datetime import date, time

from Reservation import Location, Reservation

reservation = Reservation(
    {'location': Location.HL15,
     'username': '',
     'password': ''})

reservation.book(date(2019, 8, 21), 5, time(hour=14, minute=30), time(hour=2))
