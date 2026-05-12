import unittest
import tempfile
import os
from model import FuelPrice, DataHandler, FuelPriceParseError

class TestFuelPrice(unittest.TestCase):
    def test_valid_string(self):
        fp = FuelPrice.from_string('"АИ-95" 2025.03.12 45.67')
        self.assertEqual(fp.type, "АИ-95")
        self.assertEqual(fp.date.strftime("%Y.%m.%d"), "2025.03.12")
        self.assertEqual(fp.price, 45.67)

    def test_missing_quotes(self):
        with self.assertRaises(FuelPriceParseError):
            FuelPrice.from_string('АИ-95 2025.03.12 45.67')

    def test_invalid_date(self):
        with self.assertRaises(FuelPriceParseError):
            FuelPrice.from_string('"АИ-95" 2025.13.12 45.67')

    def test_invalid_price(self):
        with self.assertRaises(FuelPriceParseError):
            FuelPrice.from_string('"АИ-95" 2025.03.12 abc')

class TestDataHandler(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.tmp.write('"АИ-95" 2025.03.12 45.67\n')
        self.tmp.write('Некорректная строка\n')
        self.tmp.write('"ДТ" 2025.04.01 48.80\n')
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_load_skips_invalid(self):
        items = DataHandler.load(self.tmp.name)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].type, "АИ-95")
        self.assertEqual(items[1].type, "ДТ")

if __name__ == '__main__':
    unittest.main()