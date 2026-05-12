# model.py
import re
from datetime import date as DateType
from datetime import datetime

class FuelPrice:
    """Модель одного объекта 'Цена топлива'."""
    def __init__(self, fuel_type: str, date: DateType, price: float):
        self._type = fuel_type
        self._date = date
        self._price = price

    @property
    def type(self):
        return self._type

    @property
    def date(self):
        return self._date

    @property
    def price(self):
        return self._price

    def __str__(self):
        return f'"{self._type}" {self._date.strftime("%Y.%m.%d")} {self._price:.2f}'

    @staticmethod
    def from_string(line: str):
        """Преобразует строку в объект FuelPrice. В случае ошибки бросает ValueError."""
        line = line.strip()
        pattern = r'^"([^"]+)"\s+(\d{4}\.\d{2}\.\d{2})\s+(\d+(?:\.\d+)?)$'
        match = re.match(pattern, line)
        if not match:
            raise ValueError(f"Неверный формат: {line}")
        fuel_type = match.group(1)
        try:
            date = datetime.strptime(match.group(2), "%Y.%m.%d").date()
        except ValueError:
            raise ValueError(f"Неверная дата: {match.group(2)}")
        try:
            price = float(match.group(3))
        except ValueError:
            raise ValueError(f"Неверная цена: {match.group(3)}")
        return FuelPrice(fuel_type, date, price)


class DataHandler:
    """Отвечает за загрузку и сохранение списка объектов в файл."""
    @staticmethod
    def load(filename: str):
        items = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    items.append(FuelPrice.from_string(line))
                except ValueError as e:
                    # В lab2 просто пропускаем некорректные строки (без логирования)
                    print(f"Пропущена строка: {e}")
                    continue
        return items

    @staticmethod
    def save(filename: str, items):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(str(item) + '\n')