from pydantic import BaseModel


class GoogleAd(BaseModel):
    campaign_id: str
    campaign: str
    ad_group_id: str
    ad_group: str
    ad_id: str
    clicks: str
    impressions: str
    engagements: str

    class Config:
        orm_mode = True