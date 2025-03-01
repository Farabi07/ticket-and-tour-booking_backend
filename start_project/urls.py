"""start_project URL Configuration."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView)

from . import views
admin.site.site_header = "BLUEBAY IT LIMITED"
admin.site.index_title = "Welcome to Bus Booking Syestem"
admin.site.site_title = "Welcome to Bus Booking Syestem"

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index),
    # path('silk/', include('silk.urls', namespace='silk')),

    # Authentication module
    path('user/', include('authentication.urls.user_urls')),
    path('employee/', include('authentication.urls.employee_urls')),
    path('vendor/', include('authentication.urls.vendor_urls')),
    path('customer_type/', include('authentication.urls.customer_type_urls')),
    path('customer/', include('authentication.urls.customer_urls')),
    path('permission/', include('authentication.urls.permission_urls')),
    path('role/', include('authentication.urls.role_urls')),
    path('designation/', include('authentication.urls.designation_urls')),
    path('department/', include('authentication.urls.department_urls')),
    path('qualification/', include('authentication.urls.qualification_urls')),

    path('country/', include('authentication.urls.country_urls')),
    path('thana/', include('authentication.urls.thana_urls')),
    path('area/', include('authentication.urls.area_urls')),
    path('branch/', include('authentication.urls.branch_urls')),
    path('city/', include('authentication.urls.city_urls')),

    # CMS
    path('cms_menu/', include('cms.urls.cms_menu_urls')),
    path('cms_menu_content/', include('cms.urls.cms_menu_content_urls')),
    path('cms_menu_content_image/',include('cms.urls.cms_menu_content_image_urls')),

	# tour
	path('tour_content/', include('tour.urls.tour_content_urls')),
	path('tour_content_image/', include('tour.urls.tour_content_image_urls')),
    path('tour_booking/', include('tour.urls.tour_booking_urls')),
   
   # Member
    path('member/', include('member.urls.member_urls')),
    path('promoter/', include('member.urls.promoter_urls')),

    #BBMS
    path('bus/', include('bbms.urls.bus_urls')), 
    path('bus_booking/', include('bbms.urls.bus_booking_urls')), 
    path('passenger/', include('bbms.urls.passenger_urls')), 
    path('booking_summery/', include('bbms.urls.booking_summery_urls')), 
    path('available_dates/', include('bbms.urls.available_dates_urls')), 

    # Payment System
    path('payments/', include('payments.urls.payments_urls')),

    # Support module
    path('ticket_department/', include('support.urls.ticket_department_urls')),
    path('ticket_priority/', include('support.urls.ticket_priority_urls')),
    path('ticket_status/', include('support.urls.ticket_status_urls')),
    path('ticket/', include('support.urls.ticket_urls')),
    path('ticket_detail/', include('support.urls.ticket_detail_urls')),

    path('message/', include('support.urls.message_urls')),

    path('task_type/', include('support.urls.task_type_urls')),
    path('todo_task/', include('support.urls.todo_task_urls')),


    # SITE SETTINGS
    path('homepage_slider/', include('site_settings.urls.homepage_slider_urls')),
    path('contact_setting/', include('site_settings.urls.contact_urls')),
    path('subscription_setting/', include('site_settings.urls.contact_urls')),
    path('general_setting/', include('site_settings.urls.general_setting_urls')),
    path('menu_item_setting/', include('site_settings.urls.menu_item_urls')),
    path('role_menu_setting/', include('site_settings.urls.role_menu_urls')),


    # YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('djoser/auth/', include('djoser.urls')),
    path('djoser/auth/', include('djoser.urls.jwt')),

    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),
]
