from flask import Blueprint, render_template, jsonify, request
from services.chest_service import get_chest_route_call, get_chest_script, analyze_drops, update_chest_loot
from services.item_service import get_item_name, get_item_pic_url, get_item_resource

bp = Blueprint('chests', __name__)


@bp.route('/chests')
def chest_list():
    chest_mids = [929, 2578]
    # Получаем данные
    chest_data, file_paths = get_chest_route_call(chest_mids)
    
    # Группируем предметы по MID с помощью словаря
    items_by_mid = {}
    for item in chest_data:
        if item['MID'] not in items_by_mid:
            items_by_mid[item['MID']] = []
        items_by_mid[item['MID']].append(item)
    
    # Формируем финальный список, используя словарь
    formatted_items = [
        items_by_mid.get(mid, [{
            'MID': mid,
            'MID_pic': '',
            'MName': 'Unknown',
            'item_id': 0,
            'item_name': 'No items',
            'item_pic': '',
            'drop_chance': 0
        }]) for mid in chest_mids
    ]
    
    return render_template(
        'chest_core/chests.html',
        ChestMid=chest_mids,
        items=formatted_items,
        item_resources=file_paths
    )
    
@bp.route('/api/item-info/<int:item_id>')
def get_item_info(item_id):
    """Получение информации о предмете"""
    try:
        item_name = get_item_name(item_id)
        item_pic = get_item_pic_url(get_item_resource(item_id))
        
        return jsonify({
            'itemName': item_name,
            'itemPic': item_pic
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/chest-loot/<int:mid>')
def get_chest_loot(mid):
    """Получение текущего содержимого сундука"""
    try:
        script = get_chest_script(mid)
        if not script:
            return jsonify({'items': []})
            
        drops, _ = analyze_drops(mid)
        if not drops:
            return jsonify({'items': []})
            
        items = [{
            'itemId': drop['item_id'],
            'itemName': drop['item_name'],
            'itemPic': drop['item_pic'],
            'MName': drop['MName'],
            'MID_pic': drop['MID_pic'],
            'dropChance': round(drop['drop_chance'] / 100),  # Конвертируем в проценты
            'count': drop.get('count', 1),  # Получаем количество или используем 1 по умолчанию
            'status': drop.get('status', 1)  # Получаем статус или используем 1 (обычный) по умолчанию
        } for drop in drops]
            
        return jsonify({'items': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/save-chest-loot', methods=['POST'])
def save_chest_loot():
    """Сохранение обновленного содержимого сундука"""
    try:
        data = request.json
        mid = data['mid']
        items = data['items']
        
        success = update_chest_loot(mid, items)
        
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Failed to update chest loot'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500