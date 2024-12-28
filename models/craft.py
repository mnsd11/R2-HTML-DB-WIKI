from dataclasses import dataclass
from typing import Optional

@dataclass
class CraftRecipe:
    """Data class for craft recipes"""
    RID: int
    RItemID0: int
    IName: str
    RItemID: int
    CraftItems: str
    RSuccess: float
    RIsCreateCnt: int
    ROrderNo: int
    ImagePath: str

@dataclass
class CraftResult:
    """Data class for items that can be crafted"""
    RID: int
    RItemID0: int
    IName: str
    RSuccess: float
    RIsCreateCnt: int
    ImagePath: str