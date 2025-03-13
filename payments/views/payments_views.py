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


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def PaymentSuccess(request):
    """
    Handle successful payment and update payment status.
    """
    try:
        payment_id = request.data.get('payment_id')

        # Retrieve payment from database
        payment = Payment.objects.filter(stripe_payment_id=payment_id).first()
        if not payment:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check status from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_id)
        if intent.status == "succeeded":
            payment.payment_status = "succeeded"
            payment.save()
            return Response({"message": "Payment successful", "payment_id": payment.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment not confirmed as successful"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def PaymentCancel(request):
    """
    Handle canceled payment and update payment status.
    """
    try:
        payment_id = request.data.get('payment_id')

        # Retrieve payment from database
        payment = Payment.objects.filter(stripe_payment_id=payment_id).first()
        if not payment:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check status from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_id)
        if intent.status in ["canceled", "requires_payment_method"]:
            payment.payment_status = "failed"
            payment.save()
            return Response({"message": "Payment canceled or failed", "payment_id": payment.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment still pending"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def PaymentFailed(request):
    """
    Handle failed payment and update the payment status to 'failed'.
    """
    try:
        payment_id = request.data.get('payment_id')

        if not payment_id:
            return Response({"error": "Payment intent ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the payment from the database
        payment = Payment.objects.filter(stripe_payment_id=payment_id).first()
        if not payment:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check the payment intent status from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_id)
        if intent.status in ["requires_payment_method", "canceled"]:
            payment.payment_status = "failed"
            payment.save()
            return Response({"message": "Payment failed", "payment_id": payment.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment still pending or already succeeded"}, status=status.HTTP_400_BAD_REQUEST)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getPaymentStatus(request, payment_id):
    """
    Get the payment status from Stripe by payment intent ID.
    """
    try:
        # Retrieve the payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_id)
        
        # Return the status of the payment intent
        return Response({
            'status': intent.status,
            'payment_id': intent.id
        }, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', None)
    event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_ENDPOINT_SECRET)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        booking_id = metadata.get('booking_id')
        total_discount = float(metadata.get('total_discount', 0))
        agent_ref_no = metadata.get('agent_ref_no', None)
        payment_key = metadata.get('payment_key', None)
        currency_code = metadata.get('currency')

        if not booking_id:
            return JsonResponse({'error': 'Booking ID not found in metadata'}, status=400)

        booking = TourBooking.objects.get(id=booking_id)
        currency = Currency.objects.get(currency_code=currency_code)

        # Create Payment
        payment = Payment.objects.create(
            traveller=booking.traveller,
            amount=booking.total_price,
            payment_method="stripe",
            payment_status="succeeded",
            tour=booking.tour,
            tour_booking=booking,
            session_id=session['id'],
            payWithCash=False,
            payWithStripe=True,
            agent_ref_no=agent_ref_no,
            payment_key=payment_key,
            currency=currency
        )

        # Update Booking
        booking.payment = payment
        booking.total_discount_amount = total_discount
        booking.status = "paid"
        booking.save()

        # Generate Invoice PDF
        context = {
            "booking_id": booking.id,
            "tour_name": booking.tour.name,
            "tour_duration": booking.tour.duration,
            "total_price": booking.total_price,
            "total_discount_amount": total_discount,
            "payment_status": "succeeded",
            "traveller_email": booking.traveller.email,
            "traveller_phone": booking.traveller.phone,
            "traveller_first_name":booking.traveller.first_name,
            "traveller_last_name":booking.traveller.last_name,
            "currency": currency.currency_code,
            "booking_date": booking.created_at,
            "travel_date": booking.selected_date,  
            "travel_time": booking.selected_time,
            "invoice_no":booking.invoice_no  
        }
            # Generate PDFs
        # pdf_html = render_to_string('payments/pdf_template.html',context)
        # pdf_file = HTML(string=pdf_html).write_pdf()
        # pdf_filename = f"{booking.tour.name}_Booking_Confirmation.pdf"
        # booking.email_pdf.save(pdf_filename, ContentFile(pdf_file), save=True)
        # payment.email_pdf.save(pdf_filename, ContentFile(pdf_file), save=True)

        invoice_html = render_to_string('payments/tour-booking-invoice.html', context)
        invoice_file = HTML(string=invoice_html).write_pdf()
        pdf_invoice = f"{booking.tour.name}_Booking_Invoice.pdf"
        booking.booking_invoice_pdf.save(pdf_invoice, ContentFile(invoice_file), save=True)
        payment.booking_invoice.save(pdf_invoice, ContentFile(invoice_file), save=True)
        # Send Email
        email_html = render_to_string('payments/email_body_template.html', {"booking": booking})
        allowed_tags = ['p', 'br', 'strong', 'em', 'a']
        email_cleaned_html = bleach.clean(email_html, tags=allowed_tags, strip=True)
        email_text = strip_tags(email_cleaned_html)

        email = EmailMessage(
            subject=f"{booking.tour.name} - Booking Confirmation",
            body=email_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.traveller.email],
            bcc=["farabicse07@gmail.com"]
        )
        email.attach('Booking_Confirmation.pdf', pdf_invoice, 'application/pdf')
        email.send()

        # Response Data
        response_data = {
            "status": "success",
            "payment_id": payment.id,
            "payment_key": payment.payment_key,
            "booking_id": booking.id,
            "payment_status": payment.payment_status,
            "total_price": payment.amount,
            "agent_ref_no": payment.agent_ref_no,
            "tour_name": booking.tour.name,
            "currency": {
                "currency_code": currency.currency_code,
                "name": currency.name,
                "symbol": currency.symbol
            },
            "session_id": session['id'],
            "total_discount": total_discount,
        }
        return JsonResponse(response_data, status=200)

    return JsonResponse({'status': 'event received'}, status=200)



@api_view(['POST'])
def CreateCheckout(request):
    try:
        checkout_data = request.data
        session = None
        required_keys = ['firstName', 'lastName', 'email', 'phone', 'gender', 'nationality', 'tourID']
        
        # Ensure all required fields are provided
        if not all(key in checkout_data for key in required_keys):
            return Response({"error": "Traveller data is incomplete. Ensure all fields are provided."}, status=400)
        
        # Parse date of birth
        date_of_birth = checkout_data.get('dateOfBirth')
        if date_of_birth:
            try:
                date_of_birth = parser.parse(date_of_birth).strftime("%Y-%m-%d")
            except ValueError:
                return Response({"error": "Invalid date format for dateOfBirth."}, status=400)
        else:
            date_of_birth = None
        
        # Get currency info and ensure it's valid
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
        print("traveller info:", traveller.first_name)
        # Get the tour
        tour_id = checkout_data.get('tourID')
        try:
            tour = TourContent.objects.get(id=tour_id)
        except TourContent.DoesNotExist:
            return Response({"error": "No matching tour found."}, status=404)
        
        # Price calculation for participants
        participants = checkout_data.get('participants', {})
        adult_count = participants.get('adult', 0)
        youth_count = participants.get('youth', 0)
        child_count = participants.get('child', 0)
        adult_price = Decimal(str(checkout_data.get('adultPrice', 0)))
        youth_price = Decimal(str(checkout_data.get('youthPrice', 0)))
        child_price = Decimal(str(checkout_data.get('childPrice', 0)))
        
        total_adult_price = adult_count * adult_price
        total_youth_price = youth_count * youth_price
        total_child_price = child_count * child_price
        total_price = total_adult_price + total_youth_price + total_child_price
        
        # Use discounted total price if provided
        discounted_total_price = checkout_data.get('discountedtotalprice')
        if discounted_total_price:
            total_price = Decimal(str(discounted_total_price)).quantize(Decimal('0.01'))
            print("coupont toal price", total_price)
            
        
        # Update the tour's price
        tour.adult_price = adult_price
        tour.youth_price = youth_price
        tour.child_price = child_price
        tour.save()

        # Discount calculation
        coupon_discount = checkout_data.get('coupon_discount')  # Get coupon_discount from request data
        agent_ref_no = checkout_data.get('agentRef') if not coupon_discount else None
        print("farabi agent ref no", agent_ref_no)

        agent = None
        total_discount_amount = Decimal(0)  # Default discount amount

        if coupon_discount is not None:
            total_discount_amount = calculate_discount(total_price, coupon_discount=coupon_discount).quantize(Decimal('0.01'))
            # Find the member by coupon_text
            print("farabi coupon discount amount", total_discount_amount)
            member = Member.objects.filter(coupon_text=checkout_data.get('coupon_text')).first()
            if member:
                agent = member
        elif agent_ref_no:
            agent = Member.objects.filter(ref_no=agent_ref_no).first()
            if not agent:
                return Response({"error": f"Agent with ref_no '{agent_ref_no}' not found"}, status=404)
            
            # Calculate discount since agent_ref_no is valid
            total_discount_amount = calculate_discount(total_price, ref_no=agent_ref_no).quantize(Decimal('0.01'))
            print("farabi total discount amount", total_discount_amount)

            # Save discount to the agent
            agent.total_discount_amount = total_discount_amount
            agent.save()
        else:
            print("Agent ref no is None, skipping discount calculation.")
        
        # Generate invoice number
        invoice_no = generate_reference_number()
        reference_no = generate_reference_number()
        
        # Select booking date and time
        selected_date = datetime.strptime(checkout_data.get('selectedDate'), "%Y-%m-%d").date()
        selected_time = datetime.strptime(checkout_data.get('selectedTime'), "%I:%M %p").time()
        pay_with_cash = checkout_data.get('payWithCash')
        pay_with_stripe = checkout_data.get('payWithStripe')
        
        # Determine payment status
        if checkout_data.get('payWithCash'):
            status = 'paid'
        elif checkout_data.get('payWithStripe'):
            status = 'unpaid'
        else:
            status = 'pending'
        
        booking_data = {
            "tour_id": tour.id,
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
            "invoice_no": invoice_no,
            "agent_ref": agent_ref_no if agent else None,
        }
      
        print("farabi booking time ", selected_date)
        
        # If paying with cash, include discount details
        if agent:
            booking_data["discount_percent"] = agent.discount_percent
            booking_data["discount_value"] = agent.discount_value
            booking_data["discount_type"] = agent.discount_type
            booking_data["agent_id"] = agent.id

            if checkout_data.get('payWithCash'):
                booking_data["total_discount_amount"] = total_discount_amount
            else:
                booking_data["total_discount_amount"] = None  
        else:
            booking_data["discount_percent"] = None
            booking_data["discount_value"] = None
            booking_data["discount_type"] = None
            booking_data["total_discount_amount"] = None
            booking_data.pop("agent_id", None)  # Remove agent_id from booking_data if no agent

        # Create the booking
        booking_serializer = TourBookingListSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking = booking_serializer.save()
        else:
            return Response(booking_serializer.errors, status=400)
        
        tour_booking = TourBooking.objects.get(id=booking.id)
        payment_key = str(uuid.uuid4())
        
        # Success URL setup
        localhost = "http://192.168.68.110:3000"
        base_url = "https://bustours.dreamtourism.co.uk"
        uk_url = "https://dreamtourism.co.uk"
        success_url = None
        if checkout_data.get('payWithStripe'):
            success_url = f"{base_url}/booking-success?payment_id={payment_key}"
        elif tour_booking.is_agent:  # If is_agent is True
            success_url = f"{base_url}/booking-success?payment_id={payment_key}"
        else:  # If is_agent is False
            success_url = f"{uk_url}/payment-success?payment_id={payment_key}"

        # Process Stripe payment if chosen
        image_urls = []
        if checkout_data.get('payWithStripe'):
            line_items = []
            image_urls = [checkout_data.get("tourImage")] if checkout_data.get("tourImage") else []
            if image_urls:
                line_items.append({
                    "price_data": {
                        "currency": currency_code,
                        "product_data": {"name": tour.name, "images": image_urls},
                        "unit_amount": int(total_price * 100),
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
                success_url=f"{base_url}/payment-success?payment_id={payment_key}",
                cancel_url="http://localhost:3000/cancel",
                customer_email=traveller.email,
                billing_address_collection="required",
                metadata={
                    'booking_id': booking.id,
                    'total_discount': str(total_discount_amount),
                    'agent_ref_no': agent_ref_no,
                    'payment_key': payment_key,
                    "currency": currency_code
                }
            )

            return Response({'session_url': session.url, 'booking_id': booking.id, 'total_discount': total_discount_amount})

        else:  # If paying with cash, immediately create payment object
            payment = Payment.objects.create(
                traveller=traveller,
                amount=total_price,
                payment_method="cash",
                payment_status="succeeded",
                tour=tour,
                currency=currency,
                payment_key=payment_key,
                agent_ref_no=checkout_data.get('agentRef'),
                payWithCash=True,
                payWithStripe=False,
                tour_booking=booking,
            )
            # Update booking with payment reference
            booking.payment = payment
            booking.save()
            context = {
                "booking_id": booking.id,
                "tour_name": tour.name,
                "tour_duration": tour.duration,
                "tour_images": image_urls,
                "adult_price": str(adult_price),  # Convert Decimal to string
                "youth_price": str(youth_price),  # Convert Decimal to string
                "child_price": str(child_price),  # Convert Decimal to string
                "total_price": str(total_price),  # Convert Decimal to string
                "total_discount_amount": str(total_discount_amount),  # Convert Decimal to string
                "payment_status": "successful",
                "payment_key": payment_key,
                "payment_method": "cash" if pay_with_cash else "stripe",
                "payment_reference_number": payment.agent_ref_no if payment else None,
                "traveller_first_name": traveller.first_name,
                "traveller_last_name": traveller.last_name,
                "traveller_email": traveller.email,
                "traveller_phone": traveller.phone,
                "currency": currency.currency_code,
                "success_url": success_url,
                "session_details": session if not pay_with_cash else None,
                "payment_id": payment.id if payment else None,
                "agent_ref_no": checkout_data.get('agentRef'),
                "pay_with_cash": pay_with_cash,
                "pay_with_stripe": not pay_with_cash,
                "booking_date": tour_booking.created_at,
                "travel_date": tour_booking.selected_date,  
                "travel_time": tour_booking.selected_time,
                "invoice_no": invoice_no 
            }
            # Generate PDFs
            invoice_html = render_to_string('payments/tour-booking-invoice.html', context)
            invoice_file = HTML(string=invoice_html).write_pdf()
            pdf_invoice = f"{tour.name}_Booking_Invoice.pdf"
            booking.booking_invoice_pdf.save(pdf_invoice, ContentFile(invoice_file), save=True)
            payment.booking_invoice.save(pdf_invoice, ContentFile(invoice_file), save=True)

            # Send Email
            email_html = render_to_string('payments/email_body_template.html', {"booking": booking})
            email_cleaned_html = bleach.clean(email_html, tags=[], strip=True)
            email_text = strip_tags(email_cleaned_html)

            email = EmailMessage(
                subject=f"{tour.name} - Booking Confirmation",
                body=email_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[traveller.email],
                bcc=["farabicse07@gmail.com"]
            )
            
            email.attach('Booking_Invoice.pdf', invoice_file, 'application/pdf')
            email.send()

            response_data = {
                "payment_id": payment.id,
                "payment_key": payment.payment_key,
                "booking_id": booking.id,
                "payment_status": "successful",
                "total_price": str(total_price),  # Convert Decimal to string
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
    
from decimal import Decimal

def calculate_discount(total_price, ref_no=None, coupon_discount=None):
    """Calculate discount based on ref_no from the Member model or use provided coupon_discount."""
    discount_amount = Decimal(0)
    
    if coupon_discount is not None:
        # Use the provided coupon discount amount
        discount_amount = Decimal(coupon_discount)
    elif ref_no:
        # Find the member by ref_no (which is the agent's reference number)
        member = Member.objects.filter(ref_no=ref_no).first()
        if member:
            # Retrieve the discount information from the member
            discount_type = member.discount_type
            discount_value = member.discount_value
            discount_percent = member.discount_percent
            
            # Ensure that the discount fields have valid values
            if discount_type == "percentage" and discount_percent is not None:
                # Calculate discount based on percentage
                discount_amount = (total_price * discount_percent) / 100
            elif discount_type == "value" and discount_value is not None:
                # Use fixed discount value
                discount_amount = discount_value
            else:
                # Invalid discount type or missing values
                print(f"Invalid discount type or missing value for ref_no {ref_no}.")
        else:
            print(f"No member found for ref_no {ref_no}.")
    
    return discount_amount.quantize(Decimal('0.01'))



# Function to generate reference number
import random
import string

def generate_reference_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_ticket_number(tour_type):
    """
    Generate a unique ticket number in the format: {TOUR_TYPE}-{RANDOM_NUMBER}{RANDOM_LETTERS}.
    """
    random_number = random.randint(100, 999)  # 3-digit random number
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))  # 3 random uppercase letters
    return f"{tour_type.upper()}-{random_number}{random_letters}"

def generate_unique_ticket_number(tour_type):
    """
    Ensure the generated ticket number is unique by checking the database.
    """
    while True:
        ticket_number = generate_ticket_number(tour_type)
        if not TourBooking.objects.filter(ticket_number=ticket_number).exists():
            return ticket_number

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