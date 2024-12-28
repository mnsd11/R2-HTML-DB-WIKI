from flask import Blueprint, render_template, current_app
from services.skill_service import (
    get_skill_detail,
    get_skills_list,
    get_skill_use_by_spid_items,
    get_skill_use_by_sid,
    get_monster_reget_skill_pic_icon_datasource,
    get_skill_attribute_data,
    get_skill_slain_data
)
from services.utils import get_google_sheets_data
from config.settings import SKILLAPPLYRACE_URL
from services.database import execute_query
from services.utils import get_skill_icon_path, clean_dict

bp = Blueprint('skills', __name__)

@bp.route('/skill/<int:skill_id>')
def skill_detail(skill_id: int):
    """Страница деталей навыка"""
    # Получение основных данных навыка
    if not (skills := get_skill_detail(skill_id)):
        return "Skill not found", 404
    
    skill = skills[0]  # Берем первый навык для основной информации
    spid_id = skill.skill_pack_id
    
    # Получение данных связанных предметов и навыков
    skill_for_item = get_skill_use_by_spid_items(spid_id)
    skill_for_item_data, skill_for_item_pic = skill_for_item or (None, None)
    
    skill_for_skill = get_skill_use_by_sid(spid_id)
    skill_for_skill_data, skill_for_skill_pic = skill_for_skill or (None, None)
    
    # Обработка класса использования
    use_class = None
    if skill.item_use_class:
        try:
            use_class = int(skill.item_use_class.split('/')[-1].replace('.png', ''))
        except (ValueError, AttributeError):
            pass
    
    # Получение информации о расе из Google Sheets
    race_info = None
    if skill.apply_race is not None:
        skill_apply_race_df = get_google_sheets_data(SKILLAPPLYRACE_URL)
        if not skill_apply_race_df.empty:
            race_match = skill_apply_race_df[skill_apply_race_df['mApplyRace'] == skill.apply_race]
            if not race_match.empty:
                race_info = race_match.iloc[0]['mDesc']
    
    # Получение иконки навыка
    skill_icon = None
    if icon_data := get_monster_reget_skill_pic_icon_datasource(skill_id):
        skill_icon = get_skill_icon_path(
            icon_data.mSpriteFile,
            icon_data.mSpriteX,
            icon_data.mSpriteY
        )
    
    
    skill_attribute_add_data = get_skill_attribute_data(skill_id) or None
    
    skill_slain_data = get_skill_slain_data(skill_id) or None

    return render_template(
        'skill_core/skill_page_detail.html',
        skill=skill,
        skills=skills,
        use_class=use_class,
        race_info=race_info,
        skill_icon=skill_icon,
        skill_for_item_data=skill_for_item_data,
        skill_for_item_pic=skill_for_item_pic,
        skill_for_skill_data=skill_for_skill_data,
        skill_for_skill_pic=skill_for_skill_pic,
        skill_attribute_add_data=skill_attribute_add_data,
        skill_slain_data=skill_slain_data
    )

@bp.route('/skills')
def skills_list():
    """List all skills"""
    skills_data, file_paths = get_skills_list()
    return render_template(
        'skill_core/skill_page_route.html', # TODO: Старый дизайн
        skills=skills_data,
        item_resources=file_paths
    )