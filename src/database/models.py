from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class AllProfiles(Base):
    __tablename__ = 'all_profiles'
    
    linkedin_id           = Column(String, primary_key=True)
    name                  = Column(String)
    position              = Column(String)
    city_state_country    = Column(String)
    country_code          = Column(String)
    number_of_connections = Column(Integer)
    profile_url           = Column(String)
    discovery_input       = Column(String)

class ProfilesSent(Base):
    __tablename__ = 'profiles_sent'
    
    linkedin_id = Column(String, ForeignKey('all_profiles.linkedin_id'), primary_key=True)
    sent        = Column(String)

class NLPAttributes(Base):
    __tablename__ = 'nlp_attributes'
    
    linkedin_id               = Column(String, ForeignKey('all_profiles.linkedin_id'), primary_key=True)
    golfer                    = Column(Boolean)
    golfer_reasoning          = Column(String)
    wealth_rating             = Column(Integer)
    wealth_reasoning          = Column(String)
    lawyer                    = Column(Boolean)
    active_ceo                = Column(Boolean)
    nationality               = Column(String)
    sex                       = Column(String)
    lives_in_preferred_states = Column(Boolean)
    retired                   = Column(Boolean)
    age_estimate              = Column(Integer)

class QualifiedProfiles(Base):
    __tablename__ = 'qualified_profiles'
    
    linkedin_id          = Column(String, ForeignKey('all_profiles.linkedin_id'), primary_key=True)
    qualified_basic_info = Column(Boolean)
    qualified_nlp_review = Column(Boolean)

if __name__ == "__main__": 
    engine = create_engine('sqlite:///data/db/profiles.db')  # Replace with your actual database URL\
    Base.metadata.create_all(engine)