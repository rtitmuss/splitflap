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


if __name__ == '__main__':
    unittest.main()
