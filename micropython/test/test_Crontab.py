import unittest

from primary.Crontab import find_matching_crontab

crontab_entries = [
    "0 12 * * * echo 'Noon'",
    "10-20 14 * * * echo '14:10 to 14:20'",
    "30 14 * * 5 echo 'Friday afternoon'",
    "0 8 * * * echo 'Morning'",
    "* * * * * echo 'Every minute'",
]


class CrontabTest(unittest.TestCase):
    def test_noon(self):
        self.assertEqual(find_matching_crontab((0, 12, 10, 3, 4), crontab_entries), "echo 'Noon'")

    def test_every_minute(self):
        self.assertEqual(find_matching_crontab((25, 14, 1, 3, 5), crontab_entries), "echo 'Every minute'")

    def test_range(self):
        self.assertEqual(find_matching_crontab((10, 14, 5, 6, 2), crontab_entries), "echo '14:10 to 14:20'")

    def test_friday_afternoon(self):
        self.assertEqual(find_matching_crontab((30, 14, 2, 6, 5), crontab_entries), "echo 'Friday afternoon'")

    def test_morning(self):
        self.assertEqual(find_matching_crontab((0, 8, 10, 3, 4), crontab_entries), "echo 'Morning'")

    def test_overnight_range(self):
        crontab_entries = [
            "* 22-06 * * * echo 'Night'",
            "* 7-21 * * * echo 'Day'",
        ]

        # Test night hours
        self.assertEqual(find_matching_crontab((0, 23, 1, 1, 0), crontab_entries), "echo 'Night'")
        self.assertEqual(find_matching_crontab((0, 0, 1, 1, 0), crontab_entries), "echo 'Night'")
        self.assertEqual(find_matching_crontab((0, 6, 1, 1, 0), crontab_entries), "echo 'Night'")

        # Test day hours
        self.assertEqual(find_matching_crontab((0, 7, 1, 1, 0), crontab_entries), "echo 'Day'")
        self.assertEqual(find_matching_crontab((0, 21, 1, 1, 0), crontab_entries), "echo 'Day'")

    def test_overnight_range_with_step(self):
        crontab_entries = [
            "* 22-06/2 * * * echo 'Night every 2 hours'",
            "* 22-06 * * * echo 'Night'",
        ]

        # Test night hours with step
        self.assertEqual(find_matching_crontab((0, 22, 1, 1, 0), crontab_entries), "echo 'Night every 2 hours'")
        self.assertEqual(find_matching_crontab((0, 23, 1, 1, 0), crontab_entries), "echo 'Night'")
        self.assertEqual(find_matching_crontab((0, 0, 1, 1, 0), crontab_entries), "echo 'Night every 2 hours'")
        self.assertEqual(find_matching_crontab((0, 1, 1, 1, 0), crontab_entries), "echo 'Night'")
        self.assertEqual(find_matching_crontab((0, 2, 1, 1, 0), crontab_entries), "echo 'Night every 2 hours'")
        self.assertEqual(find_matching_crontab((0, 3, 1, 1, 0), crontab_entries), "echo 'Night'")
        self.assertEqual(find_matching_crontab((0, 4, 1, 1, 0), crontab_entries), "echo 'Night every 2 hours'")
        self.assertEqual(find_matching_crontab((0, 5, 1, 1, 0), crontab_entries), "echo 'Night'")
        self.assertEqual(find_matching_crontab((0, 6, 1, 1, 0), crontab_entries), "echo 'Night every 2 hours'")


if __name__ == '__main__':
    unittest.main()
