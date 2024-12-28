from services.item_service import (
    apply_filters,
    item_to_dict,
    get_item_by_id,
    get_quest_items,
    get_item_resource,
    get_items_by_type,
    get_item_model_resource,
    get_specific_proc_item,
    get_itemabnormalResist_data,
    get_rune_bead_data,
    get_item_bead_module_data,
    get_item_bead_holeprob_data,
    get_item_attribute_add_data,
    get_item_attribute_resist_data,
    get_item_protect_data,
    get_item_slain_data,
    get_item_panalty_data
)
from services.monster_service import get_monster_drop_info
from services.merchant_service import get_merchant_sellers
from services.craft_service import (
    check_base_items_for_craft,
    check_next_craft_item
)
from flask import Blueprint, render_template, jsonify, request, render_template
from services.skill_service import get_item_skill, get_sid_by_spid
from services.abnormal_service import get_abnormal_in_skill
from functools import wraps

bp = Blueprint('items', __name__)



# TODO: Это тест фильтр, нужно доделать. Очень долго грузит отфильтрованные данные, Под каждую страницу свои фильтры. Сделать фильтры для: Монстров, Абнормал и Скиллов (всего остального)
# ! Работает только /weapon --&gt; @with_filters([1, 18, 20]) | Далее смотреть item_service.py --&gt; apply_filters / item_to_dict | Далее все скрипты, css и остальное от фильтров в item_page_table_filter.html
# Глобальная переменная для кэширования данных
cached_data = None

def load_data_once(item_types, search_term=''):
    """Функция для загрузки данных при старте"""
    global cached_data
    if cached_data is None:
        #print("Loading items for the first time...")  # Отладочная информация
        items, file_paths = get_items_by_type(item_types, search_term)
        cached_data = {'items': items, 'file_paths': file_paths}
    else:
        print("Using cached data...")  # Отладочная информация

def with_filters(item_types):
    """Декоратор для добавления фильтрации к роутам"""
    def decorator(original_route):
        @wraps(original_route)
        def wrapped_route(*args, **kwargs):
            global cached_data

            try:
                # Загружаем данные при первом запуске
                if cached_data is None:
                    search_term = request.args.get('search', '')  # Или по умолчанию пустая строка
                    load_data_once(item_types, search_term)
                
                # Если это AJAX запрос, возвращаем только отфильтрованные данные
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    filters = request.args.to_dict()
                    search_term = filters.pop('search', '') if 'search' in filters else ''
                    
                    #print(f"Received filters: {filters}")  # Отладочная информация
                    
                    items = cached_data['items']
                    file_paths = cached_data['file_paths']

                    #print(f"Found {len(items)} items before filtering")  # Отладочная информация
                    
                    # Применяем фильтры
                    filtered_items = apply_filters(items, filters)
                    #print(f"Found {len(filtered_items)} items after filtering")  # Отладочная информация
                    
                    # Конвертируем предметы в словари
                    items_dict = [item_to_dict(item) for item in filtered_items]
                    
                    return jsonify({
                        'items': items_dict,
                        'resources': file_paths
                    })
                
                # Иначе возвращаем полную страницу
                return original_route(*args, **kwargs)
                
            except Exception as e:
                print(f"Error in route: {str(e)}")
                import traceback
                traceback.print_exc()  # Добавьте это для полного стека ошибки
                return jsonify({'error': str(e)}), 500
                
        return wrapped_route
    return decorator




@bp.route('/item/&lt;int:item_id&gt;')
def item_detail(item_id: int):
    """Страница деталей предмета"""
    # Проверка основных данных
    if not (item := get_item_by_id(item_id)):
        return "Item not found", 404

    if not (item_resource := get_item_resource(item_id)):
        return "Item resource not found", 404

    # Обработка класса использования
    use_class = int(item.IUseClass.split('/')[-1].replace('.png', ''))

    # Получение связанных данных
    mondropinfo = get_monster_drop_info(item_id)
    merchant_sellers = get_merchant_sellers(item_id)
    craft_items = check_base_items_for_craft(item_id)
    craft_next_item = check_next_craft_item(item_id)
    skill_data = get_item_skill(item_id)
    specificproc_check = get_specific_proc_item(item_id)
    
    # Обработка данных навыков
    abnormal_type_data = abnormal_type_pic = None
    itemdskill_data = itemskill_pic = None
    linked_skills = linked_skillsaid = 0
    transform_list = monster_pic_url = None

    if skill_data and isinstance(skill_data, tuple) and len(skill_data) == 6:
        itemdskill_data, itemskill_pic, linked_skills, linked_skillsaid, transform_list, monster_pic_url = skill_data
        abnormal_type_data, abnormal_type_pic = get_abnormal_in_skill(linked_skillsaid)

    # Обработка модели предмета
    prefix = item_model_no = None
    if itemresource_result := get_item_model_resource(item_id):
        base = f"{int(itemresource_result.RPosX):03}{int(itemresource_result.RPosY):03}"
        prefix = 'i'
        item_model_no = base

        if item.IType == 3:  # Доспехи
            prefix = 'p'
            replace_dict = {
                1: [0, 1], 
                2: [2, 3], 
                4: [4, 5], 
                5: [0, 1, 4, 5],
                7: [4, 5, 0, 1, 2, 3], 
                8: [6, 7], 
                15: [0, 1, 2, 3, 4, 5, 6, 7],
                16: [8, 9], 
                18: [8, 9, 2, 3], 
                19: [8, 9, 2, 3, 0, 1],
                20: [8, 9, 4, 5], 
                22: [8, 9, 4, 5, 2, 3],
                23: [0, 1, 2, 3, 4, 5, 8, 9], 
                0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                255: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            }
            if use_class in replace_dict:
                for index in replace_dict[use_class]:
                    item_model_no = f"0{index}0{base[3:]}"
        elif item.IType not in [1, 18, 20, 2, 19]:  # Не оружие/щит/стрелы
            prefix = 'i'  # TODO: ЗАГЛУШКА ДЛЯ ОСТАЛЬНОГО!

    # Проверка DT_ItemAbnormalResist
    item_abnormalResist_data = get_itemabnormalResist_data(item_id) or None
    
    # Проверка DT_Bead и активации навыков
    rune_bead_data = activation_bead_data = activation_bead_pic = None
    if item.IName.startswith('Руна'):
        if (rune_bead_data := get_rune_bead_data(item_id)) and rune_bead_data.mBeadType == 2:
            activation_bead_data, activation_bead_pic = get_sid_by_spid(rune_bead_data.mParamA)
    
    # Получение дополнительных данных предмета
    item_bead_module_data = get_item_bead_module_data(item_id) or None
    item_bead_holeprob_data = get_item_bead_holeprob_data(item_id) or None
    
    item_attribute_add_data = get_item_attribute_add_data(item_id) or None
    item_attribute_resist_data = get_item_attribute_resist_data(item_id) or None
    
    item_protect_data = get_item_protect_data(item_id) or None

    item_slain_data = get_item_slain_data(item_id) or None
    
    item_panalty_data = get_item_panalty_data(item_id) or None
    

    
    # Рендеринг шаблона с данными
    return render_template(
        'item_core/item_page_detail.html',
        item=item,
        file_path=item_resource.file_path,
        mondropinfo=mondropinfo,
        merchant_sellers=merchant_sellers,
        monstermodelno_result=item_model_no,
        prefix=prefix,
        use_class=use_class,
        craft_result=craft_items,
        craft_next=craft_next_item,
        itemdskill_data=itemdskill_data,
        itemskill_pic=itemskill_pic,
        linked_skills=linked_skills,
        linked_skillsaid=linked_skillsaid,
        abnormal_type_data=abnormal_type_data,
        abnormal_type_pic=abnormal_type_pic,
        specificproc_data=specificproc_check,
        transform_list=transform_list,
        monster_pic_url=monster_pic_url,
        item_abnormalResist_data=item_abnormalResist_data,
        rune_bead_data=rune_bead_data,
        activation_bead_data=activation_bead_data,
        activation_bead_pic=activation_bead_pic,
        item_bead_module_data=item_bead_module_data,
        item_bead_holeprob_data=item_bead_holeprob_data,
        item_attribute_add_data=item_attribute_add_data,
        item_attribute_resist_data=item_attribute_resist_data,
        item_protect_data=item_protect_data,
        item_slain_data=item_slain_data,
        item_panalty_data=item_panalty_data
    )

# Item type routes
@bp.route('/all_weapon')
@with_filters(list(range(1, 42)))  # Преобразуем range в список
def all_weapon():
    search_term = request.args.get('search', '')
    item_types = list(range(1, 42))  # Преобразуем range в список
    items, file_paths = get_items_by_type(item_types, search_term)
    
    return render_template('item/weapon.html', items_wep=items, item_resources=file_paths)


@bp.route('/weapon')
@with_filters([1, 18, 20])
def weapon():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([1, 18, 20], search_term)
    
    return render_template('item/weapon.html', items_wep=items, item_resources=file_paths)


@bp.route('/armor')
@with_filters([3])
def armor():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([3], search_term)
    return render_template('item/armor.html', items_wep=items, item_resources=file_paths)

@bp.route('/gloves')
@with_filters([7])
def gloves():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([7], search_term)
    return render_template('item/gloves.html', items_wep=items, item_resources=file_paths)

@bp.route('/boots')
@with_filters([6])
def boots():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([6], search_term)
    return render_template('item/boots.html', items_wep=items, item_resources=file_paths)

@bp.route('/helmet')
@with_filters([8])
def helmet():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([8], search_term)
    return render_template('item/helmet.html', items_wep=items, item_resources=file_paths)

@bp.route('/shield')
@with_filters([2])
def shield():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([2], search_term)
    return render_template('item/shield.html', items_wep=items, item_resources=file_paths)

@bp.route('/arrows')
@with_filters([19])
def arrows():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([19], search_term)
    return render_template('item/arrows.html', items_wep=items, item_resources=file_paths)

@bp.route('/cloak')
@with_filters([17])
def cloak():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([17], search_term)
    return render_template('item/cloak.html', items_wep=items, item_resources=file_paths)

@bp.route('/materials')
@with_filters([10, 16])
def materials():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([10, 16], search_term)
    return render_template('item/materials.html', items_wep=items, item_resources=file_paths)

@bp.route('/ring')
@with_filters([4])
def ring():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([4], search_term)
    return render_template('item/ring.html', items_wep=items, item_resources=file_paths)

@bp.route('/belt')
@with_filters([9])
def belt():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([9], search_term)
    return render_template('item/belt.html', items_wep=items, item_resources=file_paths)

@bp.route('/necklace')
@with_filters([5])
def necklace():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([5], search_term)
    return render_template('item/necklace.html', items_wep=items, item_resources=file_paths)

@bp.route('/earrings')
@with_filters([42])
def earrings():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([42], search_term)
    return render_template('item/earrings.html', items_wep=items, item_resources=file_paths)

@bp.route('/books')
@with_filters([12])
def books():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([12], search_term)
    return render_template('item/books.html', items_wep=items, item_resources=file_paths)

@bp.route('/potions')
@with_filters([10])
def potions():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([10], search_term)
    return render_template('item/potions.html', items_wep=items, item_resources=file_paths)

@bp.route('/etc')
@with_filters([14, 16, 13, 11])
def etc():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([14, 16, 13, 11], search_term)
    return render_template('item/etc.html', items_wep=items, item_resources=file_paths)

@bp.route('/quest')
#@with_filters(IType)
def quest():
    """Get quest items"""
    item_ids = get_quest_items()
    IType = [item[1] for item in item_ids]
    

    items, file_paths = get_items_by_type(IType)
    
    return render_template('item/quest.html', items_wep=items, item_resources=file_paths)

@bp.route('/event')
@with_filters([15])
def event():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([15], search_term)
    return render_template('item/event.html', items_wep=items, item_resources=file_paths)

@bp.route('/sphere')
@with_filters([22, 23, 24, 25, 26, 27, 28, 29])
def sphere():
    search_term = request.args.get('search', '')
    items, file_paths = get_items_by_type([22, 23, 24, 25, 26, 27, 28, 29], search_term)
    return render_template('item/sphere.html', items_wep=items, item_resources=file_paths)