# from django.db.models import Sum

# from donation.models import MemberAccountLog


# def calculate_total_amount(user):
#     debit_amount_sum = MemberAccountLog.objects.filter(
#         user=user).aggregate(Sum('debit_amount'))['debit_amount__sum'] or 0
#     credit_amount_sum = MemberAccountLog.objects.filter(
#         user=user).aggregate(Sum('credit_amount'))['credit_amount__sum'] or 0
#     return credit_amount_sum - debit_amount_sum
