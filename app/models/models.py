from pydantic import BaseModel

class XrpNetwork():
    def __init__(self,     
        json_rpc: str,
        websocket: str,
        type: str,
        domain: str):
        self.json_rpc = json_rpc
        self.websocket = websocket
        self.type = type
        self.domain = domain

    def __init__(self, data):
        self.from_dict(data)
    

    def from_dict(self, data):
        for field in ['json_rpc', 'websocket', 'type', 'domain']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        return {
            "json_rpc": self.json_rpc,
            "websocket": self.websocket,
            "type": self.type,
            "domain": self.domain
        }

class URIStageStructure(BaseModel):
    date: int
    state: int
    max: int
    id: str

    class Config:
        extra = 'forbid'
    