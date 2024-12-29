import re
from collections import OrderedDict

def normalize_css_rule(rule):
    """
    Нормализует CSS правило для сравнения:
    - Удаляет пробелы и переносы строк
    - Сортирует свойства внутри правила
    """
    # Извлекаем селектор и содержимое правила
    match = re.match(r'([^{]*){([^}]*)}', rule.strip())
    if not match:
        return rule.strip()
    
    selector, properties = match.groups()
    
    # Нормализуем селектор
    selector = ' '.join(selector.split())
    
    # Разбиваем свойства на отдельные пары ключ-значение и сортируем их
    properties = [prop.strip() for prop in properties.split(';') if prop.strip()]
    properties.sort()
    
    # Собираем правило обратно
    return f"{selector} {{{'; '.join(properties)}}}"

def split_css_into_rules(css_content):
    """
    Разбивает CSS на отдельные правила, сохраняя медиа-запросы и keyframes
    """
    # Паттерн для поиска CSS правил, включая медиа-запросы и keyframes
    pattern = r'(?:@media[^{]+{(?:[^{}]|{[^{}]*})*})|(?:@keyframes[^{]+{(?:[^{}]|{[^{}]*})*})|[^{}]+{[^{}]*}'
    
    rules = re.findall(pattern, css_content)
    return [rule.strip() for rule in rules if rule.strip()]

def remove_duplicate_css_rules(css_content):
    """
    Удаляет дублирующиеся CSS правила, сохраняя порядок и структуру
    Возвращает очищенный CSS и список дубликатов
    """
    # Разбиваем CSS на правила
    rules = split_css_into_rules(css_content)
    
    # Используем OrderedDict для сохранения порядка правил
    unique_rules = OrderedDict()
    duplicates = []
    
    for rule in rules:
        # Нормализуем правило для сравнения
        normalized_rule = normalize_css_rule(rule)
        if normalized_rule not in unique_rules:
            unique_rules[normalized_rule] = rule
        else:
            # Сохраняем информацию о дубликате
            original = unique_rules[normalized_rule]
            duplicates.append({
                'rule': rule.strip(),
                'matches_with': original.strip()
            })
    
    # Собираем CSS обратно
    return '\n\n'.join(unique_rules.values()), duplicates

def process_css_file(input_path, output_path):
    """
    Обрабатывает CSS файл, удаляя дублирующиеся правила
    """
    try:
        # Читаем входной файл
        with open(input_path, 'r', encoding='utf-8') as file:
            css_content = file.read()
        
        # Удаляем дубликаты
        cleaned_css, duplicates = remove_duplicate_css_rules(css_content)
        
        # Записываем результат
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_css)
        
        # Формируем отчёт
        if duplicates:
            report = [f"Найдено {len(duplicates)} дублирующихся правил:"]
            for i, dup in enumerate(duplicates, 1):
                report.append(f"\n{i}. Дубликат:\n{dup['rule']}\n   Совпадает с:\n{dup['matches_with']}")
            return True, "\n".join(report)
        else:
            return True, "Дубликаты не найдены"
    except Exception as e:
        return False, f"Ошибка при обработке CSS: {str(e)}"

# Пример использования
if __name__ == "__main__":
    input_file = "bad_css.css"
    output_file = "good_css_cleaned.css"
    
    success, message = process_css_file(input_file, output_file)
    print(message)