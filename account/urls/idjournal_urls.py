
from django.urls import path
from account.views import idjournal_views as views


urlpatterns = [
	path('api/v1/idjournal/all/', views.getAllIDJournal),

	path('api/v1/idjournal/idjournal_by_invoice_no/<str:invoice_no>', views.getAllIDJournalByInvoiceNo),

	path('api/v1/idjournal/<int:pk>', views.getAIDJournal),

	path('api/v1/idjournal/search/', views.searchIDJournal),

	path('api/v1/idjournal/create/', views.createIDJournal),

	path('api/v1/idjournal/update/', views.updateIDJournal),
	
	path('api/v1/idjournal/delete/<int:pk>', views.deleteIDJournal),

	path('api/v1/idjournal/delete_multiple/', views.deleteMultipleIDJournal),

]