import os
from datetime import timedelta

import ecdsa as ecdsa
from django.utils import timezone
from ecdsa import SECP256k1
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from e_vote_backend.email_templates import format_otp_email, otp_message
from e_vote_backend.emails import send_email
from e_vote_backend.models import AppUser, Otp
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


def generateOTP(user):
    try:
        # TODO: Use standard TOTP https://datatracker.ietf.org/doc/html/rfc6238#section-4.1
        generated_otp_value = 234561
        try:
            # Get the last created OTP if it exists
            otp = Otp.objects.get(user=user)
            otp.delete()
        except Otp.DoesNotExist:
            pass
        # TODO: Hash the OTP
        otp = Otp(user=user, otp=generated_otp_value)
        format_otp_email(user.username, generated_otp_value)
        send_email(receiver_email=user.email, message=otp_message)

        otp.save()
        return 0
    except Exception as e:
        print(e)
        return -1


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

            # MFA: OTP generation and sending

            not_found = False
            try:
                # Get the last created OTP if it exists
                registered_otp = Otp.objects.get(user=user)
            except Otp.DoesNotExist:
                registered_otp = None
                not_found = True

            # Only if the OTP was not verified yet
            # Or if the OTP was invalidated for some reason
            # Generate another OTP or a brand new one
            if (not_found or registered_otp.valid is False
                    or registered_otp.generation_date < (timezone.now() - timedelta(minutes=30))):
                if generateOTP(user) == 0:
                    return Response({'data': 'OTP sent', 'otp': '1'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({'data': 'Error sending OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                if registered_otp.verified is False and registered_otp.valid is True:
                    if return_user:
                        return Response({'data': 'OTP already sent', 'otp': '1'},
                                        status=status.HTTP_401_UNAUTHORIZED), user
                    else:
                        return Response({'data': 'OTP already sent', 'otp': '1'}, status=status.HTTP_401_UNAUTHORIZED)
                # The OTP was already verified and is valid and it has not expired
                if (registered_otp.verified is True and registered_otp.valid is True
                        and registered_otp.generation_date >= (timezone.now() - timedelta(minutes=30))):
                    if return_user:
                        return Response({'data': 'OK'}, status=status.HTTP_200_OK), user
                    else:
                        return Response({'data': 'OK'}, status=status.HTTP_200_OK)
                else:
                    # OTP is not valid or expired
                    if return_user:
                        return Response({'data': 'OTP not valid or expired!', 'otp': '-1'},
                                        status=status.HTTP_401_UNAUTHORIZED), user
                    else:
                        return Response({'data': 'OTP not valid or expired!', 'otp': '-1'},
                                        status=status.HTTP_401_UNAUTHORIZED)

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


class otp(APIView):
    def post(self, request):
        try:
            data = request.data
            otp = data['otp']

            if auth_validator['otp']["inputNull"] is False and (not otp):
                return Response({'OK': False, 'data': 'OTP is missing!'},
                                status=status.HTTP_400_BAD_REQUEST)

            username = data['username']
            # TODO: Validate the username

            try:
                user = AppUser.objects.get(username=username)
            except AppUser.DoesNotExist:
                return Response({'data': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user = AppUser.objects.get(username=username)

            try:
                # Get the last created OTP if it exists
                registered_otp = Otp.objects.get(user=user)
            except Otp.DoesNotExist:
                # Impossible, as the user should have requested an OTP before, when he / she
                # requested the authentication
                return Response({'data': 'OTP mismatch!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # If the OTP was not verified yet
            if registered_otp.verified is False:
                if otp == registered_otp.otp:
                    # OTP was verified
                    registered_otp.verified = True
                    registered_otp.save()
                    # Tell the client to request the authentication AGAIN!
                    # This is to prevent cases where only the OTP verification
                    # Could unexpectedly log the user in with no prior NIZKP verification
                    return Response({'data': 'OK!'}, status=status.HTTP_200_OK)
                else:
                    # OTP was not verified
                    registered_otp.verified = False
                    registered_otp.save()
                    return Response({'data': 'Incorrect OTP provided!'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # Could be a replay attack here, so just invalidate the OTP and
                # tell the client to request the authentication AGAIN!
                registered_otp.verified = False
                registered_otp.valid = False
                registered_otp.save()
                # TODO: log possible replay attack
                return Response({'data': 'OTP already verified!'}, status=status.HTTP_401_UNAUTHORIZED)


        except Exception as e:
            print(e)
            return Response({'data': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
