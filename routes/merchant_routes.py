from flask import Blueprint, render_template
from services.merchant_service import get_merchant_sell_list

bp = Blueprint('merchants', __name__)

@bp.route('/merchants')
def merchants_list():
    """List all merchants and their items"""
    merchants_data, file_paths = get_merchant_sell_list()
    return render_template(
        'merchant_core/merchant_page_route.html', # TODO: Старый дизайн
        items=merchants_data,
        item_resources=file_paths
    )