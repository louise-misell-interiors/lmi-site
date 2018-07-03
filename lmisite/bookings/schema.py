from graphene_django import DjangoObjectType
import datetime
import graphene.types.datetime
from . import models


class BookingType(DjangoObjectType):
    class Meta:
        model = models.BookingType

    booking_days = graphene.List(
        graphene.types.datetime.Date,
        num=graphene.Int(default_value=5),
        start=graphene.Date(default_value=datetime.datetime.now().date()))

    def resolve_booking_days(self, info, **kwargs):
        days = []
        day = kwargs.get("start")
        for i in range(kwargs.get("num")):
            days.append(day)
            day = day + datetime.timedelta(days=1)

        return days


class Query(graphene.ObjectType):
    booking_types = graphene.List(BookingType)
    booking_type = graphene.Field(
        BookingType,
        id=graphene.ID(required=True)
    )

    def resolve_booking_types(self, info, **kwargs):
        return models.BookingType.objects.all()

    def resolve_booking_type(self, info, **kwargs):
        return models.BookingType.objects.get(pk=kwargs.get("id"))


schema = graphene.Schema(query=Query)
