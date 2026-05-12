import re
import logging
from datetime import date as DateType
from datetime import datetime

# Настройка логирования: ошибки пишутся в файл errors.log
logging.basicConfig(filename='errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class FuelPriceParseError(Exception):
    """Исключение, возникающее при ошибке парсинга строки."""
    pass

class FuelPrice:
    """Модель одного объекта 'Цена топлива'."""
    def __init__(self, fuel_type: str, date: DateType, price: float):
        self._type = fuel_type
        self._date = date
        self._price = price

    @property
    def type(self) -> str:
        return self._type

    @property
    def date(self) -> DateType:
        return self._date

    @property
    def price(self) -> float:
        return self._price

    def __str__(self) -> str:
        return f'"{self._type}" {self._date.strftime("%Y.%m.%d")} {self._price:.2f}'

    @staticmethod
    def from_string(line: str):
        """Преобразует строку в объект FuelPrice. При ошибке бросает FuelPriceParseError."""
        line = line.strip()
        pattern = r'^"([^"]+)"\s+(\d{4}\.\d{2}\.\d{2})\s+(\d+(?:\.\d+)?)$'
        match = re.match(pattern, line)
        if not match:
            raise FuelPriceParseError(f"Неверный формат: {line}")
        fuel_type = match.group(1)
        try:
            date = datetime.strptime(match.group(2), "%Y.%m.%d").date()
        except ValueError:
            raise FuelPriceParseError(f"Неверная дата: {match.group(2)}")
        try:
            price = float(match.group(3))
        except ValueError:
            raise FuelPriceParseError(f"Неверная цена: {match.group(3)}")
        return FuelPrice(fuel_type, date, price)


class DataHandler:
    """Отвечает за загрузку и сохранение списка объектов в файл."""
    @staticmethod
    def load(filename: str):
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
            # Если файла нет, возвращаем пустой список
            pass
        return items

    @staticmethod
    def save(filename: str, items):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(str(item) + '\n')