from flask import Blueprint, render_template
from services.abnormal_service import (
    get_abnormal_detail,
    get_abnormals_list,
    get_abnormal_items,
    get_abnormal_skills
)

bp = Blueprint('abnormals', __name__)

@bp.route('/abnormal/<int:aid>')
def abnormal_detail(aid: int):
    """Abnormal effect detail page"""
    abnormal = get_abnormal_detail(aid)
    if not abnormal:
        return "Abnormal effect not found", 404

    # Get related items and skills
    abnormal_items = get_abnormal_items(aid)
    abnormal_skills = get_abnormal_skills(aid)

    return render_template(
        'abnormal_core/abnormal_page_detail.html',
        abnormal=abnormal,
        abnormal_items=abnormal_items,
        abnormal_skills=abnormal_skills
    )

@bp.route('/abnormals')
def abnormals_list():
    """List all abnormal effects"""
    abnormals_data, file_paths = get_abnormals_list()
    
    return render_template(
        'abnormal_core/abnormal_page_route.html', # TODO: Старый дизайн
        abnormals=abnormals_data,
        item_resources=file_paths
    )