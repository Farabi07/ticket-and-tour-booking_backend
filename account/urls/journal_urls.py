
from django.urls import path
from account.views import journal_views as views


urlpatterns = [
	path('api/v1/journal/all/', views.getAllJournal),

	path('api/v1/journal/journal_by_invoice_no/<str:invoice_no>', views.getAllJournalByInvoiceNo),

	path('api/v1/journal/<int:pk>', views.getAJournal),

	path('api/v1/journal/search/', views.searchJournal),

	path('api/v1/journal/create/', views.createJournal),

	path('api/v1/journal/update/', views.updateJournal),
	
	path('api/v1/journal/delete/<int:pk>', views.deleteJournal),

	path('api/v1/journal/delete_multiple/', views.deleteMultipleJournal),

]