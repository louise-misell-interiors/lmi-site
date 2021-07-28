import graphene
import graphql_relay
import django_filters
import graphene_django.filter
import magiclink.helpers
import graphql
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.db import transaction
from . import models


class QuizStepAnswerNode(graphene_django.DjangoObjectType):
    class Meta:
        model = models.QuizStepAnswer
        fields = ('id', 'text', 'alt_text', 'image', 'step')
        filter_fields = []
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_staff:
            return queryset
        return queryset.filter(step__quiz__draft=False)

    def resolve_image(self, _info):
        if self.image:
            return self.image.url
        else:
            return None


class QuizStepNode(graphene_django.DjangoObjectType):
    answers = graphene_django.filter.DjangoFilterConnectionField(QuizStepAnswerNode)

    class Meta:
        model = models.QuizStep
        fields = ('id', 'style', 'question_text', 'answers', 'quiz', 'max_choices')
        filter_fields = []
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_staff:
            return queryset
        return queryset.filter(quiz__draft=False)


class QuizNodeFilterSet(django_filters.FilterSet):
    class Meta:
        model = models.Quiz
        fields = ('id',)


class QuizNode(graphene_django.DjangoObjectType):
    steps = graphene_django.filter.DjangoFilterConnectionField(QuizStepNode)

    class Meta:
        model = models.Quiz
        fields = ('id', 'name', 'intro_text', 'steps', 'result_header', 'result_save_to_email')
        filterset_class = QuizNodeFilterSet
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_staff:
            return queryset
        return queryset.filter(draft=False)


class QuizResultNode(graphene_django.DjangoObjectType):
    class Meta:
        model = models.QuizResult
        fields = ('id', 'quiz', 'text', 'image', 'link', 'link_text')
        interfaces = (graphene.relay.Node,)


class QuizSessionNode(graphene_django.DjangoObjectType):
    result = graphene.Field(QuizResultNode)
    has_user = graphene.Boolean(required=True)

    class Meta:
        model = models.QuizSession
        fields = ('id', 'quiz', 'current_step', 'result')
        interfaces = (graphene.relay.Node,)

    def resolve_has_user(self: models.QuizSession, _info):
        return self.user is not None


class CreateQuizSessionMutation(graphene.relay.ClientIDMutation):
    class Input:
        quiz_id = graphene.ID(required=True)

    session = graphene.Field(QuizSessionNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, quiz_id):
        qs = models.Quiz.objects.all()
        if not info.context.user.is_staff:
            qs = qs.filter(draft=False)

        quiz = qs.get(id=graphql_relay.from_global_id(quiz_id)[1])
        first_step = quiz.steps.first()

        session = models.QuizSession(
            quiz=quiz,
            current_step=first_step,
            user=info.context.user if info.context.user.is_authenticated else None
        )
        session.save()
        return cls(session=session)


class ProgressQuizSessionMutation(graphene.relay.ClientIDMutation):
    class Input:
        session_id = graphene.ID(required=True)
        answer_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)

    session = graphene.Field(QuizSessionNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, session_id, answer_ids):
        session = models.QuizSession.objects.get(id=graphql_relay.from_global_id(session_id)[1])
        next_step = session.quiz.steps.filter(order__gt=session.current_step.order).order_by('order').first()

        answers = list(map(
            lambda a: models.QuizStepAnswer.objects.get(
                id=graphql_relay.from_global_id(a)[1], step=session.current_step
            ), answer_ids
        ))

        for answer in answers:
            models.QuizSessionStepAnswer(
                session=session,
                answer=answer
            ).save()

        session.current_step = next_step
        session.save()

        return cls(session=session)


class UserInfo(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)


class SaveToEmailError(graphene.ObjectType):
    field = graphene.String(required=True)
    errors = graphene.List(
        graphene.String,
        required=True
    )


def validation_error_to_graphene(error):
    return map(lambda item: SaveToEmailError(field=item[0], errors=item[1]), error)


def email_quiz_session(session):
    config = models.SiteConfig.objects.first()

    context = {
        "session": session,
        "config": config
    }

    email_msg = EmailMultiAlternatives(
        subject="Your quiz results",
        body=render_to_string("main_site/quiz_email.html", context),
        to=[session.user.email],
        reply_to=[f"Louise Misell Interiors <{config.email}>"]
    )
    email_msg.content_subtype = "html"
    email_msg.send()


class SaveToEmailQuizSessionMutation(graphene.relay.ClientIDMutation):
    class Input:
        session_id = graphene.ID(required=True)
        user_info = graphene.Field(UserInfo, required=False)

    ok = graphene.Boolean()
    error = graphene.List(SaveToEmailError)

    @classmethod
    def mutate_and_get_payload(cls, root, info, session_id, user_info=None):
        session = models.QuizSession.objects.get(id=graphql_relay.from_global_id(session_id)[1])

        if not session.user:
            if not user_info:
                raise graphql.GraphQLError("User info must be specified on an anonymous session")

            if not user_info.email:
                return cls(ok=False, error=[
                    SaveToEmailError(field='email', errors=['Email cannot be blank'])
                ])

            if not user_info.name:
                return cls(ok=False, error=[
                    SaveToEmailError(field='email', errors=['Name cannot be blank'])
                ])

            try:
                validate_email(user_info.email)
            except ValidationError as e:
                return cls(ok=False, error=[
                    SaveToEmailError(field='email', errors=[e.message])
                ])

            try:
                first_name, last_name = user_info.name.split(" ", 1)
            except ValueError:
                first_name = user_info.name
                last_name = ''

            try:
                user = magiclink.helpers.get_or_create_user(
                    email=user_info.email,
                    first_name=first_name,
                    last_name=last_name,
                )
            except ValidationError as e:
                return cls(ok=False, error=validation_error_to_graphene(e))

            session.user = user
            session.save()

        email_quiz_session(session)

        return cls(ok=True, error=None)


class Query(graphene.ObjectType):
    quiz = graphene.relay.Node.Field(QuizNode)
    quiz_session = graphene.relay.Node.Field(QuizSessionNode)
    quiz_step = graphene.relay.Node.Field(QuizStepNode)
    all_quizzes = graphene_django.filter.DjangoFilterConnectionField(QuizNode)


class Mutation(graphene.ObjectType):
    create_quiz_session = CreateQuizSessionMutation.Field()
    progress_quiz_session = ProgressQuizSessionMutation.Field()
    save_to_email_quiz_session = SaveToEmailQuizSessionMutation.Field()
