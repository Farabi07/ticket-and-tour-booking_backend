import hashlib
import os
import random
import string
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from donation.models import Cause, Collection, Gift, Level, MemberAccountLog, PaymentMethod, PaymentMethodDetail
from commons.pagination import Pagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from donation.serializers import CollectionListSerializer, CollectionSerializer
import datetime
from django.contrib.auth.hashers import make_password
from sequences import get_next_value
from decimal import Decimal
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from member.models import Member
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models import Count


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CollectionSerializer,
    responses=CollectionSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_LIST.name])
def getAllCollection(request):
    collections = Collection.objects.all()
    total_elements = collections.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    collections = pagination.paginate_data(collections)

    serializer = CollectionListSerializer(collections, many=True)

    response = {
        'collections': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=CollectionSerializer, responses=CollectionSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCollectionWithoutPagination(request):
    collections = Collection.objects.all()
    print('collections: ', collections)

    serializer = CollectionSerializer(collections, many=True)

    response = {
        'collections': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=CollectionSerializer, responses=CollectionSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DETAILS.name])
def getACollection(request, pk):
    try:
        collection = Collection.objects.get(pk=pk)
        serializer = CollectionListSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Collection id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CollectionSerializer, responses=CollectionSerializer)
@api_view(['POST'])
def createCollection(request):
    data = request.data
    print("data:", data)
    filtered_data = {}
    restricted_values = ('', ' ', 0, '0', 'undefined')
    member_obj = None

    for key, value in data.items():
        if value not in restricted_values:
            filtered_data[key] = value

    first_name = filtered_data.get("first_name", '')
    father_name = filtered_data.get("father_name", '')
    mother_name = filtered_data.get("mother_name", '')
    username = filtered_data.get("username", '')
    nid_no = filtered_data.get("nid_no", '')
    amount = Decimal(filtered_data.get('amount', 0))
    payment_method_id = filtered_data.get("payment_method", None)
    password = filtered_data.get("password")
    confirm_password = filtered_data.get("confirmPassword")
    phone_number = filtered_data.get("primary_phone", '')
    country_code1 = filtered_data.get("country_code1", '')
    full_number = country_code1 + phone_number
    refer_id = filtered_data.get('refer_id', None)
    card_holder = filtered_data.get('card_holder', '')
    card_number = filtered_data.get('card_number', '')
    cvc_code = filtered_data.get('cvc_code', '')
    expiry_date = filtered_data.get('expiry_date', '')
    payment_number = filtered_data.get('payment_number', '')
    offline = filtered_data.get('offline', '')
    image = filtered_data.get('image', '')
    email = filtered_data.get('email', None)
    address = filtered_data.get('address', '')
    # Invoice generate

    current_date = datetime.date.today()
    current_date = str(current_date)
    current_date = current_date.replace('-', '')
    cv_current_date = 'CV' + current_date
    _num = get_next_value(cv_current_date)
    invoice = 'CV' + current_date + '00' + str(_num)

    member_refer_id = "RID" + str(random.randint(1000, 5000))
    filtered_data['refer_id'] = member_refer_id

    random_number = "".join([random.choice(string.digits) for _ in range(6)])
    re_password = make_password(random_number)
    filtered_data['password'] = re_password

    # Auto Email create
    if email is None:
        email_rand = ''.join(random.choices(string.ascii_lowercase, k=10))
        domain = ''.join(random.choices(
            string.ascii_lowercase, k=0)) + 'gmail.com'
        email = email_rand + '@' + domain
        filtered_data['email'] = email

    # Auto User name create
    random_number = "".join(
        [random.choice(string.digits) for _ in range(4)])
    new_username = f"{first_name}_{random_number}"
    username = new_username.lower()
    filtered_data['username'] = username

    head_user_count = 0
    user_current_level = None
    current_date = datetime.date.today()

    if refer_id:
        head_user_objs = User.objects.filter(refer_id=refer_id)
        head_user_objs = head_user_objs[0]
    else:
        head_user_objs = None

    all_user = User.objects.all()
    gifts = Gift.objects.all()
    bonus_amount = 0
    for user in all_user:
        current_level = user.current_level
        if current_level == 3:
            for gift in gifts:
                if gift.level == current_level:
                    bonus_amount = gift.amount
        if current_level == 4:
            for gift in gifts:
                if gift.level == current_level:
                    bonus_amount = gift.amount
        if current_level == 5:
            for gift in gifts:
                if gift.level == current_level:
                    bonus_amount = gift.amount
    total_amount = 0
    # member create here
    member_obj = Member.objects.create_user(
        first_name=first_name, last_name="", email=email, password=password)
    member_obj.father_name = father_name
    member_obj.mother_name = mother_name
    member_obj.username = username
    member_obj.nid = nid_no
    member_obj.image = image
    member_obj.street_address_one = address
    member_obj.confirm_password = confirm_password
    member_obj.primary_phone = full_number
    member_obj.head_user = head_user_objs
    member_obj.refer_id = member_refer_id
    member_obj.current_level = user_current_level
    member_obj.refferd_users = head_user_count
    member_obj.collection_amount = amount
    member_obj.bonus_amount = bonus_amount
    member_obj.total_amount = total_amount
    member_obj.save()

    # reffferd user count here
    if refer_id:
        members_reffered_user = User.objects.filter(
            email=head_user_objs)
        previous_refer_users = members_reffered_user[
            0].refferd_users if members_reffered_user[0].refferd_users else 0

        members_reffered_user = User.objects.filter(
            email=head_user_objs).update(refferd_users=previous_refer_users+1)
    # current level work here
    all_levels = Level.objects.all()
    members_refferd_users = 0
    user_obj = None
    try:
        user_obj = User.objects.get(email=member_obj.head_user)
        members_refferd_users = user_obj.refferd_users
    except User.DoesNotExist:
        print("User does not exist")
        # user_obj = User.objects.get(email=member_obj.head_user)

    previous_level_quantity = 1

    for level in all_levels:
        level_quantity = level.quantity
        if members_refferd_users is not None and previous_level_quantity is not None and level_quantity is not None:
            if int(members_refferd_users) >= int(previous_level_quantity) and int(members_refferd_users) <= int(level_quantity) and int(members_refferd_users) > 0:
                user_obj.current_level = level
                user_obj.save()
                previous_level_quantity = level_quantity
        else:
            break
    # end
    payment_method_obj = PaymentMethod.objects.get(id=payment_method_id)
    payment_method_detail_obj = PaymentMethodDetail.objects.create(payment_method=payment_method_obj, member=member_obj,
                                                                   offline=offline, card_number=card_number, card_holder=card_holder,
                                                                   cvc_code=cvc_code, expiry_date=expiry_date, payment_number=payment_number)
    collection_obj = Collection.objects.create(
        user=member_obj, payment_method=payment_method_obj, payment_method_detail=payment_method_detail_obj, amount=amount, date=current_date, invoice_no=invoice)

    serializer = CollectionSerializer(collection_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
    # tree wise user level amount store in member account log table
    specific_user_id = 442
    user_id = None
    try:
        user_id = Member.objects.get(id=specific_user_id)
    except Member.DoesNotExist:
        print(f"User with email does not exist")
    debit_amount = 0
    level = 1
    head_user = head_user_objs
    amount = 0
    dynamic_level_name = ""
    user_refer_id = refer_id

    try:
        if user_refer_id or user_id.id != specific_user_id:
            while level <= 5 and head_user.id != specific_user_id:
                if level == 1:
                    dynamic_level_name = "Level 1"
                if level == 2:
                    dynamic_level_name = "Level 2"
                if level == 3:
                    dynamic_level_name = "Level 3"
                if level == 4:
                    dynamic_level_name = "Level 4"
                if level == 5:
                    dynamic_level_name = "Level 5"

                dynamic_level = Level.objects.filter(name=dynamic_level_name)
                amount = dynamic_level[0].commission_amount
                if head_user:
                    MemberAccountLog.objects.create(
                        user=head_user, date=current_date, payment_method=payment_method_obj, debit_amount=debit_amount, credit_amount=amount)

                    level = level + 1
                    head_user = head_user.head_user
                    print('head_user: ', head_user)

    except AttributeError as e:
        # Handle attribute error
        print(f"Attribute error occurred: {e}")

    except NameError as e:
        # Handle name error
        print(f"Name error occurred: {e}")

    except Exception as e:
        # Handle any other exception
        print(f"An error occurred: {e}")

# Our special Owner  work

    try:
        specific_user = Member.objects.get(id=specific_user_id)
        credit_amount = round(0.1 * 5100, 2)
        MemberAccountLog.objects.create(
            user=specific_user,
            date=current_date,
            payment_method=payment_method_obj,
            credit_amount=credit_amount,
            debit_amount=0
        )
    except Member.DoesNotExist:
        print(f"User with email {specific_user_id} does not exist")
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(request=CollectionSerializer, responses=CollectionSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_UPDATE.name])
def updateCollection(request, pk):
    data = request.data
    print('data: ', data)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0' and value != 'undefined':
            filtered_data[key] = value
    image = filtered_data.get('image', None)
    if type(image) == str and image is not None:
        poped_image = filtered_data.pop('image')
    try:
        collection = Collection.objects.get(pk=pk)

        serializer = Collection(collection, data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"Collection id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CollectionSerializer, responses=CollectionSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PAYMENT_METHOD_DELETE.name])
def deleteCollection(request, pk):
    try:
        collection = Collection.objects.get(pk=pk)
        collection.delete()
        return Response({'detail': f'collection id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"collection id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
