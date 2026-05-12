import unittest
import tempfile
import os
from model import FuelPrice, DataHandler, ConditionParser, CommandProcessor, FuelPriceParseError
from datetime import date

class TestFuelPrice(unittest.TestCase):
    def test_valid_string_old(self):
        fp = FuelPrice.from_string('"АИ-95" 2025.03.12 45.67')
        self.assertEqual(fp.type, "АИ-95")
        self.assertEqual(fp.date, date(2025,3,12))
        self.assertEqual(fp.price, 45.67)

    def test_valid_string_csv(self):
        fp = FuelPrice.from_string('АИ-95; 2025.03.12; 45.67')
        self.assertEqual(fp.type, "АИ-95")
        self.assertEqual(fp.date, date(2025,3,12))
        self.assertEqual(fp.price, 45.67)

    def test_invalid_format(self):
        with self.assertRaises(FuelPriceParseError):
            FuelPrice.from_string('АИ-95 2025.03.12 45.67')

    def test_to_csv(self):
        fp = FuelPrice("АИ-92", date(2025,1,10), 42.50)
        self.assertEqual(fp.to_csv(), "АИ-92;2025.01.10;42.50")

class TestConditionParser(unittest.TestCase):
    def test_parse_price_less(self):
        field, op, val = ConditionParser.parse("price < 100")
        self.assertEqual(field, "price")
        self.assertTrue(op(50, 100))
        self.assertFalse(op(150, 100))
        self.assertEqual(val, 100)

    def test_parse_type_equal(self):
        fp = FuelPrice("АИ-95", date(2025,3,12), 45.67)
        self.assertTrue(ConditionParser.evaluate(fp, 'type == "АИ-95"'))
        self.assertFalse(ConditionParser.evaluate(fp, 'type == "АИ-92"'))

    def test_parse_date_greater(self):
        fp = FuelPrice("АИ-95", date(2025,3,12), 45.67)
        self.assertTrue(ConditionParser.evaluate(fp, 'date > 2025.01.01'))
        self.assertFalse(ConditionParser.evaluate(fp, 'date > 2025.04.01'))

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        self.items = [
            FuelPrice("АИ-92", date(2025,1,10), 42.50),
            FuelPrice("АИ-95", date(2025,2,15), 45.67),
            FuelPrice("ДТ", date(2025,3,1), 48.80)
        ]

    def test_add_command(self):
        cmd_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        cmd_file.write("ADD АИ-98; 2025.04.01; 55.00\n")
        cmd_file.close()
        new_items = CommandProcessor.apply_commands(self.items, cmd_file.name)
        self.assertEqual(len(new_items), 4)
        self.assertEqual(new_items[-1].type, "АИ-98")
        os.unlink(cmd_file.name)

    def test_remove_command(self):
        cmd_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        cmd_file.write("REM price > 45\n")
        cmd_file.close()
        new_items = CommandProcessor.apply_commands(self.items, cmd_file.name)
        self.assertEqual(len(new_items), 1)
        self.assertEqual(new_items[0].type, "АИ-92")
        os.unlink(cmd_file.name)

    def test_save_command(self):
        out_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        out_file.close()
        cmd_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        cmd_file.write(f"SAVE {out_file.name}\n")
        cmd_file.close()
        new_items = CommandProcessor.apply_commands(self.items, cmd_file.name)
        with open(out_file.name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 3)
        os.unlink(cmd_file.name)
        os.unlink(out_file.name)

if __name__ == '__main__':
    unittest.main()