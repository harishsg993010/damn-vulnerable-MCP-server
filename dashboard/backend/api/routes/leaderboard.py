from fastapi import APIRouter, Depends
from sqlalchemy import func, desc, literal
from sqlalchemy.orm import Session

from database.models import get_db, Submission, HintUsage, User

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """Return the global leaderboard: top 100 users ranked by net points
    (earned from correct submissions minus hint costs).

    Each entry contains: rank, username, total_points, challenges_completed,
    and last_submission timestamp.
    """
    points_sub = (
        db.query(
            Submission.user_id,
            func.sum(Submission.points_awarded).label("total_earned"),
            func.count(func.distinct(Submission.challenge_id)).label("challenges_completed"),
            func.max(Submission.submitted_at).label("last_submission"),
        )
        .filter(Submission.is_correct == True)
        .group_by(Submission.user_id)
        .subquery()
    )

    hints_sub = (
        db.query(
            HintUsage.user_id,
            func.coalesce(func.sum(HintUsage.points_cost), literal(0)).label("total_spent"),
        )
        .group_by(HintUsage.user_id)
        .subquery()
    )

    rows = (
        db.query(
            User.username,
            points_sub.c.total_earned,
            hints_sub.c.total_spent,
            points_sub.c.challenges_completed,
            points_sub.c.last_submission,
        )
        .join(points_sub, User.id == points_sub.c.user_id)
        .outerjoin(hints_sub, User.id == hints_sub.c.user_id)
        .order_by(desc(points_sub.c.total_earned - func.coalesce(hints_sub.c.total_spent, literal(0))))
        .limit(100)
        .all()
    )

    leaderboard = []
    for rank, row in enumerate(rows, start=1):
        earned = row.total_earned or 0
        spent = row.total_spent or 0
        leaderboard.append(
            {
                "rank": rank,
                "username": row.username,
                "total_points": earned - spent,
                "challenges_completed": row.challenges_completed or 0,
                "last_submission": row.last_submission.isoformat() if row.last_submission else None,
            }
        )

    return leaderboard
