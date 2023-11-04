import unittest
from clock import Clock


class ClockTest(unittest.TestCase):

    def test_new_overflow(self):
        self.assertEqual(Clock(second=60), Clock(minute=1, second=0))
        self.assertEqual(Clock(minute=60), Clock(hour=1, minute=0))
        self.assertEqual(Clock(hour=24), Clock(day=2, hour=0))
        self.assertEqual(Clock(day=32), Clock(month=2, day=1))  # Jan

    def test_new_underflow(self):
        self.assertEqual(Clock(minute=1, second=-60), Clock())
        self.assertEqual(Clock(hour=1, minute=-60), Clock())
        self.assertEqual(Clock(day=2, hour=-24), Clock())
        #self.assertEqual(Clock(month=2, day=-32), Clock())  # Jan

    def test_str(self):
        self.assertEqual(str(Clock(0)), '0000-01-01 00:00:00')

    def test_eq(self):
        self.assertEqual(Clock(), Clock())
        self.assertEqual(Clock(2023, 11, 4, 8, 30, 30), Clock(2023, 11, 4, 8, 30, 30))
        self.assertNotEqual(Clock(), Clock(year=2023))
        self.assertNotEqual(Clock(), Clock(month=11))
        self.assertNotEqual(Clock(), Clock(day=4))
        self.assertNotEqual(Clock(), Clock(hour=8))
        self.assertNotEqual(Clock(), Clock(minute=30))
        self.assertNotEqual(Clock(), Clock(second=30))

    def test_add_second(self):
        self.assertEqual(Clock().add(second=1), Clock(second=1))
        self.assertEqual(Clock().add(second=3600), Clock(hour=1))
        self.assertEqual(Clock().add(second=86400), Clock(day=2))
        self.assertEqual(Clock().add(second=2678400), Clock(month=2))  # Jan

    def test_add_minute(self):
        self.assertEqual(Clock().add(minute=1), Clock(minute=1))
        self.assertEqual(Clock().add(minute=60), Clock(hour=1))
        self.assertEqual(Clock().add(minute=1440), Clock(day=2))
        self.assertEqual(Clock().add(minute=44640), Clock(month=2))  # Jan

    def test_add_hour(self):
        self.assertEqual(Clock().add(hour=1), Clock(hour=1))
        self.assertEqual(Clock().add(hour=24), Clock(day=2))
        self.assertEqual(Clock().add(hour=744), Clock(month=2))  # Jan

    def test_strftime(self):
        clock = Clock(2023, 11, 4, 13, 30, 30)
        self.assertEqual(clock.strftime("%Y %m %d %H %M %S %a %b %I %p %%%"),
                         "2023 11 04 13 30 30 Sat Nov 01 PM %%")

    def test_strftime_day(self):
        self.assertEqual(Clock(day=1).strftime('%a'), 'Thu')
        self.assertEqual(Clock(day=2).strftime('%a'), 'Fri')
        self.assertEqual(Clock(day=3).strftime('%a'), 'Sat')
        self.assertEqual(Clock(day=4).strftime('%a'), 'Sun')
        self.assertEqual(Clock(day=5).strftime('%a'), 'Mon')
        self.assertEqual(Clock(day=6).strftime('%a'), 'Tue')
        self.assertEqual(Clock(day=7).strftime('%a'), 'Wed')

    def test_strftime_month(self):
        self.assertEqual(Clock(month=1).strftime('%b'), 'Jan')
        self.assertEqual(Clock(month=2).strftime('%b'), 'Feb')
        self.assertEqual(Clock(month=3).strftime('%b'), 'Mar')
        self.assertEqual(Clock(month=4).strftime('%b'), 'Apr')
        self.assertEqual(Clock(month=5).strftime('%b'), 'May')
        self.assertEqual(Clock(month=6).strftime('%b'), 'Jun')
        self.assertEqual(Clock(month=7).strftime('%b'), 'Jul')
        self.assertEqual(Clock(month=8).strftime('%b'), 'Aug')
        self.assertEqual(Clock(month=9).strftime('%b'), 'Sep')
        self.assertEqual(Clock(month=10).strftime('%b'), 'Oct')
        self.assertEqual(Clock(month=11).strftime('%b'), 'Nov')
        self.assertEqual(Clock(month=12).strftime('%b'), 'Dec')

    def test_strftime_ampm(self):
        self.assertEqual(Clock(hour=0).strftime('%I %p'), '12 AM')  # 12 midnight
        self.assertEqual(Clock(hour=1).strftime('%I %p'), '01 AM')
        self.assertEqual(Clock(hour=2).strftime('%I %p'), '02 AM')
        self.assertEqual(Clock(hour=3).strftime('%I %p'), '03 AM')
        self.assertEqual(Clock(hour=4).strftime('%I %p'), '04 AM')
        self.assertEqual(Clock(hour=5).strftime('%I %p'), '05 AM')
        self.assertEqual(Clock(hour=6).strftime('%I %p'), '06 AM')
        self.assertEqual(Clock(hour=7).strftime('%I %p'), '07 AM')
        self.assertEqual(Clock(hour=8).strftime('%I %p'), '08 AM')
        self.assertEqual(Clock(hour=9).strftime('%I %p'), '09 AM')
        self.assertEqual(Clock(hour=10).strftime('%I %p'), '10 AM')
        self.assertEqual(Clock(hour=11).strftime('%I %p'), '11 AM')
        self.assertEqual(Clock(hour=12).strftime('%I %p'), '12 PM')  # 12 noon
        self.assertEqual(Clock(hour=13).strftime('%I %p'), '01 PM')
        self.assertEqual(Clock(hour=14).strftime('%I %p'), '02 PM')
        self.assertEqual(Clock(hour=15).strftime('%I %p'), '03 PM')
        self.assertEqual(Clock(hour=16).strftime('%I %p'), '04 PM')
        self.assertEqual(Clock(hour=17).strftime('%I %p'), '05 PM')
        self.assertEqual(Clock(hour=18).strftime('%I %p'), '06 PM')
        self.assertEqual(Clock(hour=19).strftime('%I %p'), '07 PM')
        self.assertEqual(Clock(hour=20).strftime('%I %p'), '08 PM')
        self.assertEqual(Clock(hour=21).strftime('%I %p'), '09 PM')
        self.assertEqual(Clock(hour=22).strftime('%I %p'), '10 PM')
        self.assertEqual(Clock(hour=23).strftime('%I %p'), '11 PM')

    def test_now(self):
        utc = Clock.now()
        self.assertIsInstance(utc, Clock)

    def test_now_timezone(self):
        utc = Clock.now()
        localtime = Clock.now('Europe/Stockholm')
        self.assertNotEqual(utc, localtime)

    def test_now_invalid_timezone(self):
        self.assertRaises(ValueError, Clock.now, 'city')


if __name__ == '__main__':
    unittest.main()
