from mongoengine import *


class Booking(EmbeddedDocument):
    guest_owner_id = ObjectIdField()
    guest_snake_id = ObjectIdField()

    booked_date = DateTimeField()
    check_in_date = DateTimeField(required=True)
    check_out_date = DateTimeField(required=True)

    review = StringField()
    rating = IntField(default=0)

    @property
    def duration_in_days(self):
        dt = self.check_out_date- self.check_in_date
        return dt.days
