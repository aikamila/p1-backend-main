from ...serializers import TimeSincePostedCalculator
from django.test import TestCase
from django.utils.timezone import now
from datetime import timedelta


class TimeSincePostedCalculatorTest(TestCase):
    """
    Testing TimeSincePostedCalculator class
    """
    def test_more_than_a_year(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=800, seconds=20),
                         now()).calculate_string(), '2 years ago')

    def test_one_year(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=400, seconds=20),
                         now()).calculate_string(), '1 year ago')

    def test_a_few_months(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=95, seconds=20),
                                                   now()).calculate_string(), '3 months ago')

    def test_one_month(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=37, seconds=20),
                                                   now()).calculate_string(), '1 month ago')

    def test_a_few_days(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=20, seconds=20),
                                                   now()).calculate_string(), '20 days ago')

    def test_one_day(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=1, seconds=200),
                                                   now()).calculate_string(), '1 day ago')

    def test_a_few_hours(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=0, seconds=7400),
                                                   now()).calculate_string(), '2 hours ago')

    def test_one_hour(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=0, seconds=4000),
                                                   now()).calculate_string(), '1 hour ago')

    def test_a_few_minutes(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=0, seconds=267),
                                                   now()).calculate_string(), '4 minutes ago')

    def test_one_minute(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=0, seconds=62),
                                                   now()).calculate_string(), '1 minute ago')

    def test_just_now(self):
        self.assertEqual(TimeSincePostedCalculator(now() - timedelta(days=0, seconds=55),
                                                   now()).calculate_string(), 'Just now')
