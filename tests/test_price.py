import unittest

from price import discounted


class DiscountTest(unittest.TestCase):
    def test_applies_discount(self):
        self.assertEqual(discounted(10000, 0.1), 9000)

    def test_caps_discount_at_thirty_percent(self):
        self.assertEqual(discounted(10000, 0.5), 7000)


if __name__ == "__main__":
    unittest.main()
