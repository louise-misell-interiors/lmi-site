import graphene
import bookings.schema
import main_site.schema


class Query(main_site.schema.Query, bookings.schema.Query, graphene.ObjectType):
    pass


class Mutation(main_site.schema.Mutation, bookings.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
