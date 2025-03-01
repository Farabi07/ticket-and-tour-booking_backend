	
    
    
def __str__(self):
    full_path = [self.name]
    k = self.parent
    while k is not None:
        full_path.append(k.name)
        k = k.parent
    return ' -> '.join(full_path[::-1])



# def recursive(arr_of_objs):
#     for obj in arr_of_objs:
#         ledgers = LedgerAccount.objects.filter(head_group=obj['id'])
#         if len(ledgers) > 0:
#             account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers).values_list('debit_amount', flat=True)
#             total = sum(account_log_dr_list)
#             response_dict['assets'][new_group['name']] += total
#         groups = obj['children']
#         if len(groups) > 0:
#             recursive(groups)




# def getTrialBalance2(request):
#     start_date = request.query_params.get('start_date', None)    
#     end_date = request.query_params.get('end_date', None)    
#     response_dict = {}
#     groups_under_pg_assets = Group.objects.filter(head_primarygroup__name='Assets')
#     print('groups_under_pg_assets: ', groups_under_pg_assets)

#     for group in groups_under_pg_assets:
#         assets_dict = {}
#         hash_map = []
#         done = []
#         undone = []
#         assets_dict[group.name] = 0
#         ledgers = LedgerAccount.objects.filter(head_group=group)
#         if len(ledgers) > 0:
#             account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers).values_list('debit_amount', flat=True)
#             total = sum(account_log_dr_list)
#             assets_dict[group.name] += decimal(total)
#         groups = Group.objects.filter(head_group=group)
#         for new_group in groups:
#             ledgers = LedgerAccount.objects.filter(head_group=new_group)
#             if len(ledgers) > 0:
#                 account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers).values_list('debit_amount', flat=True)
#                 total = sum(account_log_dr_list)
#                 assets_dict[group.name] += decimal(total)
#             groups = Group.objects.filter(head_group=new_group)
#             undone.extend(list(groups.values_list('id', flat=True)))
#             while len(groups) > 0:
#                 for new_group in groups:
#                     if new_group.id not in done:
#                         done.append(new_group.id)
#                         ledgers = LedgerAccount.objects.filter(head_group=new_group)
#                         if len(ledgers) > 0:
#                             account_log_dr_list = AccountLog.objects.filter(ledger__in=ledgers).values_list('debit_amount', flat=True)
#                             total = sum(account_log_dr_list)
#                             assets_dict[group.name] += decimal(total)
#                         groups = Group.objects.filter(head_group=new_group)

#     response = {
#         'trial_balance': response_dict,
#     }

#     return Response(response, status=status.HTTP_200_OK)






