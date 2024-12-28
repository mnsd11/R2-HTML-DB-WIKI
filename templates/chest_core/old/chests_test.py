import pyodbc
import pandas as pd
from typing import List, Dict, Tuple
import re

class R2DropAnalyzer:
    def __init__(self, connection_string: str):
        self.conn_str = connection_string

    def get_chest_script(self, chest_mid: int) -> str:
        query = """
        SELECT mScriptText 
        FROM TblDialogScript 
        WHERE mMId = ?
        """
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(query, chest_mid)
            result = cursor.fetchone()
            return result[0] if result else ''

    def get_item_name(self, item_id: int) -> str:
        query = """
        SELECT IName 
        FROM DT_Item 
        WHERE IID = ?
        """
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(query, item_id)
                result = cursor.fetchone()
                return result[0] if result else "Неизвестный предмет"
        except Exception as e:
            print(f"Ошибка при получении названия предмета {item_id}: {e}")
            return "Ошибка получения названия"

    def parse_script(self, script: str) -> List[Dict]:
        drops = []
        current_item = None
        current_chance = None
        
        # Разбиваем скрипт на строки
        lines = [line.strip() for line in script.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            # Ищем pushitem2
            if 'pushitem2(' in line:
                match = re.search(r'pushitem2\((\d+),', line)
                if match:
                    current_item = int(match.group(1))
                    # Ищем шанс в следующих строках
                    for next_line in lines[i:i+3]:  # Проверяем следующие 3 строки
                        if 'rand <=' in next_line:
                            chance_match = re.search(r'rand <= (\d+)', next_line)
                            if chance_match:
                                chance = int(chance_match.group(1))
                                item_name = self.get_item_name(current_item)
                                print(f"Найден предмет Название: {item_name}, ID: {current_item}, Шанс: {chance}")
                                drops.append({
                                    'item_id': current_item,
                                    'item_name': item_name,
                                    'drop_chance': chance
                                })
                                break

        # Сортируем по шансу от большего к меньшему
        drops.sort(key=lambda x: x['drop_chance'], reverse=True)
        return drops

    def analyze_drops(self, chest_mid: int) -> None:
        print(f"\nАнализ содержимого сундука для MID: {chest_mid}\n")
        
        # Получаем скрипт
        script = self.get_chest_script(chest_mid)
        
        # Парсим скрипт
        drops = self.parse_script(script)
        
        if not drops:
            print("Нет данных для анализа")
            return
        
        print("\nОтсортированный список предметов по шансу выпадения:")
        print("-" * 80)
        print(f"{'Название предмета':<40} {'ID':<8} {'Шанс':<6}")
        print("-" * 80)
        for drop in drops:
            print(f"{drop['item_name']:<40} {drop['item_id']:<8} {drop['drop_chance']:<6}")
        print("-" * 80)

def main():
    connection_string = (
        "DRIVER={SQL Server};"
        "SERVER=localhost;"
        "DATABASE=FNLParm1602;"
        "UID=sa;"
        "PWD=pass;"
    )
    
    ChestMID = [929, 2578] # MID NPC (Золотой: 929, Изумрудный: 2578)
    
    try:
        analyzer = R2DropAnalyzer(connection_string)
        for mid in ChestMID:
            analyzer.analyze_drops(mid)
        
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")

if __name__ == "__main__":
    main()