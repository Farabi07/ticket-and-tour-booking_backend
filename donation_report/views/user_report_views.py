import datetime
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from authentication.serializers import UserSerializer
from django.db.models import Q
from commons.pagination import Pagination

from donation.models import Collection
from donation.serializers import DonationSerializer, LevelSerializer, PaymentMethodSerializer
from donation_report.filters import CollectionFilter, UserFilter
from member.models import Member
from member.serializers import MemberListSerializer


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
def getUserReport(request):

    date_after = request.query_params.get('date_after')
    date_before = request.query_params.get('date_before')
    current_level = request.query_params.get('current_level')
    head_user = request.query_params.get('head_user')
    members = Member.objects.all()
    if date_after:
        members = members.filter(created_at__date__gte=date_after)
    if date_before:
        members = members.filter(created_at__date__lte=date_before)
    if current_level:
        members = members.filter(current_level=current_level)
    if head_user:
        members = members.filter(head_user__id=head_user)
        level_one = members.filter(head_user=head_user)
        level_two = members.filter(head_user__in=level_one)
    total_elements = members.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    members = pagination.paginate_data(members)

    serializer = MemberListSerializer(members, many=True)

    response = {
        'members': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
def getUserReportWithoutPagination(request):

    date_after = request.query_params.get('date_after')
    date_before = request.query_params.get('date_before')
    current_level = request.query_params.get('current_level')
    head_user = request.query_params.get('head_user')
    members = Member.objects.all()
    if date_after:
        members = members.filter(created_at__date__gte=date_after)
    if date_before:
        members = members.filter(created_at__date__lt=date_before)
    if current_level:
        members = members.filter(current_level=current_level)
    if head_user:
        members = members.filter(head_user__in=head_user)

    serializer = MemberListSerializer(members, many=True)

    response = {
        'members': serializer.data,

    }

    return Response(response, status=status.HTTP_200_OK)
