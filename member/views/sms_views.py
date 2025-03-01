# import requests
# from drf_spectacular.utils import extend_schema
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

# import member
# from member.models import Member
# from member.serializers import MemberSerializer
# from member.utils import sendSms


# @extend_schema(request=MemberSerializer, responses=MemberSerializer)
# @api_view(['POST'])
# def sendSmsToMembers(request):
#     data = request.data
#     print('data: ', data)
#     member_string = data.get('receivers', '')
#     print('member_string: ', member_string)
#     adviser_member = data.get('adviser_member', False)
#     executive_member = data.get('executive_member', False)
#     general_member = data.get('general_member', False)
#     life_member = data.get('life_member', False)
#     message = data.get('message', '')
#     member_list = member_string.split(",")
#     print('member_list: ', member_list)
#     if member_string != '' and len(member_list) > 0:

#         for mobile in member_list:
#             sendSms(mobile, message)
#         return Response("SMS Sent Successfully!")
#     else:
#         if adviser_member is True:
#             adviser_numbers = [adviser_member.member.primary_phone for adviser_member in AdviserMember.objects.all()]
#             for a_number in adviser_numbers:
#                 a_number = str(a_number)[-11:]
#                 print('adviser_number:', a_number)
#                 sendSms(a_number, message)
#         if executive_member is True:
#             executive_numbers = [executive_member.member.primary_phone for executive_member in ExecutiveMember.objects.all()]

#             for e_number in executive_numbers:
#                 e_number = str(e_number)[-11:]
#                 print('executive_number:', e_number)
#                 sendSms(e_number, message)

#         if general_member is True:
#             general_numbers = [general_member.member.primary_phone for general_member in GeneralMember.objects.all()]
#             for g_number in general_numbers:
#                 g_number = str(g_number)[-11:]
#                 print(g_number)
#                 sendSms(g_number, message)

#         if life_member is True:
#             life_numbers = [life_member.member.primary_phone for life_member in LifeMember.objects.all()]
#             for l_number in life_numbers:
#                 l_number = str(l_number)[-11:]
#                 print(l_number)
#                 sendSms(l_number, message)

#         return Response("message to random people under construction")
