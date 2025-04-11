from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from lnbits.db import FilterModel


class UnitType(str, Enum):
    request = "request"
    token = "token"
    minute = "minute"


### Core Models
class CreateAgent(BaseModel):
    wallet_id: str
    name: str
    description: Optional[str] = None
    api_url: str
    api_key: Optional[str] = None
    model_name: str
    specialization: Optional[str] = None
    price_per_unit: int = Field(ge=1)
    unit_type: UnitType = Field(
        default=UnitType.request,
        description="Unit type for pricing. Can be 'request', 'token', or 'minute'.",
    )


class Agent(CreateAgent):
    id: str
    available: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PublicAgent(BaseModel):
    id: str
    wallet_id: str
    name: str
    description: Optional[str] = None
    model_name: str
    specialization: Optional[str] = None
    price_per_unit: int
    unit_type: UnitType
    available: bool = True


class AccessKeyRequest(BaseModel):
    units: int = Field(ge=1)
    payment_hash: Optional[str] = None


class AccessKeyResponse(BaseModel):
    id: str
    payment_hash: str
    payment_request: str


class AccessTokenPayload(BaseModel):
    agent_id: str
    access_key_id: str


class PublicAccessKey(BaseModel):
    id: str
    agent_id: str
    api_key: str
    prepaid_units: int = Field(ge=1)
    used_units: int = 0
    active: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def has_uses_left(self) -> bool:
        return self.prepaid_units > self.used_units


class AgentAccessKey(PublicAccessKey):
    payment_hash: str


class Role(str, Enum):
    developer = "developer"
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"
    function = "function"

    @validator("role")
    def validate_role(cls, value):
        if value not in Role.__members__:
            raise ValueError(
                f"Invalid role: {value}. Must be one of {list(Role.__members__.keys())}."
            )
        return value


class ChatMessage(BaseModel):
    role: Role
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class AgentCompletionRequest(BaseModel):
    messages: List[dict]


class CreateAgentUsageLog(BaseModel):
    access_key_id: str
    agent_id: str
    units_used: int
    input_hash: Optional[str] = None


class AgentUsageLog(CreateAgentUsageLog):
    id: str
    request_snapshot: Optional[str] = None
    response_snapshot: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


### Filters for Admin Panel


class AgentFilters(FilterModel):
    __search_fields__ = ["name", "model_name", "specialization"]
    __sort_fields__ = ["name", "price_per_unit", "created_at"]

    name: Optional[str]
    model_name: Optional[str]
    specialization: Optional[str]
    available: Optional[bool]


class AgentUsageLogFilters(FilterModel):
    __search_fields__ = ["user_id", "agent_id"]
    __sort_fields__ = ["timestamp", "units_used", "sats_charged"]

    wallet_id: Optional[str]
    agent_id: Optional[str]
    timestamp: Optional[datetime]
    sats_charged: Optional[int]
