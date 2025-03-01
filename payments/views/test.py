@api_view(['POST'])
def CreateCheckout(request):
    try:
        checkout_data = request.data
        print("Checkout data:", checkout_data)
        
        required_keys = ['firstName', 'lastName', 'email', 'phone', 'gender', 'nationality', 'tourID']
        if not all(key in checkout_data for key in required_keys):
            return Response({"error": "Traveller data is incomplete. Ensure all fields are provided."}, status=400)

        # Convert dateOfBirth to "YYYY-MM-DD"
        date_of_birth = checkout_data.get('dateOfBirth')
        if date_of_birth:
            try:
                date_of_birth = parser.parse(date_of_birth).strftime("%Y-%m-%d")
            except ValueError:
                return Response({"error": "Invalid date format for dateOfBirth."}, status=400)
        else:
            date_of_birth = None

        # Extract currency data
        current_currency = checkout_data.get('currentCurrency', {})
        currency_code = current_currency.get('currency')
        currency_name = current_currency.get('name')
        currency_symbol = current_currency.get('symbol')

        if not currency_code or not currency_name or not currency_symbol:
            return Response({"error": "Currency data is incomplete."}, status=400)

        # Create or get currency
        currency, _ = Currency.objects.get_or_create(
            currency_code=currency_code,
            name=currency_name,
            symbol=currency_symbol
        )
        currency_serialized = CurrencyListSerializer(currency).data

        # Create or get traveller
        traveller, _ = Traveller.objects.get_or_create(
            first_name=checkout_data['firstName'],
            last_name=checkout_data['lastName'],
            email=checkout_data['email'],
            phone=checkout_data['phone'],
            gender=checkout_data['gender'],
            nationality=checkout_data['nationality'],
            passport_number=checkout_data.get('passportId'),
            date_of_birth=date_of_birth
        )

        # Get tour by ID
        tour_id = checkout_data.get('tourID')
        try:
            tour = TourContent.objects.get(id=tour_id)
        except TourContent.DoesNotExist:
            return Response({"error": "No matching tour found."}, status=404)

        # Price calculation
        participants = checkout_data.get('participants', {})
        adult_count = participants.get('adult', 0)
        youth_count = participants.get('youth', 0)
        child_count = participants.get('child', 0)

        adult_price = float(checkout_data.get('adultPrice', 0))
        youth_price = float(checkout_data.get('youthPrice', 0))
        child_price = float(checkout_data.get('childPrice', 0))

        total_adult_price = adult_count * adult_price
        total_youth_price = youth_count * youth_price
        total_child_price = child_count * child_price

        # Calculate total price
        total_price = total_adult_price + total_youth_price + total_child_price

        # Update prices in the TourContent model
        tour.adult_price = adult_price
        tour.youth_price = youth_price
        tour.child_price = child_price
        tour.save()

        # Create or retrieve agent if necessary
        agent_ref_no = checkout_data.get('agentRef')
        agent = None
        if agent_ref_no:
            agent = Member.objects.filter(ref_no=agent_ref_no).first()
            if not agent:
                return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found"}, status=404)

        # Create Booking Before Payment
        selected_date = datetime.strptime(checkout_data.get('selectedDate'), "%Y-%m-%d").date()
        selected_time = datetime.strptime(checkout_data.get('selectedTime'), "%I:%M %p").time()
        booking_data = {
            "agent": agent.id if agent else None,
            "tour": tour.id,
            "traveller": traveller.id,
            "adult_count": adult_count,
            "youth_count": youth_count,
            "child_count": child_count,
            "adult_price": total_adult_price,
            "youth_price": total_youth_price,
            "child_price": total_child_price,
            "total_price": total_price,
            "participants": checkout_data.get('participants', {}),
            "payWithCash": checkout_data.get('payWithCash'),
            "payWithStripe": checkout_data.get('payWithStripe'),
            "selected_date": selected_date,
            "selected_time": selected_time,
            "duration": tour.duration,
            "is_agent": checkout_data.get('is_agent')
        }

        booking_serializer = TourBookingSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking = booking_serializer.save()
        else:
            return Response(booking_serializer.errors, status=400)
        tour_booking = TourBooking.objects.get(id=booking.id)
        pay_with_cash = checkout_data.get('payWithCash', False)
        payment_status = "cash paid"

        # Create a unique payment key
        payment_key = str(uuid.uuid4())
        # Success URL setup
        localhost = "192.168.68.115"
        success_url = None
        if pay_with_cash:
            success_url = f"http://{localhost}:3000/booking-success?payment_id={payment_key}"
        elif tour_booking.is_agent:  # If is_agent is True
            success_url = f"http://{localhost}:3000/payment-success?session_id={payment_key}"
        else:  # If is_agent is False
            success_url = f"http://{localhost}:3000/payment-success?payment_id={payment_key}"

        # Stripe Checkout Session Creation
        if not pay_with_cash:
            line_items = []
            image_urls = [checkout_data.get("tourImage")] if checkout_data.get("tourImage") else []

            if image_urls:
                line_items.append({
                    "price_data": {
                        "currency": currency_code,
                        "product_data": {"name": tour.name, "images": image_urls},
                        "unit_amount": 0,
                    },
                    "quantity": 1,
                })

            if adult_price > 0 and adult_count > 0:
                line_items.append({
                    "price_data": {
                        "currency": currency_code,
                        "product_data": {"name": f"Adult - {tour.name}"},
                        "unit_amount": int(adult_price * 100),
                    },
                    "quantity": adult_count,
                })

            if youth_price > 0 and youth_count > 0:
                line_items.append({
                    "price_data": {
                        "currency": currency_code,
                        "product_data": {"name": f"Youth - {tour.name}"},
                        "unit_amount": int(youth_price * 100),
                    },
                    "quantity": youth_count,
                })

            if child_price > 0 and child_count > 0:
                line_items.append({
                    "price_data": {
                        "currency": currency_code,
                        "product_data": {"name": f"Child - {tour.name}"},
                        "unit_amount": int(child_price * 100),
                    },
                    "quantity": child_count,
                })

            if not line_items:
                return Response({"error": "At least one participant with a valid price is required."}, status=400)

            # Create Stripe Checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=f"http://localhost:3000/payment-success?payment_id={payment_key}",
                cancel_url="http://localhost:3000/cancel",
                customer_email=traveller.email,
            )

            # Create Payment Record with session data
            payment = Payment.objects.create(
                traveller=traveller,
                amount=total_price,
                payment_method="stripe",
                payment_status=session.payment_status,
                stripe_payment_intent_id=session.payment_intent,
                stripe_payment_method_id=session.payment_method_types[0] if session.payment_method_types else "",
                tour=tour,
                currency=currency,
                payment_key=payment_key,
                session_id=session.id,
                agent_ref_no=checkout_data.get('agentRef'),
                payWithCash=pay_with_cash,
                payWithStripe=True,
            )

            # Update booking with payment reference
            booking.payment = payment
            booking.save()

            # Response with session details
            response_data = {
                "sessionId": session.id,
                "url": session.url,
                "tour_details": {
                    "payment_id": payment.id,
                    "name": tour.name,
                    "currency": currency_serialized,
                    "duration": tour.duration,
                    "images": image_urls,
                    "adult_price": tour.adult_price,
                    "child_price": tour.child_price,
                    "youth_price": tour.youth_price,
                    "ref_no": payment.agent_ref_no
                },
                "booking_id": booking.id,
                "payment_key": payment.payment_key,
                "session_details": session,
                "success_url": success_url,
            }

            print("Response data:", response_data)
            return Response(response_data)
        else:  # If paying with cash, skip Stripe session creation
            # Create Payment record as successful (since cash payment is immediate)
            payment = Payment.objects.create(
                traveller=traveller,
                amount=total_price,
                payment_method="cash",
                payment_status="successful",
                tour=tour,
                currency=currency,
                payment_key=payment_key,
                agent_ref_no=checkout_data.get('agentRef'),
                payWithCash=True,
                payWithStripe=False,
            )

            # Update booking with payment reference
            booking.payment = payment
            booking.save()

            response_data = {
                "payment_id": payment.id,
                "payment_key": payment.payment_key,
                "booking_id": booking.id,
                "payment_status": "successful",
                "total_price": total_price,
                "agent_ref_no": agent_ref_no,
                "tour_name": tour.name,
                "booking_details": booking_serializer.data,
                "success_url": success_url,
            }
            return Response(response_data)

    except TourContent.DoesNotExist:
        return Response({"error": "Tour not found"}, status=404)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Session data:", session)
        payment_id = session.get("metadata", {}).get("payment_id")

        try:
            payment = Payment.objects.get(id=payment_id)
            payment.payment_status = "success"
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.stripe_payment_method_id = session.get('payment_method')
            payment.save()

            # Optionally, generate a unique key for the successful payment
            payment.payment_key = str(uuid.uuid4())
            payment.save()

            return JsonResponse({'status': 'success'}, status=200)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

    return JsonResponse({'status': 'success'}, status=200)
