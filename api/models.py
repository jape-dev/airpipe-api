from api.database import Base
from sqlalchemy import String, Column, Integer, BigInteger


class GoogleAd(Base):
    __tablename__ = 'google_ads'

    id = Column(Integer(), primary_key=True)
    campaign_id = Column(BigInteger())
    campaign = Column(String())
    ad_group_id = Column(String())
    ad_group = Column(String())
    ad_id = Column(String())
    clicks = Column(Integer())
    impressions = Column(Integer())
    engagements = Column(Integer())
