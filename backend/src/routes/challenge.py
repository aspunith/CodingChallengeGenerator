from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..ai_generator import generate_challenge_with_ai
from ..databases.db import (
    get_challenge_quota,
    create_challenge,
    create_challenge_quota,
    reset_quota_if_needed,
    get_user_challenges
)
from ..utils import authenticate_and_get_user_details
from ..databases.models import get_db
import json
from datetime import datetime

router = APIRouter()


class ChallengeRequest(BaseModel):
    difficulty: str

    class Config:
        json_schema_extra = {"example": {"difficulty": "easy"}}


@router.post("/generate-challenge")
async def generate_challenge(request: ChallengeRequest, request_obj: Request, db: Session = Depends(get_db)):
    try:
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = str(user_details.get("user_id"))  # Ensure user_id is a string

        if user_id is None:
            raise HTTPException(status_code=401, detail="User ID is missing")
        
        quota = get_challenge_quota(db, user_id)
        if not quota:
            quota = create_challenge_quota(db, user_id)

        quota = reset_quota_if_needed(db, quota)

        if quota.quota_remaining <= 0:
            raise HTTPException(status_code=429, detail="Quota exhausted")

        challenge_data = generate_challenge_with_ai(request.difficulty)

        new_challenge = create_challenge(
            db=db,
            difficulty=request.difficulty,
            created_by=user_id,
            title=challenge_data["title"],
            options=json.dumps(challenge_data["options"]),
            correct_answer_id=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"]
        )

        new_quota_remaining = quota.quota_remaining - 1
        db.query(type(quota)).filter_by(id=quota.id).update({"quota_remaining": new_quota_remaining})
        db.commit()

        return {
            "id": new_challenge.id,
            "difficulty": request.difficulty,
            "title": new_challenge.title,
            "options": json.loads(new_challenge.options) if isinstance(new_challenge.options, str) else new_challenge.options,
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explanation,
            "timestamp": new_challenge.date_created.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-history")
async def my_history(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="User ID is missing")
    challenges = get_user_challenges(db, user_id)
    return {"challenges": challenges}


@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    try:
        user_details = authenticate_and_get_user_details(request)
        print(f"User Details: {user_details}")  # Debug log

        if not user_details or "user_id" not in user_details:
            raise HTTPException(status_code=401, detail="Authentication failed")

        user_id = user_details["user_id"]
        print(f"User ID: {user_id}")  # Debug log

        quota = get_challenge_quota(db, user_id)
        print(f"Quota: {quota}")  # Debug log

        if not quota:
            create_challenge_quota(db, user_id)
            quota = get_challenge_quota(db, user_id)

        quota = reset_quota_if_needed(db, quota)
        return quota
    except Exception as e:
        print(f"Error: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))