
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema, OpenApiParameter
import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.models import User
from donation.models import Collection, Donation, Gift, Level, MemberAccountLog
from donation.serializers import UserDetailsSerializer
from django.db.models import Sum

from member.models import Member


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getTotalAmountOfFirstLevelUser(request):
    users = User.objects.filter(current_level=1)
    print("users: ", users)
    total_amounts = []
    for user in users:
        user_amount = MemberAccountLog.objects.filter(
            user=user).aggregate(Sum('credit_amount'))
        total_amount = user_amount['credit_amount__sum'] or 0
        total_amounts.append(total_amount)

    return Response({'total_amount': sum(total_amounts)})


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getTotalAmountOfSecondLevelUser(request):
    users = User.objects.filter(current_level=2)
    print("users: ", users)
    total_amounts = []
    for user in users:
        user_amount = MemberAccountLog.objects.filter(
            user=user).aggregate(Sum('credit_amount'))
        total_amount = user_amount['credit_amount__sum'] or 0
        total_amounts.append(total_amount)

    return Response({'total_amount': sum(total_amounts)})


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getTotalAmountOfThirdLevelUser(request):
    users = User.objects.filter(current_level=3)
    print("users: ", users)
    total_amounts = []
    for user in users:
        user_amount = MemberAccountLog.objects.filter(
            user=user).aggregate(Sum('credit_amount'))
        total_amount = user_amount['credit_amount__sum'] or 0
        total_amounts.append(total_amount)

    return Response({'total_amount': sum(total_amounts)})


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getTotalAmountOfFourthLevelUser(request):
    users = User.objects.filter(current_level=4)
    print("users: ", users)
    total_amounts = []
    for user in users:
        user_amount = MemberAccountLog.objects.filter(
            user=user).aggregate(Sum('credit_amount'))
        total_amount = user_amount['credit_amount__sum'] or 0
        total_amounts.append(total_amount)

    return Response({'total_amount': sum(total_amounts)})


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getTotalAmountOfFifthLevelUser(request):
    users = User.objects.filter(current_level=5)
    print("users: ", users)
    total_amounts = []
    for user in users:
        user_amount = MemberAccountLog.objects.filter(
            user=user).aggregate(Sum('credit_amount'))
        total_amount = user_amount['credit_amount__sum'] or 0
        total_amounts.append(total_amount)

    return Response({'total_amount': sum(total_amounts)})


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getTotalCollectionAmount(request):
    total_amount = Collection.objects.aggregate(Sum('amount'))['amount__sum']
    print('Total amount:', total_amount)
    response = {
        "total_amount": total_amount
    }
    return Response(response)


# @extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
# @api_view(['GET'])
# def getThirdBonusAmount(request):
#     users = User.objects.all()
#     for user in users:
#         current_level = user.current_level
#         bonus_amount = user.bonus_amount
#         if current_level == 3:
#             bonus_amount = 6500
#         third_level_bonus = User.objects.filter(
#             bonus_amount=bonus_amount).aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
#     response = {
#         "bonus_amount": third_level_bonus
#     }
#     return Response(response)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getThirdBonusAmount(request):
    gifts = Gift.objects.all()
    users = User.objects.all()
    third_level_bonus = 0
    for user in users:
        current_level = user.current_level
        bonus_amount = user.bonus_amount
        if current_level == 3:
            for gift in gifts:
                if gift.level == current_level:
                    bonus_amount = gift.amount
                    third_level_bonus = User.objects.filter(
                        bonus_amount=bonus_amount).aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
    response = {
        "bonus_amount": third_level_bonus
    }
    return Response(response)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getFourthBonusAmount(request):
    gifts = Gift.objects.all()
    users = User.objects.all()
    fourth_level_bonus = 0
    for user in users:
        current_level = user.current_level
        bonus_amount = user.bonus_amount
        if current_level == 4:
            for gift in gifts:
                if gift.level == current_level:
                    bonus_amount = gift.amount
                    fourth_level_bonus = User.objects.filter(
                        bonus_amount=bonus_amount).aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
    response = {
        "bonus_amount": fourth_level_bonus
    }
    return Response(response)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getFifthBonusAmount(request):
    gifts = Gift.objects.all()
    users = User.objects.all()
    fifth_level_bonus = 0
    for user in users:
        current_level = user.current_level
        bonus_amount = user.bonus_amount
        if current_level == 5:
            for gift in gifts:
                if gift.level == current_level:
                    bonus_amount = gift.amount
                    fifth_level_bonus = User.objects.filter(
                        bonus_amount=bonus_amount).aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
    response = {
        "bonus_amount": fifth_level_bonus
    }
    return Response(response)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getDistributionAmount(request: requests.Request):
    http_request = HttpRequest()
    http_request.method = request.method
    http_request.headers = request.headers
    http_request.query_params = request.query_params
    http_request.data = request.data
    total_amount = 0
    total_amount += getTotalAmountOfFirstLevelUser(
        http_request).data['total_amount']
    total_amount += getTotalAmountOfSecondLevelUser(
        http_request).data['total_amount']
    total_amount += getTotalAmountOfThirdLevelUser(
        http_request).data['total_amount']
    total_amount += getTotalAmountOfFourthLevelUser(
        http_request).data['total_amount']
    total_amount += getTotalAmountOfFifthLevelUser(
        http_request).data['total_amount']
    total_amount += getThirdBonusAmount(http_request).data['bonus_amount']
    total_amount += getFourthBonusAmount(http_request).data['bonus_amount']
    total_amount += getFifthBonusAmount(http_request).data['bonus_amount']
    response = {
        "total_amount": total_amount
    }
    return Response(response)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getCurrentAmount(request: requests.Request):
    http_request = HttpRequest()
    http_request.method = request.method
    http_request.headers = request.headers
    http_request.query_params = request.query_params
    http_request.data = request.data
    current_amount = 0
    current_amount = getTotalCollectionAmount(
        http_request).data['total_amount'] - getDistributionAmount(
        http_request).data['total_amount']
    response = {
        "current_amount": current_amount
    }
    return Response(response)


@extend_schema(request=UserDetailsSerializer, responses=UserDetailsSerializer)
@api_view(['GET'])
def getUserTotalAmount(request, user_id):

    user = User.objects.get(id=user_id)

    logs = MemberAccountLog.objects.filter(user=user)

    total_amount = sum(log.credit_amount - log.debit_amount for log in logs)
    total_debit_amount = sum(log.debit_amount for log in logs)
    total_credit_amount = sum(log.credit_amount for log in logs)

    return Response({
        'total_amount': total_amount,
        "all_amount": total_credit_amount,
        "withdraw_amount": total_debit_amount

    })
