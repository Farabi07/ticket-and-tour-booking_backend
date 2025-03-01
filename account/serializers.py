from django.apps import apps
from django.db.models import fields

from rest_framework import serializers

from rest_framework_recursive.fields import RecursiveField

from django_currentuser.middleware import get_current_authenticated_user

from account.models import *
from authentication.serializers import AdminUserMinimalListSerializer, BranchMinimalListSerializer






class PrimaryGroupListSerializer(serializers.ModelSerializer):
	created_by = serializers.SerializerMethodField(read_only=True)
	updated_by = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = PrimaryGroup
		fields = '__all__'
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_created_by(self, obj):
		return obj.created_by.email if obj.created_by else obj.created_by
		
	def get_updated_by(self, obj):
		return obj.updated_by.email if obj.updated_by else obj.updated_by




class PrimaryGroupMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = PrimaryGroup
		fields = ['id', 'name']




class PrimaryGroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = PrimaryGroup
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class GroupMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ['id', 'name']




class GroupListSerializer(serializers.ModelSerializer):
	head_group = GroupMinimalListSerializer()
	head_primarygroup = PrimaryGroupMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = Group
		fields = '__all__'
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class GroupTreeSerializer(serializers.ModelSerializer):
	children = RecursiveField(many=True)
	class Meta:
		model = Group
		fields = ['id', 'name', 'children']




class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class LedgerAccountListSerializer(serializers.ModelSerializer):
	head_group = GroupMinimalListSerializer()
	head_primarygroup = PrimaryGroupMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = LedgerAccount
		fields = '__all__'
		ordering = ('-id')
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class LedgerAccountMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = LedgerAccount
		fields = ['id', 'name']




class LedgerAccountSerializer(serializers.ModelSerializer):
	class Meta:
		model = LedgerAccount
		fields = '__all__'
		ordering = ('-id')
		extra_kwargs = {
			'ledger_type':{
				'read_only': True,
			},
			'reference_id':{
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}
	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class SubLedgerAccountListSerializer(serializers.ModelSerializer):
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = SubLedgerAccount
		fields = '__all__'
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class SubLedgerAccountMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubLedgerAccount
		fields = ['id', 'name']




class SubLedgerAccountSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubLedgerAccount
		fields = '__all__'
	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject





class PaymentVoucherListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = PaymentVoucher
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_created_by(self, obj):
		return obj.created_by.email if obj.created_by else obj.created_by
		
	def get_updated_by(self, obj):
		return obj.updated_by.email if obj.updated_by else obj.updated_by




class PaymentVoucherListCustomSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()

	amount = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = PaymentVoucher
		fields = ['id', 'invoice_no', 'branch', 'ledger', 'sub_ledger', 'amount', 'payment_date', 'details', 'created_at', 'updated_at', 'created_by', 'updated_by']
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_created_by(self, obj):
		return obj.created_by.email if obj.created_by else obj.created_by
		
	def get_updated_by(self, obj):
		return obj.updated_by.email if obj.updated_by else obj.updated_by

	def get_amount(self, obj):
		invoice = obj.invoice_no
		total = sum(PaymentVoucher.objects.filter(invoice_no=invoice).values_list('credit_amount', flat=True))
		return total if obj.invoice_no else 0




class PaymentVoucherMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = PaymentVoucher
		fields = ['id', 'invoice_no']


		

class PaymentVoucherSerializer(serializers.ModelSerializer):
	class Meta:
		model = PaymentVoucher
		fields = '__all__'
		
	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class ReceiptVoucherListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = ReceiptVoucher
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class ReceiptVoucherListCustomSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()

	amount = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = ReceiptVoucher
		fields = ['id', 'invoice_no', 'branch', 'ledger', 'sub_ledger', 'amount', 'receipt_date', 'details', 'created_at', 'updated_at', 'created_by', 'updated_by']
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_amount(self, obj):
		invoice = obj.invoice_no
		total = sum(ReceiptVoucher.objects.filter(invoice_no=invoice).values_list('debit_amount', flat=True))
		return total if obj.invoice_no else 0




class ReceiptVoucherMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = ReceiptVoucher
		fields = ['id', 'invoice_no']




class ReceiptVoucherSerializer(serializers.ModelSerializer):
	class Meta:
		model = ReceiptVoucher
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class SalesListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = Sales
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class SalesListCustomSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()

	amount = serializers.SerializerMethodField()
	class Meta:
		model = Sales
		fields = ['id', 'invoice_no', 'branch', 'ledger', 'sub_ledger', 'amount', 'sales_date', 'details', 'created_at', 'updated_at', 'created_by', 'updated_by']
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_amount(self, obj):
		invoice = obj.invoice_no
		total = sum(Sales.objects.filter(invoice_no=invoice).values_list('credit_amount', flat=True))
		return total if obj.invoice_no else 0




class SalesMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Sales
		fields = ['id', 'invoice_no']




class SalesSerializer(serializers.ModelSerializer):
	class Meta:
		model = Sales
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class PurchaseListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = Purchase
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class PurchaseListCustomSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()

	amount = serializers.SerializerMethodField()
	class Meta:
		model = Purchase
		fields = ['id', 'invoice_no', 'branch', 'ledger', 'sub_ledger', 'amount', 'purchase_date', 'details', 'created_at', 'updated_at', 'created_by', 'updated_by']
		extra_kwargs = {
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_amount(self, obj):
		invoice = obj.invoice_no
		total = sum(Purchase.objects.filter(invoice_no=invoice).values_list('debit_amount', flat=True))
		return total if obj.invoice_no else 0




class PurchaseMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Purchase
		fields = ['id', 'invoice_no']




class PurchaseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Purchase
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class ContraListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = Contra
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class ContraListCustomSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()

	amount = serializers.SerializerMethodField()
	class Meta:
		model = Contra
		fields = ['id', 'invoice_no', 'branch', 'ledger', 'amount', 'contra_date', 'details', 'created_at', 'updated_at', 'created_by', 'updated_by']
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_amount(self, obj):
		invoice = obj.invoice_no
		total = sum(Contra.objects.filter(invoice_no=invoice).values_list('credit_amount', flat=True))
		return total if obj.invoice_no else 0





class ContraMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Contra
		fields = ['id', 'invoice_no']




class ContraSerializer(serializers.ModelSerializer):
	class Meta:
		model = Contra
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class JournalListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = Journal
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class JournalListCustomSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()

	amount = serializers.SerializerMethodField()
	class Meta:
		model = Journal
		fields = ['id', 'invoice_no', 'branch', 'ledger', 'amount', 'journal_date', 'details', 'created_at', 'updated_at', 'created_by', 'updated_by']
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}

	def get_amount(self, obj):
		invoice = obj.invoice_no
		total = sum(Journal.objects.filter(invoice_no=invoice).values_list('credit_amount', flat=True))
		return total if obj.invoice_no else 0




class JournalMinimalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Journal
		fields = ['id', 'invoice_no']




class JournalSerializer(serializers.ModelSerializer):
	class Meta:
		model = Journal
		fields = '__all__'

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class IDJournalListSerializer(serializers.ModelSerializer):
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = IDJournal
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
			'created_at':{
				'read_only': True,
			},
			'updated_at':{
				'read_only': True,
			},
			'created_by':{
				'read_only': True,
			},
			'updated_by':{
				'read_only': True,
			},
		}




class IDJournalListSerializer(serializers.ModelSerializer):
	class Meta:
		model = IDJournal
		fields = ['id', 'invoice_no']




class IDJournalSerializer(serializers.ModelSerializer):
	class Meta:
		model = IDJournal
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
		}

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject




class AccountLogListSerializer(serializers.ModelSerializer):
	ledger = LedgerAccountMinimalListSerializer()
	sub_ledger = SubLedgerAccountMinimalListSerializer()
	branch = BranchMinimalListSerializer()
	created_by = AdminUserMinimalListSerializer()
	updated_by = AdminUserMinimalListSerializer()
	class Meta:
		model = AccountLog
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
		}

	def get_created_by(self, obj):
		return obj.created_by.email if obj.created_by else obj.created_by
		
	def get_updated_by(self, obj):
		return obj.updated_by.email if obj.updated_by else obj.updated_by




class AccountLogSerializer(serializers.ModelSerializer):
	class Meta:
		model = AccountLog
		fields = '__all__'
		extra_kwargs = {
			'invoice_no': {
				'read_only': True,
			},
		}

	def create(self, validated_data):
		modelObject = super().create(validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.created_by = user
		modelObject.save()
		return modelObject
	
	def update(self, instance, validated_data):
		modelObject = super().update(instance=instance, validated_data=validated_data)
		user = get_current_authenticated_user()
		if user is not None:
			modelObject.updated_by = user
		modelObject.save()
		return modelObject
	




