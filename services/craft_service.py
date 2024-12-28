from typing import List, Dict, Optional
from flask import current_app
from services.database import execute_query
from services.item_service import get_item_resource

def check_base_items_for_craft(item_id: int) -> List[Dict]:
    """Get crafting recipe for an item"""
    query = """
    SELECT DISTINCT
        a.RID,
        a.RItemID0,
        b.IName,
        c.RItemID,
        b1.IName AS 'CraftItems',
        a.RSuccess,
        a.RIsCreateCnt,
        c.ROrderNo
    FROM
        DT_Refine AS a
        INNER JOIN DT_Item AS b ON (a.RItemID0 = b.IID)
        INNER JOIN DT_RefineMaterial AS c ON (a.RID = c.RID)
        INNER JOIN DT_Item AS b1 ON (c.RItemID = b1.IID) 
    WHERE
        a.RItemID0 = ? 
    ORDER BY
        a.RID, c.ROrderNo
    """

    rows = execute_query(query, (item_id,))
    unique_results = {}

    for row in rows:
        # Use RItemID as key for uniqueness
        key = row.RItemID

        # Update record only if it doesn't exist
        if key not in unique_results:
            item_resource = get_item_resource(row.RItemID)
            
            if item_resource:
                file_name = item_resource.RFileName.split('.')[0]
                image_path = f"{current_app.config['GITHUB_URL']}{file_name}_{item_resource.RPosX}_{item_resource.RPosY}.png"
            else:
                image_path = f"{current_app.config['GITHUB_URL']}no_item_image.png"

            unique_results[key] = {
                'RID': row.RID,
                'RItemID0': row.RItemID0,
                'IName': row.IName,
                'RItemID': row.RItemID,
                'CraftItems': row.CraftItems,
                'RSuccess': round(float(row.RSuccess), 1),
                'RIsCreateCnt': row.RIsCreateCnt,
                'ROrderNo': row.ROrderNo,
                'ImagePath': image_path
            }

    return list(unique_results.values())

def check_next_craft_item(item_id: int) -> List[Dict]:
    """Get items that can be crafted using this item"""
    query = """
    SELECT DISTINCT
        a.RID,
        a.RItemID0,
        b.IName,
        a.RSuccess,
        a.RIsCreateCnt
    FROM
        DT_Refine AS a
        INNER JOIN DT_Item AS b ON (a.RItemID0 = b.IID)
        INNER JOIN DT_RefineMaterial AS c ON (a.RID = c.RID)
        INNER JOIN DT_Item AS b1 ON (c.RItemID = b1.IID)
    WHERE
        c.RItemID = ?
    ORDER BY
        a.RID
    """

    rows = execute_query(query, (item_id,))
    unique_results = {}

    for row in rows:
        # Use RItemID0 as key for uniqueness
        key = row.RItemID0

        # Update record only if it doesn't exist
        if key not in unique_results:
            item_resource = get_item_resource(row.RItemID0)

            if item_resource:
                file_name = item_resource.RFileName.split('.')[0]
                image_path = f"{current_app.config['GITHUB_URL']}{file_name}_{item_resource.RPosX}_{item_resource.RPosY}.png"
            else:
                image_path = f"{current_app.config['GITHUB_URL']}no_item_image.png"

            unique_results[key] = {
                'RID': row.RID,
                'RItemID0': row.RItemID0,
                'IName': row.IName,
                'RSuccess': round(float(row.RSuccess), 1),
                'RIsCreateCnt': row.RIsCreateCnt,
                'ImagePath': image_path
            }

    return list(unique_results.values())