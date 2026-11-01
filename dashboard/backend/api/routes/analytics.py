from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, desc, case
from sqlalchemy.orm import Session

from database.models import get_db, Submission, User, Progress, HintUsage, AnalyticsEvent
from api.routes.auth import get_current_user
from api.routes.challenges import CHALLENGES

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/global")
def global_analytics(db: Session = Depends(get_db)):
    """Return aggregate statistics across all users and challenges."""

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_submissions = db.query(func.count(Submission.id)).scalar() or 0
    total_correct = (
        db.query(func.count(Submission.id))
        .filter(Submission.is_correct == True)
        .scalar()
        or 0
    )

    # Solves per challenge
    solves_per_challenge = (
        db.query(
            Submission.challenge_id,
            func.count(func.distinct(Submission.user_id)).label("solvers"),
        )
        .filter(Submission.is_correct == True)
        .group_by(Submission.challenge_id)
        .all()
    )

    solve_map = {row.challenge_id: row.solvers for row in solves_per_challenge}

    # Most solved
    most_solved = None
    least_solved = None
    if solve_map:
        most_id = max(solve_map, key=solve_map.get)
        least_id = min(solve_map, key=solve_map.get)
        most_solved = {
            "challenge_id": most_id,
            "name": CHALLENGES[most_id]["name"],
            "solvers": solve_map[most_id],
        }
        least_solved = {
            "challenge_id": least_id,
            "name": CHALLENGES[least_id]["name"],
            "solvers": solve_map[least_id],
        }

    # Average completion time (for solved challenges only)
    # Computed as time between first attempt and first correct submission per user per challenge
    avg_times = []
    for cid in CHALLENGES:
        first_attempts = (
            db.query(
                Submission.user_id,
                func.min(Submission.submitted_at).label("first_attempt"),
            )
            .filter(Submission.challenge_id == cid)
            .group_by(Submission.user_id)
            .subquery()
        )

        correct_times = (
            db.query(
                Submission.user_id,
                func.min(Submission.submitted_at).label("solved_at"),
            )
            .filter(Submission.challenge_id == cid, Submission.is_correct == True)
            .group_by(Submission.user_id)
            .subquery()
        )

        rows = (
            db.query(
                first_attempts.c.user_id,
                first_attempts.c.first_attempt,
                correct_times.c.solved_at,
            )
            .join(correct_times, first_attempts.c.user_id == correct_times.c.user_id)
            .all()
        )

        if rows:
            durations = []
            for r in rows:
                if r.solved_at and r.first_attempt:
                    delta = (r.solved_at - r.first_attempt).total_seconds()
                    durations.append(delta)
            if durations:
                avg_seconds = sum(durations) / len(durations)
                avg_times.append(
                    {
                        "challenge_id": cid,
                        "name": CHALLENGES[cid]["name"],
                        "avg_seconds": round(avg_seconds, 1),
                        "solvers": len(durations),
                    }
                )

    # Challenge breakdown. The frontend reads `id` and `solve_rate` (the
    # percentage of users who solved the challenge), so expose both along
    # with the raw numbers.
    challenge_stats = []
    for cid, meta in CHALLENGES.items():
        solvers = solve_map.get(cid, 0)
        solve_rate = round(solvers / total_users * 100, 1) if total_users else 0.0
        challenge_stats.append(
            {
                "id": cid,
                "challenge_id": cid,
                "name": meta["name"],
                "category": meta["category"],
                "difficulty": meta["difficulty"],
                "solvers": solvers,
                "solve_rate": solve_rate,
            }
        )

    return {
        "total_users": total_users,
        "total_submissions": total_submissions,
        "total_correct_submissions": total_correct,
        "most_solved": most_solved,
        "most_solved_challenge": most_solved["name"] if most_solved else None,
        "least_solved": least_solved,
        "average_completion_times": avg_times,
        "challenge_stats": challenge_stats,
    }


class EventRequest(BaseModel):
    event_type: str
    challenge_id: int


@router.post("/event")
def record_client_event(
    body: EventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a page event the browser can see, such as opening a challenge."""
    if body.event_type != "challenge_view":
        raise HTTPException(status_code=400, detail="Unsupported event")
    if body.challenge_id not in CHALLENGES:
        raise HTTPException(status_code=404, detail="Challenge not found")
    db.add(AnalyticsEvent(
        user_id=current_user.id,
        event_type=body.event_type,
        challenge_id=body.challenge_id,
    ))
    db.commit()
    return {"ok": True}


@router.get("/user")
def user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return personal statistics for the authenticated user."""

    # Challenges completed
    completed = (
        db.query(Submission.challenge_id)
        .filter(Submission.user_id == current_user.id, Submission.is_correct == True)
        .distinct()
        .all()
    )
    completed_ids = [r.challenge_id for r in completed]

    # Total points earned from correct submissions
    total_earned = (
        db.query(func.sum(Submission.points_awarded))
        .filter(Submission.user_id == current_user.id, Submission.is_correct == True)
        .scalar()
        or 0
    )

    # Total points spent on hints
    total_spent = (
        db.query(func.sum(HintUsage.points_cost))
        .filter(HintUsage.user_id == current_user.id)
        .scalar()
        or 0
    )

    net_points = total_earned - total_spent

    # Total submissions
    total_submissions = (
        db.query(func.count(Submission.id))
        .filter(Submission.user_id == current_user.id)
        .scalar()
        or 0
    )

    total_correct = (
        db.query(func.count(Submission.id))
        .filter(Submission.user_id == current_user.id, Submission.is_correct == True)
        .scalar()
        or 0
    )

    success_rate = round(total_correct / total_submissions * 100, 1) if total_submissions > 0 else 0.0

    # Time per challenge
    time_per_challenge = []
    for cid in completed_ids:
        first_attempt = (
            db.query(func.min(Submission.submitted_at))
            .filter(Submission.user_id == current_user.id, Submission.challenge_id == cid)
            .scalar()
        )
        solved_at = (
            db.query(func.min(Submission.submitted_at))
            .filter(
                Submission.user_id == current_user.id,
                Submission.challenge_id == cid,
                Submission.is_correct == True,
            )
            .scalar()
        )
        if first_attempt and solved_at:
            delta = (solved_at - first_attempt).total_seconds()
            time_per_challenge.append(
                {
                    "challenge_id": cid,
                    "name": CHALLENGES.get(cid, {}).get("name", "Unknown"),
                    "seconds": round(delta, 1),
                }
            )

    # Success rate by category
    category_stats = {}
    for cid, meta in CHALLENGES.items():
        cat = meta["category"]
        if cat not in category_stats:
            category_stats[cat] = {"attempts": 0, "correct": 0}

        user_attempts = (
            db.query(func.count(Submission.id))
            .filter(Submission.user_id == current_user.id, Submission.challenge_id == cid)
            .scalar()
            or 0
        )
        user_correct = (
            db.query(func.count(Submission.id))
            .filter(
                Submission.user_id == current_user.id,
                Submission.challenge_id == cid,
                Submission.is_correct == True,
            )
            .scalar()
            or 0
        )
        category_stats[cat]["attempts"] += user_attempts
        category_stats[cat]["correct"] += user_correct

    success_by_category = []
    for cat, stats in category_stats.items():
        rate = round(stats["correct"] / stats["attempts"] * 100, 1) if stats["attempts"] > 0 else 0.0
        success_by_category.append(
            {
                "category": cat,
                "attempts": stats["attempts"],
                "correct": stats["correct"],
                "success_rate": rate,
            }
        )

    # Hints used
    hints_used = (
        db.query(func.count(HintUsage.id))
        .filter(HintUsage.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Solved-challenge counts bucketed by category and difficulty — the
    # frontend's Skill Radar, Category Bar, and Difficulty Pie charts
    # index into these dicts directly.
    by_category: dict[str, int] = {}
    by_difficulty: dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}
    for cid in completed_ids:
        meta = CHALLENGES.get(cid)
        if not meta:
            continue
        by_category[meta["category"]] = by_category.get(meta["category"], 0) + 1
        by_difficulty[meta["difficulty"]] = by_difficulty.get(meta["difficulty"], 0) + 1

    return {
        "username": current_user.username,
        "challenges_completed": len(completed_ids),
        "completed_challenge_ids": completed_ids,
        "total_challenges": len(CHALLENGES),
        "total_points": net_points,
        "points_earned": total_earned,
        "points_spent_on_hints": total_spent,
        "total_submissions": total_submissions,
        "correct_submissions": total_correct,
        "success_rate": success_rate,
        "time_per_challenge": time_per_challenge,
        "success_by_category": success_by_category,
        "by_category": by_category,
        "by_difficulty": by_difficulty,
        "hints_used": hints_used,
    }
