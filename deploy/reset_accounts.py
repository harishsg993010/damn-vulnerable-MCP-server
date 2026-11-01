#!/usr/bin/env python3
"""Remove player accounts and everything attached to them.

Deleting a user row on its own leaves submissions, hint usage, progress,
analytics events, and the pool slot behind. An orphaned slot stays taken.

Run it from the lab host through deploy/reset_accounts.sh. That wrapper
deletes the accounts and restarts each freed player container:

    ./deploy/reset_accounts.sh --prefix smoke_ --dry-run
    ./deploy/reset_accounts.sh --prefix smoke_
    ./deploy/reset_accounts.sh --all
"""

import argparse
import sys

sys.path.insert(0, "/app/dashboard/backend")

from database.models import (  # noqa: E402
    AnalyticsEvent,
    HintUsage,
    PlayerSlot,
    Progress,
    SessionLocal,
    Submission,
    User,
)

CHILD_MODELS = (Submission, Progress, HintUsage, AnalyticsEvent, PlayerSlot)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--prefix", help="delete accounts whose username starts with this")
    group.add_argument("--all", action="store_true", help="delete every account")
    ap.add_argument("--dry-run", action="store_true", help="show what would be deleted")
    args = ap.parse_args()

    db = SessionLocal()
    query = db.query(User)
    if args.prefix:
        users = [u for u in query.all() if u.username.startswith(args.prefix)]
    else:
        users = query.all()

    if not users:
        print("No matching accounts.")
        return 0

    print(f"{'Would delete' if args.dry_run else 'Deleting'} {len(users)} account(s):")
    freed_slots: list[int] = []
    for u in users:
        slot = db.query(PlayerSlot).filter(PlayerSlot.user_id == u.id).first()
        subs = db.query(Submission).filter(Submission.user_id == u.id).count()
        print(f"  {u.username:<24} slot={slot.slot if slot else '-':<4} submissions={subs}")
        if slot is not None:
            freed_slots.append(slot.slot)

    if args.dry_run:
        for slot_id in freed_slots:
            print(f"WOULD_FREE_SLOT {slot_id}")
        return 0

    user_ids = [u.id for u in users]
    for model in CHILD_MODELS:
        db.query(model).filter(model.user_id.in_(user_ids)).delete(synchronize_session=False)
    db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    db.commit()

    remaining = db.query(User).count()
    free_slots = db.query(PlayerSlot).count()
    print(f"\nDone. {remaining} account(s) left, {free_slots} pool slot(s) still assigned.")
    for slot_id in freed_slots:
        print(f"FREED_SLOT {slot_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
