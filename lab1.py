import sys
from datetime import datetime

def parse_fuel_price(line):
    """Парсит строку формата: "тип" гггг.мм.дд цена. Возвращает словарь или None."""
    line = line.strip()
    if not line.startswith('"'):
        return None
    # Разделяем по пробелам, но учитываем кавычки
    parts = line.split(' ', 2)
    if len(parts) < 3:
        return None
    fuel_type = parts[0].strip('"')
    date_str = parts[1]
    price_str = parts[2]
    try:
        date = datetime.strptime(date_str, "%Y.%m.%d").date()
        price = float(price_str)
        return {"type": fuel_type, "date": date, "price": price}
    except:
        return None

def load_data(filename):
    items = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            obj = parse_fuel_price(line)
            if obj:
                items.append(obj)
    return items

def main():
    filename = "data.txt"
    try:
        items = load_data(filename)
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        sys.exit(1)

    print("Список объектов 'Цена топлива':")
    for i, obj in enumerate(items, 1):
        print(f"{i}. Тип: {obj['type']}, Дата: {obj['date']}, Цена: {obj['price']:.2f}")

if __name__ == "__main__":
    main()