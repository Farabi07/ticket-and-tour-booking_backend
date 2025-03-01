import this
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from sequences import get_next_value

from authentication.decorators import has_permissions

from account.models import AccountLog, Group, LedgerAccount, Sales, SubLedgerAccount
from authentication.serializers import AdminUserMinimalListSerializer

from donation.models import Cause, CauseContent, Donation
from donation.serializers import CauseSerializer, CauseListSerializer, CauseMinimalSerializer

from utils.login_logout import get_all_logged_in_users

from commons.pagination import Pagination
from commons.enums import PermissionEnum

from decimal import Decimal
import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CauseSerializer,
    responses=CauseListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCause(request):
    causes = Cause.objects.all()
    print('causes: ', causes)

    total_elements = causes.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    causes = pagination.paginate_data(causes)

    serializer = CauseListSerializer(causes, many=True)

    response = {
        'causes': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CauseSerializer,
    responses=CauseListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseWithoutPagination(request):
    causes = Cause.objects.all()
    print('causes: ', causes)

    serializer = CauseMinimalSerializer(causes, many=True)

    response = {
        'causes': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=CauseSerializer,
    responses=CauseListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCauseContentAndImageByCauseId(request, cause_id):
    # menu_items = TourContent.objects.filter(cms_menu=cms_menu_id)
    with connection.cursor() as cursor:
        cursor.execute('''
						select 
							cause_id AS cause,
							json_object_agg(name, value) AS data
							from donation_causecontent where cause_id=%s
							group by cause_id
							order by cause_id;
						''', [cause_id])
        content_row = cursor.fetchone()
        print('content_row: ', content_row)
        print('content_row type: ', type(content_row))

    cause_contents = content_row[1]

    with connection.cursor() as cursor:
        cursor.execute('''
			select
			json_object_agg(
				head,
				case
				when array_length(image,1)=1 then to_json(image[1])
				else to_json(image)
				end)
			from (
			select head, array_agg(image) as image
			from donation_causecontentimage where cause_id=%s
			group by head) as x;
						''', [cause_id])
        image_row = cursor.fetchall()
        print('image_row: ', image_row)
        print('image_row type: ', type(image_row))

    content_images = image_row[0]

    response = {
        'cause_contents': cause_contents,
        'content_images': content_images,

    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=CauseSerializer, responses=CauseSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getACause(request, pk):
    try:
        cause = Cause.objects.get(pk=pk)
        serializer = CauseMinimalSerializer(cause)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Cause id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CauseSerializer, responses=CauseSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createCause(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)
    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)
    str_current_datetime = str(timezone.now())

    current_date = str(datetime.date.today())
    current_date = current_date.replace('-', '')
    pv_current_date = 'SA' + current_date
    print('current_date: ', current_date, type(current_date))

    serializer = CauseSerializer(data=filtered_data)

    if serializer.is_valid():
        serializer.save()

        try:
            group_obj = Group.objects.get(name='Sundrey Debtors')
        except Group.DoesNotExist:
            group_obj = None

        id = serializer.data['id']
        name = serializer.data['name']
        cause_ledger = LedgerAccount.objects.create(
            name=name, reference_id=id, head_group=group_obj, ledger_type='cause_ledger'
        )

        goal_amount = Decimal(filtered_data['goal_amount'], None)
        _num = get_next_value(pv_current_date)
        print('get_next_value: ', _num)

        invoice = 'PV' + current_date + '00' + str(_num)
        print('invoice: ', invoice)

        cause_subledger, created = SubLedgerAccount.objects.get_or_create(name='cause')

        try:
            company_sales_ledger = LedgerAccount.objects.get(name='Company Sales')
        except LedgerAccount.DoesNotExist:
            company_sales_ledger = LedgerAccount.objects.create(name='Company Sales')  

        sales = Sales(
            ledger=cause_ledger if cause_ledger else None,
            sub_ledger=cause_subledger,
            invoice_no=invoice,
            debit_amount=goal_amount,
            sales_date=str_current_datetime
        )
        sales.full_clean()  # Validate the model instance
        sales.save()

        company_sales = Sales(
            ledger=company_sales_ledger,
            sub_ledger=cause_subledger,
            invoice_no=invoice,
            credit_amount=goal_amount,
            sales_date=str_current_datetime
        )
        company_sales.full_clean()  # Validate the model instance
        company_sales.save()

        AccountLog.objects.create(
            ledger=cause_ledger if cause_ledger else None,
            sub_ledger=cause_subledger,
            reference_no=invoice,
            log_type='sales',
            debit_amount=goal_amount,
            log_date=str_current_datetime
        )
        AccountLog.objects.create(
            ledger=company_sales_ledger,
            sub_ledger=cause_subledger,
            reference_no=invoice,
            log_type='sales',
            credit_amount=goal_amount,
            log_date=str_current_datetime
        )


        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CauseSerializer, responses=CauseSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
def updateCause(request, pk):
    data = request.data
    print('dataa :', data)
    filtered_data = {}

    try:
        cause_obj = Cause.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Product id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    image = filtered_data.get('image', None)

    if image is not None and type(image) == str:
        popped_logo = filtered_data.pop('image')

    serializer = CauseSerializer(cause_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)


@extend_schema(request=CauseSerializer, responses=CauseSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteCause(request, pk):
    try:
        cause = Cause.objects.get(pk=pk)
        cause.delete()
        return Response({'detail': f'Cause id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Cause id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)
