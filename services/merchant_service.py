from typing import List, Dict, Tuple
from flask import current_app
from services.database import execute_query
from services.item_service import get_item_resource
from services.utils import get_payment_type_name

def get_merchant_sell_list() -> Tuple[List[Tuple], Dict]:
    """Get complete merchant sell list"""
    query = f"""
        SELECT
          a.ListID,
          c.MID,
          c.MName,
          c.MClass,
          a.ItemID,
          d.IName,
          a.Price,
          b.mPaymentType 
        FROM
          {current_app.config['DATABASE_NAME']}.[dbo].[TblMerchantSellList] AS a
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[TblMerchantName] AS b ON ( a.ListID = b.mID )
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[DT_Monster] AS c ON ( b.mID = c.mSellMerchanID )
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[DT_Item] AS d ON ( a.ItemID = d.IID ) 
        ORDER BY
          c.MName DESC 
    """
    
    rows = execute_query(query)
    merchants_data = [
        (row.ListID, row.MID, 
         (row.MName.replace('/n', ' ') if row.MName else ''),
         row.MClass, row.ItemID, row.IName, 
         row.Price, row.mPaymentType)
        for row in rows
    ]

    file_paths = {
        monster[0]: f"{current_app.config['GITHUB_URL']}{monster[1]}.png"
        for monster in merchants_data
    }

    return merchants_data, file_paths

def get_merchant_sellers(item_id: int) -> List[Dict]:
    """Get merchants selling a specific item"""
    query = f"""
        SELECT
          a.ListID,
          c.MID,
          c.MName,
          a.Price,
          b.mPaymentType 
        FROM
          {current_app.config['DATABASE_NAME']}.[dbo].[TblMerchantSellList] AS a
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[TblMerchantName] AS b ON ( a.ListID = b.mID )
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[DT_Monster] AS c ON ( b.mID = c.mSellMerchanID )
        WHERE a.ItemID = ?
        ORDER BY c.MName
    """
    
    rows = execute_query(query, (item_id,))
    merchants = []

    for row in rows:
        if row.MID:  # Check that merchant exists
            merchants.append({
                "MerchantID": row.MID,
                "MerchantName": row.MName.replace('/n', ' ') if row.MName else '',
                "Price": row.Price,
                "PaymentType": get_payment_type_name(row.mPaymentType)
            })
    
    return merchants

def get_merchant_items(merchant_id: int) -> List[Dict]:
    """Get all items sold by a specific merchant"""
    query = f"""
        SELECT
          a.ListID,
          a.ItemID,
          d.IName,
          a.Price,
          b.mPaymentType 
        FROM
          {current_app.config['DATABASE_NAME']}.[dbo].[TblMerchantSellList] AS a
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[TblMerchantName] AS b ON ( a.ListID = b.mID )
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[DT_Monster] AS c ON ( b.mID = c.mSellMerchanID )
          LEFT JOIN {current_app.config['DATABASE_NAME']}.[dbo].[DT_Item] AS d ON ( a.ItemID = d.IID )
        WHERE c.MID = ?
    """
    
    rows = execute_query(query, (merchant_id,))
    merchant_items = []

    for row in rows:
        merch_pic = None
        merch_item_pics = get_item_resource(row.ItemID)

        if merch_item_pics:
            if merch_item_pics.RFileName and merch_item_pics.RPosX is not None and merch_item_pics.RPosY is not None:
                merch_pic = f"{current_app.config['GITHUB_URL']}{merch_item_pics.RFileName.split('.')[0]}_{merch_item_pics.RPosX}_{merch_item_pics.RPosY}.png"

        merchant_items.append({
            "MerchantListID": row.ListID,
            "MerchantItemID": row.ItemID,
            "MerchantItemName": row.IName,
            "MerchantItemPrice": row.Price,
            "MerchantPaymentType": get_payment_type_name(row.mPaymentType),
            "MerchantItemPicture": merch_pic,
        })

    return merchant_items