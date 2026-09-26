"""Seed the database with a realistic freelance-artist demo dataset.

Usage:  ../.venv/bin/python seed.py      (from the backend dir)
"""

from datetime import date as DateType
from datetime import timedelta

from sqlmodel import Session, select

from app.database import engine, init_db
from app.models import Commission, Transaction, dollars_to_cents

TODAY = DateType.today()

TRANSACTIONS = [
    # (type, amount, description, date, fee_amount, source, category, merchant)
    ("income", 350.0, "commission: character bust for Nova", TODAY - timedelta(days=130), 0, "commission", None, None),
    ("income", 90.0, "sticker pack - Etsy sale x6", TODAY - timedelta(days=126), 6.3, "etsy", None, "Etsy"),
    ("expense", 18.5, "digital print paper", TODAY - timedelta(days=125), None, None, "supplies", "Blick Art"),
    ("income", 180.0, "Patreon monthly support", TODAY - timedelta(days=120), 0, "patreon", None, "Patreon"),
    ("expense", 20.0, "Adobe Illustrator sub", TODAY - timedelta(days=118), None, None, "subscriptions", "Adobe"),
    ("income", 500.0, "commission: full portrait for Wren", TODAY - timedelta(days=112), 0, "commission", None, None),
    ("expense", 6.4, "Etsy listing + payment fees", TODAY - timedelta(days=110), None, None, "platform_fees", "Etsy"),
    ("expense", 36.0, "paint set - gouache", TODAY - timedelta(days=105), None, None, "supplies", "Blick Art"),
    ("income", 240.0, "Patreon monthly support", TODAY - timedelta(days=90), 0, "patreon", None, "Patreon"),
    ("income", 45.0, "digital print - Etsy sale x3", TODAY - timedelta(days=88), 3.1, "etsy", None, "Etsy"),
    ("expense", 60.0, "Procreate + brushes", TODAY - timedelta(days=85), None, None, "subscriptions", "Procreate"),
    ("income", 800.0, "commission: twitch panels for Sol", TODAY - timedelta(days=80), 0, "commission", None, None),
    ("expense", 22.0, "mat board + sleeves", TODAY - timedelta(days=76), None, None, "supplies", "Blick Art"),
    ("income", 240.0, "Patreon monthly support", TODAY - timedelta(days=60), 0, "patreon", None, "Patreon"),
    ("income", 110.0, "print drop - Etsy sale", TODAY - timedelta(days=57), 7.7, "etsy", None, "Etsy"),
    ("expense", 15.0, "Spotify artist tools", TODAY - timedelta(days=30), None, None, "subscriptions", "Spotify"),
    ("income", 260.0, "Patreon monthly support", TODAY - timedelta(days=30), 0, "patreon", None, "Patreon"),
    ("expense", 12.0, "shipping supplies - mailers", TODAY - timedelta(days=28), None, None, "supplies", "UPS Store"),
    ("income", 300.0, "commission: icon set for Rae", TODAY - timedelta(days=25), 0, "commission", None, None),
    ("expense", 19.99, "Dropbox for file delivery", TODAY - timedelta(days=22), None, None, "subscriptions", "Dropbox"),
    ("income", 160.0, "sticker + print Etsy sale", TODAY - timedelta(days=20), 11.2, "etsy", None, "Etsy"),
    ("expense", 8.5, "washed paper pads", TODAY - timedelta(days=18), None, None, "supplies", "Blick Art"),
    ("income", 240.0, "Patreon monthly support", TODAY, 0, "patreon", None, "Patreon"),
    ("expense", 45.0, "bank transfer fee (Wise)", TODAY - timedelta(days=15), None, None, "platform_fees", "Wise"),
]

LINKED_COMMISSIONS = [
    # (client, piece, hours, amount, linked_transaction_index)
    ("Nova", "character bust", 9, 350.0, 0),
    ("Wren", "full portrait", 18, 500.0, 5),
    ("Sol", "twitch panels x4", 14, 800.0, 11),
    ("Rae", "icon set x8", 8, 300.0, 18),
]

PENDING_COMMISSIONS = [
    # (client, piece, hours, amount, expected_date_delta_days, status)
    ("Indigo", "album cover", 0, 700.0, 12, "agreed"),
    ("Kite", "comm sticker sheet", 2, 220.0, 20, "in_progress"),
    ("Fern", "tabletop token set", 5, 500.0, 7, "in_progress"),
]


def seed() -> None:
    init_db()
    with Session(engine) as session:
        existing = session.exec(select(Transaction)).first()
        if existing is not None:
            print("Database already has data; clearing it first.")
            for t in session.exec(select(Transaction)).all():
                session.delete(t)
            for c in session.exec(select(Commission)).all():
                session.delete(c)
            session.commit()

        tx_ids: list[int] = []
        for row in TRANSACTIONS:
            tx = Transaction(
                type=row[0],
                amount_cents=dollars_to_cents(row[1]),
                description=row[2],
                date=row[3],
                fee_amount_cents=None if row[4] is None else dollars_to_cents(row[4]),
                source=row[5],
                category=row[6],
                merchant=row[7],
            )
            session.add(tx)
            session.flush()
            tx_ids.append(tx.id)  # type: ignore[union-attr]

        for client, piece, hours, amount, tx_index in LINKED_COMMISSIONS:
            session.add(
                Commission(
                    client=client,
                    piece=piece,
                    hours_spent=hours,
                    amount_cents=dollars_to_cents(amount),
                    expected_date=TODAY - timedelta(days=3),
                    status="completed",
                    transaction_id=tx_ids[tx_index],
                )
            )

        for client, piece, hours, amount, delta_days, status in PENDING_COMMISSIONS:
            session.add(
                Commission(
                    client=client,
                    piece=piece,
                    hours_spent=hours,
                    amount_cents=dollars_to_cents(amount),
                    expected_date=TODAY + timedelta(days=delta_days),
                    status=status,
                )
            )

        session.commit()
        total_commissions = len(LINKED_COMMISSIONS) + len(PENDING_COMMISSIONS)
        print(f"Seeded {len(TRANSACTIONS)} transactions and {total_commissions} commissions.")


if __name__ == "__main__":
    seed()
