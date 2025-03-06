from calendar import c
from email import message
from re import sub
import re
from threading import local
from yaml import serialize
import stripe
import uuid
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from payments.models import Payment, Traveller, Currency
from payments.serializers import PaymentSerializer, PaymentListSerializer, PaymentMinimalSerializer, CurrencyListSerializer
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import  extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from authentication.decorators import has_permissions
from tour.models import TourContent, TourContentImage
from tour.serializers import TourBookingListSerializer
from datetime import datetime
from dateutil import parser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from member.models import Member
import uuid
from dateutil import parser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from payments.models import Traveller,Payment, Currency
from tour.models import TourContent,TourBooking
from tour.serializers import  TourBookingSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from payments.models import Payment
from decimal import Decimal,ROUND_DOWN
from weasyprint import HTML
import bleach
from django.core.files.base import ContentFile
from django.utils.html import strip_tags
import os
import segno

@api_view(['POST'])
def CreatePayment(request):
    if request.method == 'POST':
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            currency = serializer.validated_data['currency']
            payment_method_id = serializer.validated_data['payment_method_id']
            return_url = serializer.validated_data['return_url']
            
            try:
                # Create the Stripe payment intent
                payment_intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency=currency,
                    payment_method=payment_method_id,
                    confirmation_method='manual',
                    confirm=True,
                    return_url=return_url
                )

                # Save payment record in the database
                payment = Payment.objects.create(
                    user=request.user,  # Assuming you have a logged-in user
                    amount=amount / 100,  # Amount in dollars (Stripe returns in cents)
                    currency=currency,
                    payment_method='card',  # You can modify this based on payment method
                    stripe_payment_id=payment_intent.id,
                    stripe_payment_method_id=payment_method_id
                )

                # Return the client secret to the frontend to confirm the payment
                return Response({
                    'client_secret': payment_intent.client_secret,
                    'payment_id': payment.id  # Optionally, return the payment ID
                }, status=status.HTTP_200_OK)

            except stripe.error.CardError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        customer_email = session["customer_details"]["email"]
        tour_id = session["metadata"]["tour_id"]
        print("customer_email",customer_email)
        tour = TourBooking.objects.get(id=tour_id)
        send_mail(
            subject="Here is your product",
            message=f"Thank you for purchasing {tour_id}",
            recipient_list=[customer_email],
            from_email=settings.DEFAULT_FROM_EMAIL
        )
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



stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def CreateCheckout(request):
    try:
        checkout_data = request.data
        session = None
        required_keys = ['firstName', 'lastName', 'email', 'phone', 'gender', 'nationality', 'tourID']
        if not all(key in checkout_data for key in required_keys):
            return Response({"error": "Traveller data is incomplete. Ensure all fields are provided."}, status=400)
        
        date_of_birth = checkout_data.get('dateOfBirth')
        if date_of_birth:
            try:
                date_of_birth = parser.parse(date_of_birth).strftime("%Y-%m-%d")
            except ValueError:
                return Response({"error": "Invalid date format for dateOfBirth."}, status=400)
        else:
            date_of_birth = None
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
        print("traveller info:",traveller.first_name)
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

        # Convert float values to Decimal
        adult_price = Decimal(str(checkout_data.get('adultPrice', 0)))
        youth_price = Decimal(str(checkout_data.get('youthPrice', 0)))
        child_price = Decimal(str(checkout_data.get('childPrice', 0)))

        total_adult_price = adult_count * adult_price
        total_youth_price = youth_count * youth_price
        total_child_price = child_count * child_price
        total_price = total_adult_price + total_youth_price + total_child_price

        # Update prices in the TourContent model
        tour.adult_price = adult_price
        tour.youth_price = youth_price
        tour.child_price = child_price
        tour.save()
        agent_ref_no = checkout_data.get('agentRef')
        payment_status = ""
        agent = None
        if agent_ref_no:
            agent = Member.objects.filter(ref_no=agent_ref_no).first()
            if not agent:
                return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found"}, status=404)
        # Calculate discount based on total price and agent ref_no
        total_discount_amount = calculate_discount(total_price, agent_ref_no)
        # print("total_discount_amount:", total_discount_amount)
        total_discount_amount = total_discount_amount.quantize(Decimal('0.01'),)
        # Update the total discount amount for the agent
        if agent:
            agent.total_discount_amount = total_discount_amount
            agent.save()
        # print("Updated agent total discount amount:", agent.total_discount_amount)
        # print("agent:", agent.total_discount_amount)
        # Create Booking Before Payment
        selected_date = datetime.strptime(checkout_data.get('selectedDate'), "%Y-%m-%d").date()
        selected_time = datetime.strptime(checkout_data.get('selectedTime'), "%I:%M %p").time()
        if checkout_data.get('payWithCash'):
            status = 'paid'
        elif checkout_data.get('payWithStripe'):
            status = 'unpaid'
        else:
            status = 'pending' 
        booking_data = {
            "agent_id": agent.id if agent else None,  # Pass agent ID
            "tour_id": tour.id,  # Pass tour ID
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
            "is_agent": checkout_data.get('is_agent'),
            "status": status,           
        }
        # Apply discount details only if paying with Cash
        pay_with_stripe = checkout_data.get('payWithStripe', False)  # Default to False
        pay_with_cash = checkout_data.get('payWithCash', False)
        if pay_with_cash:
            booking_data["total_discount_amount"] = total_discount_amount
            if agent:
                booking_data["discount_percent"] = agent.discount_percent
                booking_data["discount_value"] = agent.discount_value
                booking_data["discount_type"] = agent.discount_type
            print("Booking Data with Discount (Pay with Cash):", booking_data)
            print(" farabi agent data ",booking_data["total_discount_amount"])
        # Create the booking data (without discount details if paying with Stripe)
        booking_serializer = TourBookingListSerializer(data=booking_data)
        if booking_serializer.is_valid():
            print("Debug - Before Saving Booking Data:", booking_data)
            booking = booking_serializer.save()
            booking.save()
            # print("Debug - After Saving - Agent:", booking.agent)
            # print("Debug - After Saving - Tour:", booking.tour)
        else:
            return Response(booking_serializer.errors, status=400)
        

        # print("booking serialized data ",booking_serializer)
        tour_booking = TourBooking.objects.get(id=booking.id)

        # print("booking total_discount_amount ",total_discount_amount)
        # Create a unique payment key
        payment_key = str(uuid.uuid4())
        # Success URL setup
        localhost = "http://192.168.68.110:3000"
        base_url = "https://bustours.dreamtourism.co.uk"
        success_url = None
        if pay_with_stripe:
            success_url = f"{localhost}/booking-success?payment_id={payment_key}"
        elif tour_booking.is_agent:  # If is_agent is True
            success_url = f"{localhost}/payment-success?payment_id={payment_key}"
        else:  # If is_agent is False
            success_url = f"{localhost}/payment-success?payment_id={payment_key}"
        print("success_url",success_url)
        # Stripe Checkout Session Creation
        image_urls = []
        if  pay_with_stripe:
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
                # customer = traveller.first_name,
                billing_address_collection="required",
                metadata={'booking_id': booking.id}
  
            )
            booking_data = {
                "status":"success"
            }
            
            payment_status = "succeeded"  # Assuming payment is successful here, you can adjust this based on Stripe's response

            payment = Payment.objects.create(
                traveller=traveller,
                amount=total_price,
                payment_method=session.payment_method_types[0] if session.payment_method_types else "",
                payment_status=payment_status,
                stripe_payment_intent_id=session.payment_intent,
                stripe_payment_method_id=session.payment_method_types[0] if session.payment_method_types else "",
                tour=tour,
                currency=currency,
                payment_key=payment_key,
                session_id=session.id,
                agent_ref_no=checkout_data.get('agentRef'),
                payWithStripe=True
            )

            # Update booking with payment reference
            # booking.payment = payment
            # booking.status = "paid"  # Set the booking status to 'paid' since payment was successful
            # booking.total_discount_amount = total_discount_amount
            # booking.save()

            # # Optional: Add Stripe session details to the booking for better tracking
            booking.stripe_session_id = session.id
            booking.stripe_payment_intent = session.payment_intent
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

            # print("Response data:", response_data)
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
        context = {
            "booking_id": booking.id,
            "tour_name": tour.name,
            "tour_duration": tour.duration,
            "tour_images": image_urls,
            "adult_price": adult_price,
            "youth_price": youth_price,
            "child_price": child_price,
            "total_price": total_price,
            "total_discount_amount": total_discount_amount,
            "payment_status": payment_status,
            "payment_key": payment_key,
            "payment_method": "cash" if pay_with_cash else "stripe",
            "payment_reference_number": payment.agent_ref_no if payment else None,
            "traveller_first_name": traveller.first_name,
            "traveller_last_name": traveller.last_name,
            "traveller_email": traveller.email,
            "traveller_phone": traveller.phone,
            "currency": currency,
            "success_url": success_url,
            "session_details": session if not pay_with_cash else None,
            "payment_id": payment.id if payment else None,
            "agent_ref_no": checkout_data.get('agentRef'),
            "pay_with_cash": pay_with_cash,
            "pay_with_stripe": not pay_with_cash,
            "booking_date": tour_booking.created_at, 
            "travel_date": tour_booking.selected_date,
            "travel_time": tour_booking.selected_time
        }
    # Generate PDFs
            # pdf_html = render_to_string('payments/pdf_template.html',context)
            # print("farabi booking data",booking_data)
            # pdf_file = HTML(string=pdf_html).write_pdf()
            # pdf_filename = f"{tour.name}_Booking_Confirmation.pdf"
            # booking.email_pdf.save(pdf_filename, ContentFile(pdf_file), save=True)
            # payment.email_pdf.save(pdf_filename, ContentFile(pdf_file), save=True)

        invoice_html = render_to_string('payments/tour-booking-invoice.html',context)
        invoice_file = HTML(string=invoice_html).write_pdf()
        pdf_invoice = f"{tour.name}_Booking_Invoice.pdf"
        booking.booking_invoice.save(pdf_invoice, ContentFile(invoice_file), save=True)
        payment.booking_invoice.save(pdf_invoice, ContentFile(invoice_file), save=True)

        # Send Email
        email_html = render_to_string('payments/email_template.html', {"booking": booking})
        email_cleaned_html = bleach.clean(email_html, tags=[], strip=True)
        email_text = strip_tags(email_cleaned_html)

        email = EmailMessage(
            subject=f"{tour.name} - Booking Confirmation",
            body=email_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[traveller.email],
            bcc = ["farabicse07@gmail.com"]
        )
        
        email.attach('Booking_Invoice.pdf', invoice_file, 'application/pdf')

            # email.send()
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

    
def calculate_discount(total_price, ref_no):
    """Calculate discount based on ref_no from the Member model."""
    discount_amount = Decimal(0)
    
    # Find the member by ref_no (which is the agent's reference number)
    member = Member.objects.filter(ref_no=ref_no).first()
    
    if member:
        # Retrieve the discount information from the member
        discount_type = member.discount_type
        discount_value = member.discount_value
        discount_percent = member.discount_percent
        
        if discount_type == "percentage":
            # Calculate discount based on percentage
            discount_amount = (total_price * discount_percent) / 100
        elif discount_type == "value":
            # Use fixed discount value
            discount_amount = discount_value
    
    return discount_amount




@api_view(['GET'])
def getPaymentDetails(request, payment_key):
    try:
        payment_item = Payment.objects.get(payment_key=payment_key)
        # print("payment data:", payment_item)

        serializer = PaymentListSerializer(payment_item)
        # print("serializer data:", serializer.data)

        # Construct response data
        response_data = {"payment_details": serializer.data}
        print("response_data:", response_data,"tour_name:", payment_item.tour.name)
        return Response(response_data)

    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)


@api_view(['GET'])
def get_customers(request):
    try:
        customers = stripe.Customer.list(limit=3)
        customer_list = [{"id": c.id, "email": c.email, "created": c.created} for c in customers.auto_paging_iter()]
        print("customer_list:", customer_list)
        print("customers:", customers)
        return JsonResponse({"customers": customer_list}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



@api_view(['GET'])
def get_balance_transactions(request):
    try:
        # Set limit to 100 to fetch a larger batch of balance transactions
        balance_transactions = stripe.BalanceTransaction.list(limit=100)

        # Check if 'data' field contains transactions
        if 'data' in balance_transactions and balance_transactions['data']:
            transaction_list = balance_transactions['data']
        else:
            return JsonResponse({"error": "No balance transactions found."}, status=404)

        # Return the transactions in the response
        return JsonResponse({"balance_transactions": transaction_list}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@extend_schema(request=PaymentListSerializer, responses=PaymentListSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def getAPayment(request, pk):
	try:
		payments = Payment.objects.get(pk=pk)
		serializer = PaymentListSerializer(payments)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Payment id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)