from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SpriteProperties:
    rows: int
    cols: int
    width: int
    height: int
    path: Optional[str] = None
    frame_rate: Optional[int] = None
    loop: Optional[bool] = None
    hitbox: Optional[List[int]] = None
    hurtbox: Optional[List[int]] = None