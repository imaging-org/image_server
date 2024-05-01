import uuid
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
from dataclasses import fields
from typing import Optional


class EventTypeEnum(Enum):
    SAVE = "Save"
    DELETE = "Delete"
    SIMILAR = "Similar"
    RESET = "Reset"


@dataclass
class MQMessage:
    EventType: EventTypeEnum
    timestamp: datetime
    ImageURL: Optional[str] = None
    image_id: Optional[str] = None
    batch_id: Optional[str] = None
    user_id: Optional[str] = None

    @classmethod
    def from_json(cls, json_data):
        keys = [f.name for f in fields(cls)]
        normal_json_data = {key: json_data[key] for key in json_data if key in keys and key != "EventType"}
        normal_json_data["EventType"] = EventTypeEnum[json_data["EventType"].upper()]
        tmp = cls(**normal_json_data)
        return tmp

