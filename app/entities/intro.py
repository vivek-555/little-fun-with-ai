from pydantic import BaseModel

class Intro(BaseModel):
    app_name_domain: str
    basic_info: str 
    feature: str
    capability: str
