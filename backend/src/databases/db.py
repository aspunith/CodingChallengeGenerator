#Contains helper functions to interact with the database
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models

def get_challenge_quota(db: Session, user_id: str):
    return (db.query(models.ChallengeQuota)
            .filter(models.ChallengeQuota.user_id == user_id).
            first())
    
def create_challenge_quota(db: Session, user_id = str):
    db_quota = models.ChallengeQuota(user_id=user_id)
    db.add(db_quota) # Create a new quota entry, if it doesn't exist
    db.commit() # Commit the changes to the database
    db.refresh(db_quota) # Refresh the instance to get the updated data
    return db_quota

def reset_quota_if_needed(db: Session, quota: models.ChallengeQuota):
    now = datetime.now()
    if (now - quota.last_reset_date).total_seconds() > timedelta(hours=24).total_seconds():
        
        db.query(models.ChallengeQuota).filter(models.ChallengeQuota.id == quota.id).update({"quota_remaining": 50})
        db.query(models.ChallengeQuota).filter(models.ChallengeQuota.id == quota.id).update({"last_reset_date": now})
        db.commit() # Commit the changes to the database
        db.refresh(quota)
    return quota

def create_challenge(
    db: Session, 
    difficulty: str, 
    created_by: str, 
    title: str, 
    options: str, 
    correct_answer_id: int, 
    explanation: str
):
    db_challenge = models.Challenge(
        difficulty=difficulty,
        created_by=datetime.now(),  # Ensure created_by is a datetime object
        title=title,
        options=options,
        correct_answer_id=correct_answer_id,
        explanation=explanation
    )
    db.add(db_challenge)  # Add the new challenge to the session
    db.commit()  # Commit the changes to the database
    db.refresh(db_challenge)  # Refresh the instance to get the updated data
    return db_challenge


def get_user_challenges(db: Session, user_id: str):
    return (db.query(models.Challenge)
            .filter(models.Challenge.created_by == user_id)
            .all())