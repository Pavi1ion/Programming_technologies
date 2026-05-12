import re
import logging
from datetime import date as DateType
from datetime import datetime
from typing import List, Tuple, Any

logging.basicConfig(filename='errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class FuelPriceParseError(Exception):
    pass

class FuelPrice:
    def __init__(self, fuel_type: str, date: DateType, price: float):
        self._type = fuel_type
        self._date = date
        self._price = price

    @property
    def type(self): return self._type
    @property
    def date(self): return self._date
    @property
    def price(self): return self._price

    def __str__(self):
        return f'"{self._type}" {self._date.strftime("%Y.%m.%d")} {self._price:.2f}'

    @staticmethod
    def from_string(line: str):
        line = line.strip()
        # старый формат с кавычками и пробелами (для совместимости)
        pattern_old = r'^"([^"]+)"\s+(\d{4}\.\d{2}\.\d{2})\s+(\d+(?:\.\d+)?)$'
        # новый CSV формат: тип; дата; цена   (без кавычек)
        pattern_csv = r'^([^;]+);\s*(\d{4}\.\d{2}\.\d{2});\s*(\d+(?:\.\d+)?)$'
        match = re.match(pattern_old, line)
        if not match:
            match = re.match(pattern_csv, line)
        if not match:
            raise FuelPriceParseError(f"Неверный формат: {line}")
        fuel_type = match.group(1).strip()
        try:
            date = datetime.strptime(match.group(2), "%Y.%m.%d").date()
        except ValueError:
            raise FuelPriceParseError(f"Неверная дата: {match.group(2)}")
        try:
            price = float(match.group(3))
        except ValueError:
            raise FuelPriceParseError(f"Неверная цена: {match.group(3)}")
        return FuelPrice(fuel_type, date, price)

    def to_csv(self) -> str:
        return f"{self._type};{self._date.strftime('%Y.%m.%d')};{self._price:.2f}"


class DataHandler:
    @staticmethod
    def load(filename: str) -> List[FuelPrice]:
        items = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        items.append(FuelPrice.from_string(line))
                    except FuelPriceParseError as e:
                        logging.error(f"Строка {line_num}: {e} | Содержимое: {line.strip()}")
                        continue
        except FileNotFoundError:
            pass
        return items

    @staticmethod
    def save(filename: str, items: List[FuelPrice]):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(str(item) + '\n')

    @staticmethod
    def save_csv(filename: str, items: List[FuelPrice]):
        """Сохраняет в CSV-формате (тип;дата;цена) без кавычек"""
        with open(filename, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(item.to_csv() + '\n')


class ConditionParser:
    """Разбирает строку условия вида: поле оператор значение"""
    # допустимые операторы
    operators = {
        '<': lambda a, b: a < b,
        '>': lambda a, b: a > b,
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '<=': lambda a, b: a <= b,
        '>=': lambda a, b: a >= b,
    }

    @classmethod
    def parse(cls, condition_str: str):
        condition_str = condition_str.strip()
        # регулярное выражение для извлечения field op value
        # поле может быть: type, date, price
        # значение: число, строка в кавычках, дата в формате ГГГГ.ММ.ДД
        pattern = r'^(type|date|price)\s+(==|!=|<|>|<=|>=)\s+(.+)$'
        match = re.match(pattern, condition_str)
        if not match:
            raise ValueError(f"Неверный формат условия: {condition_str}")
        field, op, val_str = match.groups()
        val_str = val_str.strip().strip('"')
        # преобразуем значение к нужному типу
        if field == 'price':
            try:
                value = float(val_str)
            except ValueError:
                raise ValueError(f"Цена должна быть числом: {val_str}")
        elif field == 'date':
            try:
                value = datetime.strptime(val_str, "%Y.%m.%d").date()
            except ValueError:
                raise ValueError(f"Неверный формат даты: {val_str} (ожидается ГГГГ.ММ.ДД)")
        elif field == 'type':
            value = val_str
        else:
            raise ValueError(f"Неизвестное поле: {field}")
        op_func = cls.operators.get(op)
        if not op_func:
            raise ValueError(f"Неизвестный оператор: {op}")
        return field, op_func, value

    @classmethod
    def evaluate(cls, item: FuelPrice, condition_str: str) -> bool:
        field, op_func, expected = cls.parse(condition_str)
        if field == 'type':
            actual = item.type
        elif field == 'date':
            actual = item.date
        elif field == 'price':
            actual = item.price
        else:
            return False
        return op_func(actual, expected)


class CommandProcessor:
    """Обрабатывает команды ADD, REM, SAVE из файла"""
    @staticmethod
    def apply_commands(items: List[FuelPrice], commands_file: str) -> List[FuelPrice]:
        with open(commands_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    items = CommandProcessor._process_line(items, line, line_num)
                except Exception as e:
                    logging.error(f"Команда стр. {line_num}: {line} -> {e}")
        return items

    @staticmethod
    def _process_line(items: List[FuelPrice], line: str, line_num: int) -> List[FuelPrice]:
        if line.upper().startswith('ADD '):
            # ADD тип; дата; цена
            data_str = line[4:].strip()
            try:
                new_item = FuelPrice.from_string(data_str)  # from_string поддерживает CSV
                items.append(new_item)
            except FuelPriceParseError as e:
                raise ValueError(f"Ошибка ADD: {e}")
        elif line.upper().startswith('REM '):
            condition = line[4:].strip()
            new_items = [it for it in items if not ConditionParser.evaluate(it, condition)]
            items = new_items
        elif line.upper().startswith('SAVE '):
            filename = line[5:].strip()
            DataHandler.save_csv(filename, items)
        else:
            raise ValueError(f"Неизвестная команда: {line}")
        return items