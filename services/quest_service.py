from typing import List, Dict, Optional
from flask import current_app
from services.database import execute_query
from services.monster_service import get_monster_name, get_monster_pic_url
from services.item_service import get_item_pic_url, get_item_resource, get_item_pic_url

def get_quests_data() -> List[Dict]:
    """Получение данных о квестах"""
    try:
        query = """
        SELECT
            a.mQuestNo,
            a.mQuestNm,
            a.mClass,
            b.mDesc AS class_desc,
            a.mLevel1,
            a.mLevel2,
            a.mPreQuestNo,
            a.mIsOverlap,
            a.mQuestDesc,
            e.mDesc AS quest_info_desc,
            a.mAbandonment,
            a.mDifficulty,
            a.mRewardNo,
            c.mExp,
            c.mID AS reward_item_id,
            c1.IName AS reward_name,
            c.mCnt AS reward_count,
            c.mBinding,
            c.mStatus,
            c.mEffTime,
            c.mValTime,
            w.mID AS required_item_id,
            c2.IName AS required_item_name,
            w.mCnt AS required_count,
            a.mPlace,
            r.mPlaceNm AS place_name,
            a.mPosX,
            a.mPosY,
            a.mPosZ,
            d.mMonsterID AS ref_monster_id,
            a.mFindNPC,
            q1.MName AS find_npc_name,
            a.mCompletionNPC,
            q.MName AS completion_npc_name 
        FROM TblQuest AS a
        LEFT OUTER JOIN FNLParm1602.dbo.TP_PlayerClass AS b ON (b.mClassNo = a.mClass)
        LEFT OUTER JOIN TblQuestReward AS c ON (c.mRewardNo = a.mRewardNo)
        LEFT OUTER JOIN DT_Item AS c1 ON (c1.IID = c.mID)
        LEFT OUTER JOIN TblQuestRefMonster AS d ON (d.mQuestNo = a.mQuestNo)
        LEFT OUTER JOIN DT_Monster AS q ON (q.MID = a.mCompletionNPC)
        LEFT OUTER JOIN DT_Monster AS q1 ON (q1.MID = d.mMonsterID)
        LEFT OUTER JOIN TblQuestCondition AS w ON (w.mQuestNo = a.mQuestNo)
        LEFT OUTER JOIN DT_Item AS c2 ON (c2.IID = w.mID)
        LEFT OUTER JOIN TblQuestInfo AS e ON (e.mQuestNo = a.mQuestNo)
        LEFT OUTER JOIN TblPlace AS r ON (r.mPlaceNo = a.mPlace)
        
        ORDER BY a.mQuestNo
        """
        
        results = execute_query(query)
        quests = []
        
        for row in results:
            row_dict = {
                'mQuestNo': row[0],
                'mQuestNm': row[1],
                'mClass': row[2],
                'class_desc': row[3],
                'mLevel1': row[4],
                'mLevel2': row[5],
                'mPreQuestNo': row[6],
                'mIsOverlap': row[7],
                'mQuestDesc': row[8],
                'quest_info_desc': row[9],
                'mAbandonment': row[10],
                'mDifficulty': row[11],
                'mRewardNo': row[12],
                'mExp': row[13],
                'reward_item_id': row[14],
                'reward_name': row[15],
                'reward_count': row[16],
                'mBinding': row[17],
                'mStatus': row[18],
                'mEffTime': row[19],
                'mValTime': row[20],
                'required_item_id': row[21],
                'required_item_name': row[22],
                'required_count': row[23],
                'mPlace': row[24],
                'place_name': row[25],
                'mPosX': row[26],
                'mPosY': row[27],
                'mPosZ': row[28],
                'ref_monster_id': row[29],
                'mFindNPC': row[30],
                'find_npc_name': row[31],
                'mCompletionNPC': row[32],
                'completion_npc_name': row[33]
            }

            # Подготовка наград
            rewards_items = []
            if row_dict['reward_item_id']:
                try:
                    rewards_items.append({
                        'id': row_dict['reward_item_id'],
                        'name': row_dict['reward_name'] or 'Неизвестный предмет',
                        'count': row_dict['reward_count'] or 1,
                        'pic': get_item_pic_url(row_dict['reward_item_id'])
                    })
                except Exception as e:
                    print(f"Error processing reward item {row_dict['reward_item_id']}: {e}")

            # Подготовка требований
            requirement_items = []
            if row_dict['required_item_id']:
                try:
                    requirement_items.append({
                        'id': row_dict['required_item_id'],
                        'name': row_dict['required_item_name'] or 'Неизвестный предмет',
                        'count': row_dict['required_count'] or 1,
                        'pic': get_item_pic_url(row_dict['required_item_id'])
                    })
                except Exception as e:
                    print(f"Error processing required item {row_dict['required_item_id']}: {e}")


            # Подготовка NPC
            completion_npc = None
            if row_dict['mCompletionNPC']:
                try:
                    completion_npc = {
                        'id': row_dict['mCompletionNPC'],
                        'name': row_dict['completion_npc_name'],
                        'pic': get_monster_pic_url(row_dict['mCompletionNPC']) if row_dict['mCompletionNPC'] else None
                    }
                except Exception as e:
                    print(f"Error processing completion NPC {row_dict['mCompletionNPC']}: {e}")

            find_npc = None
            if row_dict['mFindNPC']:
                try:
                    find_npc = {
                        'id': row_dict['mFindNPC'],
                        'name': row_dict['find_npc_name'],
                        'pic': get_monster_pic_url(row_dict['mFindNPC']) if row_dict['mFindNPC'] else None
                    }
                except Exception as e:
                    print(f"Error processing find NPC {row_dict['mFindNPC']}: {e}")

            quest = {
                'questNo': row_dict['mQuestNo'],
                'questName': row_dict['mQuestNm'],
                'level': f"{row_dict['mLevel1']}-{row_dict['mLevel2']}",
                'class': row_dict['class_desc'],
                'difficulty': row_dict['mDifficulty'],
                'description': row_dict['mQuestDesc'],
                'place': row_dict['place_name'],
                'rewards': {
                    'exp': row_dict['mExp'],
                    'itemList': rewards_items  # Изменено название с items на itemList
                },
                'requirements': {
                    'itemList': requirement_items  # Изменено название с items на itemList
                },
                'npcs': {
                    'completion': completion_npc,
                    'find': find_npc
                }
            }
            quests.append(quest)
            
        return quests
        
    except Exception as e:
        print(f"Error getting quests data: {e}")
        return []