import os

import ecdsa as ecdsa
from ecdsa import SECP256k1
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from e_vote_backend.models import AppUser
from e_vote_backend.validations.auth_validations import auth_validator

public_params = {
    'p': int('0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f', 16),
    'q': int('0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141', 16),
}


def generateRandomNumber(curve):
    # Generate a random number between [1, 2^t - 1]
    # Where t is the number of bits of the challenge chosen by the server
    seed = os.urandom(80 // 8)
    return ecdsa.util.randrange_from_seed__trytryagain(seed, curve.order)


def performAuth(data, return_user=False):
    try:
        username = data['username']
        try:
            user = AppUser.objects.get(username=username)
        except AppUser.DoesNotExist:
            return Response({'data': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        public_key = data['publicKey']

        if public_key != user.public_key:
            return Response({'data': 'Public Key does not match'}, status=status.HTTP_401_UNAUTHORIZED)

        r = int(data['r'], 16)
        V_x = int(data['V_x'], 16)
        V_y = int(data['V_y'], 16)
        P_y = int(data['P_y'], 16)
        P_x = int(data['P_x'], 16)

        if auth_validator['r']["inputNull"] is False and (not r):
            return Response({'OK': False, 'data': 'r is missing!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if auth_validator['V_x']["inputNull"] is False and (not V_x):
            return Response({'OK': False, 'data': 'V_x is missing!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if auth_validator['V_y']["inputNull"] is False and (not V_y):
            return Response({'OK': False, 'data': 'V_y is missing!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if auth_validator['P_x']["inputNull"] is False and (not P_x):
            return Response({'OK': False, 'data': 'P_x is missing!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if auth_validator['P_y']["inputNull"] is False and (not P_y):
            return Response({'OK': False, 'data': 'P_y is missing!'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Convert the public key from hexadecimal to integer
        public_key = int(public_key, 16)
        # Initialize the secp256k1 curve
        curve = SECP256k1
        # Create a new elliptic curve point with the public key (this is just to be able to do the scalar
        # multiplication over the elliptic curve)
        pk = ecdsa.ellipticcurve.Point(curve.curve, P_x, P_y)

        # Check to see if the public key is within [1, p - 1]
        if not curve.curve.contains_point(P_x, P_y):
            return Response({'data': 'Public Key out of range'}, status=status.HTTP_400_BAD_REQUEST)
        # Check to see if the public key has a discrete logarithm with respect to the base G
        if pk * 1 == ecdsa.ellipticcurve.INFINITY:
            return Response(
                {'data': 'Public Key not valid, it does not have a discrete logarithm with respect to the '
                         'base g'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the generator with its default parameters
        G = curve.generator
        # Retrieve the issued challenge
        c = int(user.challenge_issued, 16)
        # Calculate the target point
        target = (G * r) + (pk * c)
        # Create a new elliptic curve point with the public key
        # (this is just to be able to compare the target point with the V point from the user)
        V = ecdsa.ellipticcurve.Point(curve.curve, V_x, V_y)

        print(target.x(), V.x(), target.y(), V.y())
        # Compare the results, they must yield the same point if the user has the correct private key
        if user.challenge_burnt is False and target.x() == V.x() and target.y() == V.y():
            user.challenge_burnt = True
            user.save()
            if return_user:
                return Response({'data': 'OK'}, status=status.HTTP_200_OK), user
            return Response({'data': 'OK'}, status=status.HTTP_200_OK)
        else:
            if user.challenge_burnt is True:
                print('Challenge already burnt')
                # TODO: LOG THE INTRUSION AND POSSIBLE SECURITY BREACH (REPLAY ATTACK)
                return Response({'data': 'Challenge already burnt'}, status=status.HTTP_400_BAD_REQUEST)
            user.challenge_burnt = True
            user.save()
            return Response({'data': 'Wrong Key'}, status=status.HTTP_401_UNAUTHORIZED)
    except KeyError as err:
        print(str(err))
        return Response({'data': 'Missing parameter: ' + str(err)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        print(str(err))
        return Response({'data': 'Something happened on our side. This is what we know so far: ' + str(err)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generateChallenge():
    return 21


class log_in(APIView):
    def get(self, request):
        # Return the challenge
        c = generateRandomNumber(SECP256k1)
        user = AppUser.objects.get(username='stefan')
        user.challenge_issued = hex(c)
        user.challenge_burnt = False
        user.save()
        return Response({'c': hex(c)}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        return performAuth(data)
