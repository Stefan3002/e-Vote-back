from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from e_vote_backend.models import Ballot
from e_vote_backend.security_utils import encrypt_data_user_pk
from e_vote_backend.serializers import BallotSerializer, BallotSectionsSerializer
from e_vote_backend.validations.ballot_validations import ballot_validator
from e_vote_backend.views.auth_views.auth_views import performAuth


class all_ballots(APIView):
    def post(self, request):
        try:
            # Zero trust policy, authenticate again and again
            (res, user) = performAuth(request.data, True)
            if res.status_code != 200:
                print('NO AUTH!')
                return res

            # Identity confirmed from here on
            ballots = Ballot.objects.all()
            serialized_ballots = BallotSerializer(ballots, many=True)
            # TODO: Encrypt the date with the user's public key to prevent MitM attacks
            encrypted_data = encrypt_data_user_pk(serialized_ballots.data, user.public_key)
            return Response({'data': encrypted_data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'data': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ballot_sections(APIView):
    def post(self, request):
        try:
            # Zero trust policy, authenticate again and again
            (res, user) = performAuth(request.data, True)
            if res.status_code != 200:
                print('NO AUTH!')
                return res

            # Identity confirmed from here on
            slug = request.data['slug']
            if ballot_validator['slug']["inputNull"] is False and (not slug):
                return Response({'OK': False, 'data': 'Slug of ballot is missing!'},
                                status=status.HTTP_400_BAD_REQUEST)

            ballot = Ballot.objects.get(slug=slug)
            ballot_sections = ballot.sections.all()

            serialized_ballot_sections = BallotSectionsSerializer(ballot_sections, many=True)
            # TODO: Encrypt the date with the user's public key to prevent MitM attacks
            encrypted_data = encrypt_data_user_pk(serialized_ballot_sections.data, user.public_key)
            return Response({'data': encrypted_data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'data': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
