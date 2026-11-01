from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models import get_db, Submission, Progress, AnalyticsEvent, User
from api.routes.auth import get_current_user
from api.routes.challenges import CHALLENGES
from api.services.websocket import manager

router = APIRouter(prefix="/api", tags=["submissions"])

# ---------------------------------------------------------------------------
# Known flags for each challenge
# ---------------------------------------------------------------------------

FLAGS = {
    1: "DVMCP{ch1_pr0mpt_1nj3ct10n_a3f8}",
    2: "DVMCP{ch2_t00l_p01s0n_b7c2}",
    3: "DVMCP{ch3_3xc3ss1v3_p3rms_d4e1}",
    4: "DVMCP{ch4_rug_pull_sw1tch_e5f2}",
    5: "DVMCP{ch5_t00l_sh4d0w_c8d3}",
    6: "DVMCP{ch6_1nd1r3ct_1nj3ct_f7a9}",
    7: "DVMCP{ch7_t0k3n_th3ft_88b4}",
    8: "DVMCP{ch8_c0d3_3x3c_9af5}",
    9: "DVMCP{ch9_cmd_1nj3ct10n_b2c7}",
    10: "DVMCP{ch10_mult1_v3ct0r_d9e6}",
    11: "DVMCP{ch11_1d3nt1ty_1nj3ct_7x9k}",
    12: "DVMCP{ch12_s3ss10n_f1x_m4n2}",
    13: "DVMCP{ch13_pr1v_3sc_r0l3_c0nf_8k2m}",
    14: "DVMCP{ch14_supply_ch41n_p0is0n_6d3f}",
    15: "DVMCP{ch15_d3p_c0nfus10n_r3s0lv3_4e7b}",
}

# Points mapping by difficulty. Must match the `points` field exposed by
# api/routes/challenges.py::CHALLENGES so the value shown on the challenge
# list, the challenge detail page, and the submission result always agree.
DIFFICULTY_POINTS = {
    "Easy": 100,
    "Medium": 250,
    "Hard": 500,
}

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class SubmitRequest(BaseModel):
    challenge_id: int
    flag: str


class SubmitResponse(BaseModel):
    correct: bool
    points_awarded: int
    message: str

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/submit", response_model=SubmitResponse)
async def submit_flag(
    body: SubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate a flag submission for a given challenge."""
    challenge_id = body.challenge_id
    flag = body.flag.strip()

    # Validate challenge exists
    meta = CHALLENGES.get(challenge_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Check for duplicate correct submission
    existing_correct = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id,
            Submission.challenge_id == challenge_id,
            Submission.is_correct == True,
        )
        .first()
    )
    if existing_correct:
        raise HTTPException(
            status_code=400,
            detail="You have already solved this challenge",
        )

    correct = flag == FLAGS.get(challenge_id, "")

    # Points awarded must equal the value advertised on the challenge card
    # and detail page (CHALLENGES[*]['points']), which is keyed on difficulty.
    points = DIFFICULTY_POINTS.get(meta["difficulty"], 100) if correct else 0

    # Record submission
    submission = Submission(
        user_id=current_user.id,
        challenge_id=challenge_id,
        flag=flag,
        is_correct=correct,
        points_awarded=points,
        submitted_at=datetime.utcnow(),
    )
    db.add(submission)

    # Update progress
    if correct:
        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == current_user.id,
                Progress.challenge_id == challenge_id,
            )
            .first()
        )
        if progress:
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
        else:
            progress = Progress(
                user_id=current_user.id,
                challenge_id=challenge_id,
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            db.add(progress)
    else:
        # Mark as in_progress if not already tracked
        progress = (
            db.query(Progress)
            .filter(
                Progress.user_id == current_user.id,
                Progress.challenge_id == challenge_id,
            )
            .first()
        )
        if not progress:
            progress = Progress(
                user_id=current_user.id,
                challenge_id=challenge_id,
                status="in_progress",
                started_at=datetime.utcnow(),
            )
            db.add(progress)

    # Record analytics event
    event = AnalyticsEvent(
        user_id=current_user.id,
        event_type="flag_submission",
        challenge_id=challenge_id,
        data_json=f'{{"correct": {str(correct).lower()}, "points": {points}}}',
    )
    db.add(event)

    db.commit()

    # Broadcast leaderboard update via WebSocket if correct
    if correct:
        await manager.broadcast(
            {
                "type": "leaderboard_update",
                "data": {
                    "username": current_user.username,
                    "challenge_id": challenge_id,
                    "challenge_name": meta["name"],
                    "points_awarded": points,
                },
            }
        )

    if correct:
        message = f"Correct! You earned {points} points."
    else:
        message = "Incorrect flag. Keep trying!"

    return SubmitResponse(
        correct=correct,
        points_awarded=points,
        message=message,
    )
