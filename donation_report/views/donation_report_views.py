from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from commons.pagination import Pagination
from donation.filters import DonationFilter
from donation.models import Donation, Cause
from donation.serializers import DonationSerializer, DonationListSerializer


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    request=DonationSerializer,
    responses=DonationSerializer
)
@api_view(['GET'])
def getDonationReport(request):
    donation_reports = DonationFilter(request.GET, queryset=Donation.objects.all())
    donation_reports = donation_reports.qs
    total_elements = donation_reports.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    donation_reports = pagination.paginate_data(donation_reports)
    print('donation_reports: ', donation_reports)

    response_list = []
    if len(donation_reports) > 0:
        for donation_report in donation_reports:
            donation_report_dict = {}
            cause_id = donation_report.cause
            print('cause_id', cause_id)
            donation_report_serializer = DonationListSerializer(donation_report)
            for key, value in donation_report_serializer.data.items():
                donation_report_dict[key] = value
            response_list.append(donation_report_dict)

    response = {
        'donation_reports': response_list,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)


@extend_schema(request=DonationSerializer, responses=DonationSerializer)
@api_view(['GET'])
def getADonationReport(request, cause_id):
    try:
        donation = Donation.objects.get(cause=cause_id)
        serializer = DonationListSerializer(donation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Donation id - {cause_id} does't exists"}, status=status.HTTP_400_BAD_REQUEST)

