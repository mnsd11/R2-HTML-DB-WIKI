from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class Abnormal:
    """Data class for abnormal effects"""
    abnormal_data: Dict
    module_data: Dict
    skill_data: Dict
    abnormal_type_data: Optional[tuple]
    abnormal_type_pic: Optional[str]

@dataclass
class AbnormalItem:
    """Data class for items related to abnormal effects"""
    id: int
    name: str
    icon: Optional[str]

@dataclass
class AbnormalSkill:
    """Data class for skills related to abnormal effects"""
    id: int
    name: str
    desc: str
    icon: Optional[str]

@dataclass
class AbnormalListItem:
    """Data class for abnormal list display"""
    AID: int
    AName: str
    ADesc: str
    AType: int
    ALevel: int
    AEffect: int
    AFileName: str
    AIconX: int
    AIconY: int
    icon_path: str