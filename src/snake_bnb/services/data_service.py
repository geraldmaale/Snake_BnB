import datetime
from typing import List
import bson

from data.bookings import Booking
from data.cages import Cage
from data.owners import Owner
from data.snakes import Snake


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()
    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects().filter(email=email).first()
    return owner


def register_cage(active_account: Owner, meters, carpeted, has_toys, allow_dangerous, name, price) -> Cage:
    cage = Cage()
    cage.square_meters = meters
    cage.name = name
    cage.allow_dangerous_snakes = allow_dangerous
    cage.is_carpeted = carpeted
    cage.has_toys = has_toys
    cage.price = price

    cage.save()

    account = find_account_by_email(active_account.email)
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)
    return cages


def add_available_date(cage: Cage, start_date: datetime.datetime, days: int) -> Cage:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    cage = Cage.objects(id=cage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage


def add_snake(account: Owner, name: str, length: float, species: str, is_venomous) -> Snake:
    owner = find_account_by_email(account.email)

    snake = Snake()
    snake.name = name
    snake.length = length
    snake.species = species
    snake.is_venomous = is_venomous
    snake.save()

    owner.snake_ids.append(snake.id)
    owner.save()

    return snake


def get_snakes_for_user(user_id: bson.ObjectId) -> List[Snake]:
    owner = Owner.objects(id=user_id).first()
    snakes = Snake.objects(id__in=owner.snake_ids).all()

    return list(snakes)


def get_available_cages(checkin: datetime.datetime, checkout: datetime.datetime, snake: Snake) -> List[Cage]:
    min_size = snake.length / 4

    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    # Todo: use _match to compare

    if snake.is_venomous:
        query = query.filter(allow_dangerous_snakes=True)

    cages = query.order_by('price', '-square_meters')

    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
                final_cages.append(c)

    return cages


def book_cage(account, snake, cage, checkin, checkout):
    booking:Booking = Booking()

    for b in cage.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_snake_id = snake.id
    booking.booked_date = datetime.datetime.now()

    cage.save()

