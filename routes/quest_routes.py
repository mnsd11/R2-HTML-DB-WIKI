from flask import Blueprint, render_template, jsonify, request
from services.quest_service import get_quests_data

bp = Blueprint('quests', __name__)

@bp.route('/quests')
def quest_list():
    # Получаем данные о квестах
    quests_data = get_quests_data()
    
    return render_template(
        'quest_core/quest.html',
        quests=quests_data
    )

@bp.route('/api/quest/<int:quest_no>')
def get_quest_details(quest_no):
    """Получение детальной информации о квесте"""
    try:
        quest_details = get_quest_details(quest_no)
        return jsonify(quest_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500