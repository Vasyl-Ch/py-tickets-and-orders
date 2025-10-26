from django.db import transaction
from django.db.models import QuerySet
from django.utils.dateparse import parse_datetime
from db.models import Order, Ticket, MovieSession, User


@transaction.atomic
def create_order(
        tickets: list[dict],
        username: str,
        date: str = None
) -> Order:
    user = User.objects.get(username=username)

    ticket_objects = []
    for ticket_data in tickets:
        movie_session = MovieSession.objects.get(
            pk=ticket_data["movie_session"]
        )

        ticket = Ticket(
            movie_session=movie_session,
            row=ticket_data["row"],
            seat=ticket_data["seat"],
            order_id=None  # Временно None
        )
        ticket_objects.append((ticket, movie_session))

    order_data = {"user": user}
    if date:
        order_data["created_at"] = parse_datetime(date)

    order = Order.objects.create(**order_data)

    validated_tickets = []
    for ticket, movie_session in ticket_objects:
        ticket.order = order
        ticket.full_clean()
        validated_tickets.append(ticket)

    Ticket.objects.bulk_create(validated_tickets)

    return order


def get_orders(username: str = None) -> QuerySet:
    if username is None:
        return Order.objects.all()

    user = User.objects.get(username=username)

    return user.orders.all()
