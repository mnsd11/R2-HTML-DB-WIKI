from typing import List, Dict, Optional, Tuple, Union, Any
from os.path import splitext
from functools import lru_cache
from flask import current_app
from models.item import (DT_Item, DT_ItemResource, TblSpecificProcItem, DT_ItemAbnormalResist,
DT_Bead, DT_ItemBeadModule, TblBeadHoleProb, DT_ItemAttributeAdd, 
DT_ItemAttributeResist, DT_ItemProtect, DT_ItemSlain, DT_ItemPanalty)

from services.database import execute_query
from services.utils import get_skill_icon_path, clean_description, get_google_sheets_data
from config.settings import ATTRIBUTE_TYPE_WEAPON_URL, ATTRIBUTE_TYPE_ARMOR_URL

# Фильтры
def apply_filters(items, filters):
    """Optimized filter function with debugging"""
    #print(f"Applying filters: {filters}")
    #print(f"Initial items count: {len(items)}")

    if not items or not filters:
        return items

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v and k != ''}
    if not filters:
        return items

    filtered_items = items

    try:
        # Process filters in order of most restrictive first
        if type_filter := filters.get('typeFilter'):
            #print(f"Applying type filter: {type_filter}")
            type_val = int(type_filter)
            filtered_items = [item for item in filtered_items if item.IType == type_val]
            #print(f"After type filter: {len(filtered_items)} items")
            if not filtered_items:
                return []

        # Level filter (common restriction)
        if filters.get('levelMin') or filters.get('levelMax'):
            level_min = int(filters.get('levelMin', 0))
            level_max = int(filters.get('levelMax', 999999))
            #print(f"Applying level filter: min={level_min}, max={level_max}")
            filtered_items = [item for item in filtered_items 
                            if level_min <= item.ILevel <= level_max]
            #print(f"After level filter: {len(filtered_items)} items")
            if not filtered_items:
                return []

        # Boolean filters (quick to process)
        bool_fields = {
            'stackableFilter': ('IMaxStack', lambda x: int(x) if x in ['0', '1'] else None),
            'eventItemFilter': ('IIsEvent', lambda x: bool(int(x))),
            'testItemFilter': ('IIsTest', lambda x: bool(int(x))),
            'indictFilter': ('IIsIndict', lambda x: bool(int(x))),
            'chargeFilter': ('IIsCharge', lambda x: bool(int(x))),
            'partyDropFilter': ('IIsPartyDrop', lambda x: bool(int(x)))
        }

        for filter_name, (attr, converter) in bool_fields.items():
            if filter_val := filters.get(filter_name):
                #print(f"Applying boolean filter {filter_name}: {filter_val}")
                val = converter(filter_val)
                if val is not None:
                    filtered_items = [item for item in filtered_items 
                                    if getattr(item, attr) == val]
                    #print(f"After {filter_name}: {len(filtered_items)} items")
                    if not filtered_items:
                        return []

        # Numeric range filters
        numeric_fields = {
            'IDHIT': ('IDHIT', float), 
            'IDDD': ('IDDD', float),
            'IRHIT': ('IRHIT', float), 
            'IRDD': ('IRDD', float),
            'IMHIT': ('IMHIT', float), 
            'IMDD': ('IMDD', float),
            'IHPPlus': ('IHPPlus', float),
            'IMPPlus': ('IMPPlus', float),
            'ISTR': ('ISTR', float),
            'IDEX': ('IDEX', float),
            'IINT': ('IINT', float),
            'IHPRegen': ('IHPRegen', float),
            'IMPRegen': ('IMPRegen', float),
            'IAttackRate': ('IAttackRate', float),
            'IMoveRate': ('IMoveRate', float),
            'ICritical': ('ICritical', float)
        }

        for field_base, (attr, converter) in numeric_fields.items():
            min_key = f"{field_base}Min"
            max_key = f"{field_base}Max"
            
            if min_val := filters.get(min_key):
                #print(f"Applying min filter {min_key}: {min_val}")
                min_val = converter(min_val)
                filtered_items = [item for item in filtered_items 
                                if converter(getattr(item, attr, 0) or 0) >= min_val]
                #print(f"After {min_key}: {len(filtered_items)} items")
                if not filtered_items:
                    return []
                    
            if max_val := filters.get(max_key):
                #print(f"Applying max filter {max_key}: {max_val}")
                max_val = converter(max_val)
                filtered_items = [item for item in filtered_items 
                                if converter(getattr(item, attr, 0) or 0) <= max_val]
                #print(f"After {max_key}: {len(filtered_items)} items")
                if not filtered_items:
                    return []

        # Weight filter (special handling for float)
        if filters.get('weightMin') or filters.get('weightMax'):
            weight_min = float(filters.get('weightMin', 0))
            weight_max = float(filters.get('weightMax', 999999))
            #print(f"Applying weight filter: min={weight_min}, max={weight_max}")
            filtered_items = [item for item in filtered_items 
                            if weight_min <= float(item.IWeight or 0) <= weight_max]
            #print(f"After weight filter: {len(filtered_items)} items")

        # Quest No filter
        if quest_no := filters.get('questNoFilter'):
            #print(f"Applying quest filter: {quest_no}")
            quest_val = int(quest_no)
            filtered_items = [item for item in filtered_items 
                            if item.IQuestNo == quest_val]
            #print(f"After quest filter: {len(filtered_items)} items")

        #print(f"Final filtered items count: {len(filtered_items)}")
        return filtered_items

    except Exception as e:
        print(f"Error in apply_filters: {e}")
        import traceback
        traceback.print_exc()
        return []

# Какие ячейки из запроса передаем на сайт для фильтров
def item_to_dict(item):
    """Конвертирует объект DT_Item в словарь со всеми нужными атрибутами"""
    return {
        'IID': item.IID,
        'IName': item.IName,
        'IType': item.IType,
        'ILevel': item.ILevel,
        'IWeight': float(item.IWeight) if item.IWeight else 0,
        'IDesc': item.IDesc.replace('\\n', ' ⭑ ') if item.IDesc else '',
        'IUseClass': item.IUseClass,
        'IMaxStack': item.IMaxStack,
        'IIsEvent': item.IIsEvent,
        'IIsTest': item.IIsTest,
        'IIsIndict': item.IIsIndict,
        'IIsCharge': item.IIsCharge,
        'IIsPartyDrop': item.IIsPartyDrop,
        'IQuestNo': item.IQuestNo,
        'ITermOfValidity': item.ITermOfValidity,
        'ITermOfValidityMi': item.ITermOfValidityMi,
        'IDHIT': item.IDHIT,
        'IDDD': item.IDDD,
        'IRHIT': item.IRHIT,
        'IRDD': item.IRDD,
        'IMHIT': item.IMHIT,
        'IMDD': item.IMDD,
        'IHPPlus': item.IHPPlus,
        'IMPPlus': item.IMPPlus,
        'ISTR': item.ISTR,
        'IDEX': item.IDEX,
        'IINT': item.IINT,
        'IHPRegen': item.IHPRegen,
        'IMPRegen': item.IMPRegen,
        'IAttackRate': item.IAttackRate,
        'IMoveRate': item.IMoveRate,
        'ICritical': item.ICritical,
        'IUseType': item.IUseType,
        'IUseNum': item.IUseNum,
        'IRecycle': item.IRecycle,
        'IStatus': item.IStatus,
        'IFakeID': item.IFakeID,
        'IFakeName': item.IFakeName,
        'IUseMsg': item.IUseMsg,
        'IRange': item.IRange,
        'IDropEffect': item.IDropEffect,
        'IUseLevel': item.IUseLevel,
        'IUseEternal': item.IUseEternal,
        'IUseDelay': item.IUseDelay,
        'IUseInAttack': item.IUseInAttack,
        'IAddWeight': item.IAddWeight,
        'ISubType': item.ISubType,
        'INationOp': item.INationOp,
        'IPShopItemType': item.IPShopItemType,
        'IQuestNeedCnt': item.IQuestNeedCnt,
        'IContentsLv': item.IContentsLv,
        'IIsConfirm': item.IIsConfirm,
        'IIsSealable': item.IIsSealable,
        'IAddDDWhenCritical': item.IAddDDWhenCritical,
        'mSealRemovalNeedCnt': item.mSealRemovalNeedCnt,
        'mIsPracticalPeriod': item.mIsPracticalPeriod,
        'mIsReceiveTown': item.mIsReceiveTown,
        'IIsReinforceDestroy': item.IIsReinforceDestroy,
        'IAddPotionRestore': item.IAddPotionRestore,
        'IAddMaxHpWhenTransform': item.IAddMaxHpWhenTransform,
        'IAddMaxMpWhenTransform': item.IAddMaxMpWhenTransform,
        'IAddAttackRateWhenTransform': item.IAddAttackRateWhenTransform,
        'IAddMoveRateWhenTransform': item.IAddMoveRateWhenTransform,
        'ISupportType': item.ISupportType,
        'ITermOfValidityLv': item.ITermOfValidityLv,
        'mIsUseableUTGWSvr': item.mIsUseableUTGWSvr,
        'IAddShortAttackRange': item.IAddShortAttackRange,
        'IAddLongAttackRange': item.IAddLongAttackRange,
        'IWeaponPoisonType': item.IWeaponPoisonType,
        'IDPV': item.IDPV,
        'IMPV': item.IMPV,
        'IRPV': item.IRPV,
        'IDDV': item.IDDV,
        'IMDV': item.IMDV,
        'IRDV': item.IRDV,
        'IHDPV': item.IHDPV,
        'IHMPV': item.IHMPV,
        'IHRPV': item.IHRPV,
        'IHDDV': item.IHDDV,
        'IHMDV': item.IHMDV,
        'IHRDV': item.IHRDV,
        'ISubDDWhenCritical': item.ISubDDWhenCritical,
        'IGetItemFeedback': item.IGetItemFeedback,
        'IEnemySubCriticalHit': item.IEnemySubCriticalHit,
        'IMaxBeadHoleCount': item.IMaxBeadHoleCount,
        'ISubTypeOption': item.ISubTypeOption,
        'mIsDeleteArenaSvr': item.mIsDeleteArenaSvr
    }





#@lru_cache(maxsize=10000)
def get_item_by_id(item_ids: Union[int, List[int]]) -> Union[Optional[DT_Item], List[Optional[DT_Item]]]:
    """Get item by ID with caching. Now supports both single ID and list of IDs"""
    single_id = isinstance(item_ids, int)
    ids = [item_ids] if single_id else item_ids
    
    if not ids:
        return None if single_id else []
        
    placeholders = ','.join('?' * len(ids))
    query = f"""
    SELECT 
        IID, IName, IType, ILevel, IDHIT, IDDD, IRHIT, IRDD, IMHIT, IMDD,
        IHPPlus, IMPPlus, ISTR, IDEX, IINT, IMaxStack, IWeight, IUseType,
        IUseNum, IRecycle, IHPRegen, IMPRegen, IAttackRate, IMoveRate,
        ICritical, ITermOfValidity, ITermOfValidityMi, IDesc, IStatus,
        IFakeID, IFakeName, IUseMsg, IRange, IUseClass, IDropEffect,
        IUseLevel, IUseEternal, IUseDelay, IUseInAttack, IIsEvent,
        IIsIndict, IAddWeight, ISubType, IIsCharge, INationOp,
        IPShopItemType, IQuestNo, IIsTest, IQuestNeedCnt, IContentsLv,
        IIsConfirm, IIsSealable, IAddDDWhenCritical, mSealRemovalNeedCnt,
        mIsPracticalPeriod, mIsReceiveTown, IIsReinforceDestroy,
        IAddPotionRestore, IAddMaxHpWhenTransform, IAddMaxMpWhenTransform,
        IAddAttackRateWhenTransform, IAddMoveRateWhenTransform, ISupportType,
        ITermOfValidityLv, mIsUseableUTGWSvr, IAddShortAttackRange,
        IAddLongAttackRange, IWeaponPoisonType, IDPV, IMPV, IRPV, IDDV,
        IMDV, IRDV, IHDPV, IHMPV, IHRPV, IHDDV, IHMDV, IHRDV,
        ISubDDWhenCritical, IGetItemFeedback, IEnemySubCriticalHit,
        IIsPartyDrop, IMaxBeadHoleCount, ISubTypeOption, mIsDeleteArenaSvr
    FROM DT_Item 
    WHERE IID IN ({placeholders})
    """
    
    rows = execute_query(query, ids, fetch_one=False)
    
    # Создаем словарь id -> item для сохранения порядка
    items_dict = {}
    for row in rows:
        items_dict[row.IID] = DT_Item(
            IID=row.IID,
            IName=row.IName,
            IType=row.IType,
            ILevel=row.ILevel,
            IDHIT=row.IDHIT,
            IDDD=row.IDDD,
            IRHIT=row.IRHIT,
            IRDD=row.IRDD,
            IMHIT=row.IMHIT,
            IMDD=row.IMDD,
            IHPPlus=row.IHPPlus,
            IMPPlus=row.IMPPlus,
            ISTR=row.ISTR,
            IDEX=row.IDEX,
            IINT=row.IINT,
            IMaxStack=row.IMaxStack,
            IWeight=float(row.IWeight),
            IUseType=row.IUseType,
            IUseNum=row.IUseNum,
            IRecycle=row.IRecycle,
            IHPRegen=row.IHPRegen,
            IMPRegen=row.IMPRegen,
            IAttackRate=row.IAttackRate,
            IMoveRate=row.IMoveRate,
            ICritical=row.ICritical,
            ITermOfValidity=row.ITermOfValidity,
            ITermOfValidityMi=row.ITermOfValidityMi,
            IDesc=row.IDesc.replace('\\n', ' ⭑ ') if row.IDesc else '',
            IStatus=row.IStatus,
            IFakeID=row.IFakeID,
            IFakeName=row.IFakeName,
            IUseMsg=row.IUseMsg,
            IRange=row.IRange,
            IUseClass=row.IUseClass,
            IDropEffect=row.IDropEffect,
            IUseLevel=row.IUseLevel,
            IUseEternal=bool(row.IUseEternal),
            IUseDelay=row.IUseDelay,
            IUseInAttack=bool(row.IUseInAttack),
            IIsEvent=bool(row.IIsEvent),
            IIsIndict=bool(row.IIsIndict),
            IAddWeight=float(row.IAddWeight),
            ISubType=row.ISubType,
            IIsCharge=bool(row.IIsCharge),
            INationOp=row.INationOp,
            IPShopItemType=row.IPShopItemType,
            IQuestNo=row.IQuestNo,
            IIsTest=bool(row.IIsTest),
            IQuestNeedCnt=row.IQuestNeedCnt,
            IContentsLv=row.IContentsLv,
            IIsConfirm=bool(row.IIsConfirm),
            IIsSealable=bool(row.IIsSealable),
            IAddDDWhenCritical=row.IAddDDWhenCritical,
            mSealRemovalNeedCnt=row.mSealRemovalNeedCnt,
            mIsPracticalPeriod=bool(row.mIsPracticalPeriod),
            mIsReceiveTown=bool(row.mIsReceiveTown),
            IIsReinforceDestroy=bool(row.IIsReinforceDestroy),
            IAddPotionRestore=row.IAddPotionRestore,
            IAddMaxHpWhenTransform=row.IAddMaxHpWhenTransform,
            IAddMaxMpWhenTransform=row.IAddMaxMpWhenTransform,
            IAddAttackRateWhenTransform=row.IAddAttackRateWhenTransform,
            IAddMoveRateWhenTransform=row.IAddMoveRateWhenTransform,
            ISupportType=row.ISupportType,
            ITermOfValidityLv=row.ITermOfValidityLv,
            mIsUseableUTGWSvr=bool(row.mIsUseableUTGWSvr),
            IAddShortAttackRange=row.IAddShortAttackRange,
            IAddLongAttackRange=row.IAddLongAttackRange,
            IWeaponPoisonType=row.IWeaponPoisonType,
            IDPV=row.IDPV,
            IMPV=row.IMPV,
            IRPV=row.IRPV,
            IDDV=row.IDDV,
            IMDV=row.IMDV,
            IRDV=row.IRDV,
            IHDPV=row.IHDPV,
            IHMPV=row.IHMPV,
            IHRPV=row.IHRPV,
            IHDDV=row.IHDDV,
            IHMDV=row.IHMDV,
            IHRDV=row.IHRDV,
            ISubDDWhenCritical=row.ISubDDWhenCritical,
            IGetItemFeedback=row.IGetItemFeedback,
            IEnemySubCriticalHit=row.IEnemySubCriticalHit,
            IIsPartyDrop=bool(row.IIsPartyDrop),
            IMaxBeadHoleCount=row.IMaxBeadHoleCount,
            ISubTypeOption=row.ISubTypeOption,
            mIsDeleteArenaSvr=bool(row.mIsDeleteArenaSvr)
        )
    
    if single_id:
        return items_dict.get(item_ids)
    return [items_dict.get(item_id) for item_id in ids]

# ! Загрузка предметов (ГЛАВНАЯ СТРАНИЦА ПО /items/)
def get_items_by_type(item_types: List[int], search_term: str = '') -> Tuple[List[DT_Item], Dict[int, str]]:
    """Generic function to fetch items by type with optional search"""
    # Используем параметризованный запрос для безопасности
    placeholders = ','.join('?' * len(item_types))
    
    query = f"""
    SELECT IID
    FROM DT_ITem
    WHERE IType IN ({placeholders})
    AND IName LIKE ?
    ORDER BY IID
    """
    
    # Создаем список параметров: сначала item_types, затем search_term
    params = item_types + [f'%{search_term}%']
    
    rows = execute_query(query, params, fetch_one=False)
    item_ids = [row.IID for row in rows]
    
    if not item_ids:
        return [], {}
        
    # Получаем все предметы и ресурсы одним запросом для всех ID
    items = get_item_by_id(item_ids)
    resources = get_item_resource(item_ids)
   
    # Формируем словарь путей к файлам
    file_paths = {}
    for item_id in item_ids:
        if item_id in resources:
            file_paths[item_id] = resources[item_id].file_path
        else:
            file_paths[item_id] = f"{current_app.config['GITHUB_URL']}no_item_image.png"
               
    return items, file_paths




def get_item_details(item_id: int) -> Dict[str, Any]:
    """
    Оптимизированная функция для получения всех данных предмета одним запросом
    """
    base_query = """
    WITH ItemData AS (
        -- Основные данные предмета и ресурса
        SELECT 
            i.*,
            ir.RFileName as resource_file_path,
            ir.RPosX as resource_pos_x,
            ir.RPosY as resource_pos_y,
            irm.RPosX as model_pos_x,
            irm.RPosY as model_pos_y,
            irm.RFileName as model_file_name
        FROM DT_Item i
        LEFT JOIN DT_ItemResource ir ON ir.ROwnerID = i.IID AND ir.RType = 2
        LEFT JOIN DT_ItemResource irm ON irm.ROwnerID = i.IID AND irm.RType = 0
        WHERE i.IID = ?
    ),
    MonsterDropInfo AS (
        -- Информация о дропе с монстров
        SELECT * FROM get_monster_drop_info(?) AS mdi
    ),
    MerchantInfo AS (
        -- Информация о продавцах
        SELECT * FROM get_merchant_sellers(?) AS ms
    ),
    CraftInfo AS (
        -- Информация о крафте
        SELECT 
            base_items.*,
            next_items.*
        FROM check_base_items_for_craft(?) AS base_items
        CROSS JOIN check_next_craft_item(?) AS next_items
    ),
    SkillInfo AS (
        -- Информация о навыках предмета
        SELECT 
            s.*,
            sa.AbnormalID,
            a.AType as abnormal_type,
            a.ADesc as abnormal_desc
        FROM get_item_skill(?) AS s
        LEFT JOIN DT_SkillAbnormal sa ON s.SID = sa.SID
        LEFT JOIN DT_Abnormal a ON sa.AbnormalID = a.AID
    ),
    SpecificProcData AS (
        -- Данные о специфических процессах
        SELECT 
            sp.*,
            pt.mProcDesc,
            pt.mAParamDesc,
            pt.mBParamDesc,
            pt.mCParamDesc,
            pt.mDParamDesc
        FROM TblSpecificProcItem sp
        LEFT JOIN TP_SpecificProcItemType pt ON pt.mProcNo = sp.mProcNo
        WHERE sp.mIID = ?
    ),
    AbnormalResistData AS (
        -- Данные о сопротивлении аномалиям
        SELECT 
            iar.*,
            a.ADesc,
            at.AType,
            at.AName as ATypeName,
            s.SID,
            s.SName,
            sp.mSPID,
            sp.mName as SPName,
            sp.mDesc as SPDesc,
            sp.mSpriteFile,
            sp.mSpriteX,
            sp.mSpriteY
        FROM DT_ItemAbnormalResist iar
        LEFT JOIN DT_Abnormal a ON a.AID = iar.AID
        LEFT JOIN TP_AbnormalType at ON at.AType = a.AType
        LEFT JOIN DT_SkillAbnormal sa ON a.AID = sa.AbnormalID
        LEFT JOIN DT_Skill s ON sa.SID = s.SID
        LEFT JOIN DT_SkillPackSkill sps ON s.SID = sps.mSID
        LEFT JOIN DT_SkillPack sp ON sps.mSPID = sp.mSPID
        WHERE iar.IID = ?
    ),
    BeadData AS (
        -- Полные данные о бусинах/рунах включая активацию
        SELECT 
            ibe.*,
            be.mName as BeadName,
            be.mBeadType,
            bt.mDesc as BeadTypeDesc,
            b.mTargetIPos,
            b.mProb,
            bhp.mMaxHoleCount,
            bhp.mHoleCount,
            bhp.mProb as HoleProb,
            ibm.MID,
            -- Данные активации
            spid.mParamA as activation_param,
            s.SName as activation_skill_name,
            s.mSpriteFile as activation_sprite_file,
            s.mSpriteX as activation_sprite_x,
            s.mSpriteY as activation_sprite_y
        FROM DT_ItemBeadEffect ibe
        LEFT JOIN DT_BeadEffect be ON ibe.mBeadNo = be.mBeadNo
        LEFT JOIN TP_BeadType bt ON bt.mBeadType = be.mBeadType
        LEFT JOIN DT_Bead b ON ibe.IID = b.IID
        LEFT JOIN TblBeadHoleProb bhp ON ibe.IID = bhp.IID
        LEFT JOIN DT_ItemBeadModule ibm ON ibe.IID = ibm.IID
        LEFT JOIN get_sid_by_spid(be.mParamA) spid ON be.mBeadType = 2
        LEFT JOIN DT_Skill s ON spid.SID = s.SID
        WHERE ibe.IID = ?
    ),
    AttributeData AS (
        -- Данные об атрибутах (add и resist)
        SELECT 
            iaa.IID,
            aa.AID as add_aid,
            aa.AType as add_type,
            aa.ALevel as add_level,
            aa.ADiceDamage as add_dice_damage,
            aa.ADamage as add_damage,
            iar.AID as resist_aid,
            ar.AType as resist_type,
            ar.ALevel as resist_level,
            ar.ADiceDamage as resist_dice_damage,
            ar.ADamage as resist_damage
        FROM DT_ItemAttributeAdd iaa
        FULL OUTER JOIN DT_AttributeAdd aa ON iaa.AID = aa.AID
        FULL OUTER JOIN DT_ItemAttributeResist iar ON iaa.IID = iar.IID
        FULL OUTER JOIN DT_AttributeResist ar ON iar.AID = ar.AID
        WHERE iaa.IID = ? OR iar.IID = ?
    ),
    ProtectSlainData AS (
        -- Данные о защите и убийствах
        SELECT 
            ip.IID,
            p.SID as protect_sid,
            p.SLevel as protect_level,
            p.SDPV, p.SMPV, p.SRPV,
            p.SDDV, p.SMDV, p.SRDV,
            isl.SID as slain_sid,
            s.SType as slain_type,
            s.SLevel as slain_level,
            s.SHitPlus, s.SDDPlus,
            s.SRHitPlus, s.SRDDPlus
        FROM DT_ItemProtect ip
        FULL OUTER JOIN DT_Protect p ON ip.PID = p.SID
        FULL OUTER JOIN DT_ItemSlain isl ON ip.IID = isl.IID
        FULL OUTER JOIN DT_Slain s ON isl.SID = s.SID
        WHERE ip.IID = ? OR isl.IID = ?
    )
    -- Основной SELECT
    SELECT 
        i.*,
        md.*,
        mi.*,
        ci.*,
        si.*,
        sp.*,
        ar.*,
        bd.*,
        ad.*,
        ps.*
    FROM ItemData i
    LEFT JOIN MonsterDropInfo md ON 1=1
    LEFT JOIN MerchantInfo mi ON 1=1
    LEFT JOIN CraftInfo ci ON 1=1
    LEFT JOIN SkillInfo si ON 1=1
    LEFT JOIN SpecificProcData sp ON 1=1
    LEFT JOIN AbnormalResistData ar ON 1=1
    LEFT JOIN BeadData bd ON 1=1
    LEFT JOIN AttributeData ad ON 1=1
    LEFT JOIN ProtectSlainData ps ON 1=1
    """
    
    # Выполняем запрос с множественным использованием item_id
    result = execute_query(
        base_query,
        (item_id,) * 12,  # Передаем item_id для каждого подзапроса
        fetch_one=True
    )
    
    if not result:
        return "Item not found", 404

    # Обработка класса использования
    use_class = int(result.IUseClass.split('/')[-1].replace('.png', ''))
    
    # Получение информации о модели
    base = f"{int(result.model_pos_x):03}{int(result.model_pos_y):03}"
    prefix, item_model_no = get_item_model_info(use_class, result.IType, base)

    # Обработка данных навыков
    skill_data = parse_skill_data(result)
    abnormal_data = parse_abnormal_data(result)
    
    # Рендеринг шаблона с данными
    return
        item=result,
        file_path=result.resource_file_path,
        mondropinfo=result.monster_drop_info,
        merchant_sellers=result.merchant_info,
        monstermodelno_result=item_model_no,
        prefix=prefix,
        use_class=use_class,
        craft_result=result.craft_base_items,
        craft_next=result.craft_next_items,
        itemdskill_data=skill_data.get('skill_data'),
        itemskill_pic=skill_data.get('skill_pic'),
        linked_skills=skill_data.get('linked_skills'),
        linked_skillsaid=skill_data.get('linked_skillsaid'),
        abnormal_type_data=abnormal_data.get('type_data'),
        abnormal_type_pic=abnormal_data.get('type_pic'),
        specificproc_data=parse_specific_proc_data(result),
        transform_list=skill_data.get('transform_list'),
        monster_pic_url=skill_data.get('monster_pic_url'),
        item_abnormalResist_data=parse_abnormal_resist_data(result),
        rune_bead_data=parse_bead_data(result),
        activation_bead_data=parse_activation_bead_data(result),
        activation_bead_pic=get_activation_bead_pic(result),
        item_bead_module_data=parse_bead_module_data(result),
        item_bead_holeprob_data=parse_bead_hole_data(result),
        item_attribute_add_data=parse_attribute_add_data(result),
        item_attribute_resist_data=parse_attribute_resist_data(result),
        item_protect_data=parse_protect_data(result),
        item_slain_data=parse_slain_data(result),
        item_panalty_data=parse_penalty_data(result)



def parse_skill_data(row):
    """Обработка данных навыков"""
    if not hasattr(row, 'SID'):
        return {}
    
    return {
        'skill_data': {
            'id': row.SID,
            'name': row.SName,
            'sprite_file': row.mSpriteFile,
            'sprite_x': row.mSpriteX,
            'sprite_y': row.mSpriteY,
            'description': row.mDesc if hasattr(row, 'mDesc') else None
        },
        'skill_pic': get_skill_icon_path(row.mSpriteFile, row.mSpriteX, row.mSpriteY),
        'linked_skills': getattr(row, 'linked_skills', None),
        'linked_skillsaid': getattr(row, 'AbnormalID', None),
        'transform_list': getattr(row, 'transform_list', None),
        'monster_pic_url': getattr(row, 'monster_pic_url', None)
    }

def parse_abnormal_data(row):
    """Обработка данных аномалий"""
    if not hasattr(row, 'AType'):
        return {}
    
    return {
        'type_data': {
            'type': row.AType,
            'desc': clean_description(row.ADesc) if hasattr(row, 'ADesc') else None,
            'name': row.ATypeName if hasattr(row, 'ATypeName') else None
        },
        'type_pic': get_abnormal_icon_path(row)
    }

def parse_specific_proc_data(row):
    """Обработка данных специфических процессов"""
    if not hasattr(row, 'mProcNo'):
        return None
    
    return {
        'mIID': row.mIID,
        'mProcNo': row.mProcNo,
        'mProcDesc': clean_description(row.mProcDesc) if hasattr(row, 'mProcDesc') else None,
        'params': {
            'a': {
                'value': getattr(row, 'mAParam', None),
                'desc': clean_description(row.mAParamDesc) if hasattr(row, 'mAParamDesc') else None
            },
            'b': {
                'value': getattr(row, 'mBParam', None),
                'desc': clean_description(row.mBParamDesc) if hasattr(row, 'mBParamDesc') else None
            },
            'c': {
                'value': getattr(row, 'mCParam', None),
                'desc': clean_description(row.mCParamDesc) if hasattr(row, 'mCParamDesc') else None
            },
            'd': {
                'value': getattr(row, 'mDParam', None),
                'desc': clean_description(row.mDParamDesc) if hasattr(row, 'mDParamDesc') else None
            }
        }
    }

def parse_abnormal_resist_data(row):
    """Обработка данных сопротивления аномалиям"""
    if not hasattr(row, 'AID') or not row.AID:
        return None
    
    return {
        'AID': row.AID,
        'ADesc': clean_description(row.ADesc) if hasattr(row, 'ADesc') else None,
        'AType': row.AType if hasattr(row, 'AType') else None,
        'ATypeName': row.ATypeName if hasattr(row, 'ATypeName') else None,
        'skill': {
            'SID': getattr(row, 'SID', None),
            'SName': getattr(row, 'SName', None),
            'mSPID': getattr(row, 'mSPID', None),
            'SPName': getattr(row, 'SPName', None),
            'SPDesc': clean_description(row.SPDesc) if hasattr(row, 'SPDesc') else None,
        },
        'sprite': {
            'file': getattr(row, 'mSpriteFile', None),
            'x': getattr(row, 'mSpriteX', None),
            'y': getattr(row, 'mSpriteY', None)
        }
    }

def parse_bead_data(row):
    """Обработка данных бусин/рун"""
    if not hasattr(row, 'mBeadType') or not row.mBeadType:
        return None
    
    return {
        'bead': {
            'mBeadNo': row.mBeadNo if hasattr(row, 'mBeadNo') else None,
            'name': row.BeadName if hasattr(row, 'BeadName') else None,
            'type': row.mBeadType,
            'type_desc': row.BeadTypeDesc if hasattr(row, 'BeadTypeDesc') else None,
            'target_pos': row.mTargetIPos if hasattr(row, 'mTargetIPos') else None,
            'prob': float(row.mProb) if hasattr(row, 'mProb') else None,
            'group': row.mGroup if hasattr(row, 'mGroup') else None
        }
    }

def parse_activation_bead_data(row):
    """Обработка данных активации бусин"""
    if not hasattr(row, 'activation_param'):
        return None
    
    return {
        'param': row.activation_param,
        'skill_name': row.activation_skill_name if hasattr(row, 'activation_skill_name') else None
    }

def get_activation_bead_pic(row):
    """Получение изображения для активации бусины"""
    if not (hasattr(row, 'activation_sprite_file') and 
            hasattr(row, 'activation_sprite_x') and 
            hasattr(row, 'activation_sprite_y')):
        return None
    
    return get_skill_icon_path(
        row.activation_sprite_file,
        row.activation_sprite_x,
        row.activation_sprite_y
    )

def parse_bead_module_data(row):
    """Обработка данных модулей бусин"""
    if not hasattr(row, 'MID') or not row.MID:
        return None
    
    return {
        'id': row.MID,
        'type': row.MType if hasattr(row, 'MType') else None,
        'name': row.MName if hasattr(row, 'MName') else None,
        'desc': clean_description(row.MDesc) if hasattr(row, 'MDesc') else None,
        'level': row.MLevel if hasattr(row, 'MLevel') else None,
        'params': {
            'a': {
                'value': getattr(row, 'MAParam', None),
                'name': getattr(row, 'MAParamName', None)
            },
            'b': {
                'value': getattr(row, 'MBParam', None),
                'name': getattr(row, 'MBParamName', None)
            },
            'c': {
                'value': getattr(row, 'MCParam', None),
                'name': getattr(row, 'MCParamName', None)
            }
        }
    }

def parse_bead_hole_data(row):
    """Обработка данных отверстий для бусин"""
    if not hasattr(row, 'mMaxHoleCount'):
        return None
    
    return {
        'max_count': row.mMaxHoleCount,
        'count': row.mHoleCount if hasattr(row, 'mHoleCount') else None,
        'prob': float(row.HoleProb) if hasattr(row, 'HoleProb') else None
    }

def parse_attribute_add_data(row):
    """Обработка данных добавления атрибутов"""
    if not hasattr(row, 'add_aid') or not row.add_aid:
        return None
    
    return {
        'aid': row.add_aid,
        'type': row.add_type,
        'level': row.add_level,
        'dice_damage': row.add_dice_damage,
        'damage': row.add_damage
    }

def parse_attribute_resist_data(row):
    """Обработка данных сопротивления атрибутам"""
    if not hasattr(row, 'resist_aid') or not row.resist_aid:
        return None
    
    return {
        'aid': row.resist_aid,
        'type': row.resist_type,
        'level': row.resist_level,
        'dice_damage': row.resist_dice_damage,
        'damage': row.resist_damage
    }

def parse_protect_data(row):
    """Обработка данных защиты"""
    if not hasattr(row, 'protect_sid') or not row.protect_sid:
        return None
    
    return {
        'sid': row.protect_sid,
        'level': row.protect_level,
        'stats': {
            'dpv': row.SDPV,
            'mpv': row.SMPV,
            'rpv': row.SRPV,
            'ddv': row.SDDV,
            'mdv': row.SMDV,
            'rdv': row.SRDV
        }
    }

def parse_slain_data(row):
    """Обработка данных убийства"""
    if not hasattr(row, 'slain_sid') or not row.slain_sid:
        return None
    
    return {
        'sid': row.slain_sid,
        'type': row.slain_type,
        'level': row.slain_level,
        'stats': {
            'hit_plus': row.SHitPlus,
            'dd_plus': row.SDDPlus,
            'r_hit_plus': row.SRHitPlus,
            'r_dd_plus': row.SRDDPlus
        }
    }

def parse_penalty_data(row):
    """Обработка данных штрафов"""
    if not hasattr(row, 'IDHIT_penalty'):
        return None
        
    return {
        'stats': {
            'dhit': row.IDHIT_penalty,
            'ddd': row.IDDD_penalty,
            'rhit': row.IRHIT_penalty,
            'rdd': row.IRDD_penalty,
            'mhit': row.IMHIT_penalty,
            'mdd': row.IMDD_penalty,
            'hp_plus': row.IHPPlus_penalty,
            'mp_plus': row.IMPPlus_penalty,
            'str': row.ISTR_penalty,
            'dex': row.IDEX_penalty,
            'int': row.IINT_penalty
        },
        'regen': {
            'hp': row.IHPRegen_penalty,
            'mp': row.IMPRegen_penalty
        },
        'rates': {
            'attack': row.IAttackRate_penalty,
            'move': row.IMoveRate_penalty,
            'critical': row.ICritical_penalty
        }
    }

def get_item_model_info(use_class: int, item_type: int, base: str) -> tuple:
    """Получает информацию о модели предмета"""
    prefix = 'i'
    item_model_no = base

    if item_type == 3:  # Доспехи
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
    elif item_type not in [1, 18, 20, 2, 19]:
        prefix = 'i'

    return prefix, item_model_no
    """Генерация пути к иконке аномалии"""
    if not all([sprite_file, sprite_x is not None, sprite_y is not None]):
        return None

    return f"{current_app.config['GITHUB_URL']}abnormal/{sprite_file}_{sprite_x}_{sprite_y}.png"
    """Получает информацию о модели предмета"""
    prefix = 'i'
    item_model_no = base

    if item_type == 3:  # Доспехи
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
    elif item_type not in [1, 18, 20, 2, 19]:
        prefix = 'i'

    return prefix, item_model_no