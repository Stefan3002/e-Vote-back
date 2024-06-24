from rest_framework import serializers

from e_vote_backend.models import Ballot, BallotSection


class BallotSectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BallotSection
        fields = ['title', 'slug', 'description']


class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot
        fields = ['title', 'slug', 'description', 'eligible_people', 'end_date', 'start_date']

    # slug = serializers.SerializerMethodField()
    #
    # def get_author(self, comment):
    #     author = comment.author
    #     return AppUserSerializer(author).data
    #
    # def get_slug(self, comment):
    #     challenge_slug = comment.challenge.slug
    #     return challenge_slug
