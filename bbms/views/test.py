# @extend_schema(request=BusBookingSerializer, responses=BusBookingSerializer)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def createBusBooking(request): 
#     data = request.data
#     filtered_data = {}
#     for key, value in data.items():
#         if value != '' and value != '0':
#             filtered_data[key] = value

#     seat_no = filtered_data.get('seat_no', [])
#     if not seat_no or not isinstance(seat_no, list):
#         return Response({"message": "Seat numbers must be provided as a list"}, status=status.HTTP_400_BAD_REQUEST)
    
#     seat_no_count = len(seat_no)
#     filtered_data.pop('seat_no')
#     primary_phone = filtered_data.get('primary_phone')
    
#     # Check if a passenger with the same primary_phone already exists
#     existing_passenger = Passenger.objects.filter(primary_phone=primary_phone).first()
#     if existing_passenger:
#         filtered_data['passenger'] = existing_passenger.id
#     else:
#         passenger_serializer = PassengerSerializer(data=filtered_data)
#         if passenger_serializer.is_valid():
#             passenger_instance = passenger_serializer.save()
#         else:
#             return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         filtered_data['passenger'] = passenger_instance.id

#     # Retrieve the member associated with the authenticated user
#     member_id = filtered_data.get('member')
#     if not member_id:
#         return Response({'error': 'Member ID is required'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         member = Member.objects.get(pk=member_id)
#     except Member.DoesNotExist:
#         return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

#     bus_instance = Bus.objects.get(pk=filtered_data['bus'])
#     adult_seat_count = int(filtered_data.get('adult_seat_count', 0))
#     child_seat_count = int(filtered_data.get('child_seat_count', 0))
#     youth_seat_count = int(filtered_data.get('youth_seat_count', 0))
    
#     total_seat_count = int(adult_seat_count + child_seat_count + youth_seat_count)
    
#     adult_seat_price = Decimal(bus_instance.adult_seat_price)
#     child_seat_price = Decimal(bus_instance.child_seat_price)
#     youth_seat_price = Decimal(bus_instance.youth_seat_price)
    
#     total_cost = (
#         Decimal(adult_seat_price) * adult_seat_count +
#         Decimal(child_seat_price) * child_seat_count +
#         Decimal(youth_seat_price) * youth_seat_count
#     )

#     # Calculate discounts for each category
#     adult_discount_amount = 0
#     if member.discount_type == 'percentage':
#         adult_discount_amount = (Decimal(adult_seat_price) * adult_seat_count) * (member.discount_percent / 100)
#     elif member.discount_type == 'value':
#         adult_discount_amount = member.discount_value * adult_seat_count

#     child_discount_amount = 0
#     if member.discount_type == 'percentage':
#         child_discount_amount = (Decimal(child_seat_price) * child_seat_count) * (member.discount_percent / 100)
#     elif member.discount_type == 'value':
#         child_discount_amount = member.discount_value * child_seat_count

#     youth_discount_amount = 0
#     if member.discount_type == 'percentage':
#         youth_discount_amount = (Decimal(youth_seat_price) * youth_seat_count) * (member.discount_percent / 100)
#     elif member.discount_type == 'value':
#         youth_discount_amount = member.discount_value * youth_seat_count

#     total_discount_amount = adult_discount_amount + child_discount_amount + youth_discount_amount
#     total_discount_amount = total_discount_amount.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
#     # Create a booking for each seat number
#     company_email = None 
#     bookings = []
#     for seat_number in seat_no:
#         booking_data = filtered_data.copy()
#         booking_data['seat_no'] = seat_number
        
#         today = datetime.datetime.today()
#         today_date = today.date()
#         re_today_date = str(today_date).replace('-', '')
      
#         next_value = get_next_value(re_today_date)
#         reference_no = str(today_date) + '00' + str(next_value)
#         reference_no = reference_no.replace('-', '')
#         booking_data['reference_no'] = f"{reference_no}"

#         # Add total_cost, total_discount_amount, total_seat_count, discount_percent, discount_value, and discount_type to booking_data
#         booking_data['total_cost'] = total_cost.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
#         booking_data['total_discount_amount'] = total_discount_amount
#         booking_data['total_seat_count'] = total_seat_count
#         booking_data['discount_percent'] = member.discount_percent
#         booking_data['discount_value'] = member.discount_value
#         booking_data['discount_type'] = member.discount_type
#         booking_data['status'] = BusBooking.TicketStatus.BOOKED

#         serializer = BusBookingSerializer(data=booking_data)
#         if serializer.is_valid():
#             serializer.save()
#             bookings.append(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     passenger_id = filtered_data.get('passenger')
#     passenger_obj = Passenger.objects.get(pk=passenger_id)
#     bus_id = filtered_data.get('bus')
#     bus_obj = Bus.objects.get(pk=bus_id)

#     if bookings:
#         member_id = bookings[0].get('member', None)
#         if member_id:
#             member_instance = Member.objects.get(id=member_id)
#             company_email = member_instance.email

#         reference_no = bookings[0].get('reference_no', '')
#         created_at_str = bookings[0].get('created_at', '')

#         format_str = '%Y-%m-%dT%H:%M:%S.%f%z'
#         try:
#             created_at_datetime = datetime.datetime.strptime(created_at_str, format_str).astimezone(pytz.UTC)
#             created_at_date = created_at_datetime.date()
#         except ValueError:
#             created_at_date = ''
#         travel_date = datetime.datetime.strptime(created_at_str, format_str).astimezone(pytz.UTC).date()
#         date_str = bookings[0].get('date', '')
#         try:
#             date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#             formatted_travel_date = date.strftime('%B %d, %Y')
#         except ValueError:
#             formatted_travel_date = ''
#         booking_time = bookings[0].get('booking_time', '')

#         bus_id = bookings[0].get('bus', None)
#         if bus_id:
#             bus_instance = Bus.objects.get(pk=bus_id)
#             bus_name = bus_instance.name
#         else:
#             bus_name = ''
#     else:
#         reference_no = ''
#         travel_date = ''
#         booking_time = ''
#         bus_name = ''
#         date_str = ''

#     support_id = GeneralSetting.objects.first()
#     support_number = support_id.phone
#     site_title = support_id.title
#     support_email = support_id.email

#     def generate_qr_code(data, filename):
#         qr = segno.make_qr(data)
#         file_path = os.path.join(settings.MEDIA_ROOT, filename)
#         qr.save(file_path, scale=10)
#         return os.path.join(settings.MEDIA_URL, filename)

#     qr_code_url = generate_qr_code(reference_no, f"qr{reference_no}.png")

#     context = {
#         'passenger': passenger_obj,
#         'primary_phone': passenger_obj.primary_phone,
#         'email': passenger_obj.email,
#         'fullname': passenger_obj.first_name,
#         'bookings': bookings,
#         'bus_name' : bus_instance.name ,
#         'itinerary': bus_obj.itinerary,
#         'seat_quantity': bus_obj.seat_quantity,
#         'starting_point': bus_obj.starting_point,
#         'owner_name': bus_obj.owner_name,
#         'seat_plan': bus_obj.seat_plan,
#         'bus_type': bus_obj.type,
#         'primary_phone': bus_obj.primary_phone,
#         'reference_number': reference_no,
#         'travel_date': travel_date,
#         'booking_time': booking_time,
#         'bus_name': bus_name,
#         'seat_numbers': ", ".join(seat_no),
#         'total_cost': total_cost,
#         'support_number': support_number,
#         'site_title': site_title,
#         'support_email': support_email,
#         'seat_no_count': seat_no_count,
#         'total_cost' : total_cost,
#         'booking_time':booking_time,
#         'date' :formatted_travel_date,
#         'adult_seat_count' : adult_seat_count,
#         'youth_seat_count' : youth_seat_count,
#         'child_seat_count' : child_seat_count,
#         'adult_seat_price' : adult_seat_price,
#         'youth_seat_price' : youth_seat_price,
#         'child_seat_price' : child_seat_price,
#         'created_at' : created_at_date,
#         'qrcode':qr_code_url
#     }

#     print('this is itinerary',bus_obj.itinerary)

#     # Generate PDF
#     pdf_html = render_to_string('bbms/pdf_template.html', context)
    
#     pdf_file = HTML(string=pdf_html).write_pdf()

#     # Generate Email
#     email_html = render_to_string('bbms/email_template.html', context)
#     email_text = strip_tags(email_html)
    
#     email = EmailMessage(
#         subject= bus_name + ' - Booking Confirmation',
#         body=email_text,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         # from_email= "sales@dreamtourism.it",
#         to=[passenger_obj.email],
#         bcc = [support_email,"farhadkabir1212@gmail.com","sales@dreamtourism.it","info@dreamtourism.co.uk","rakib@dreamtourism.co.uk"]
#     )
    
#     email.attach('Booking_Confirmation.pdf', pdf_file, 'application/pdf')

#     email.send()

#     return Response({"message": "Booking created successfully", "data": bookings}, status=status.HTTP_201_CREATED)