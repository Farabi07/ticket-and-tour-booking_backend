# from background_task import background

# @background(schedule=0)  # Schedule to run the task immediately
# def send_email_task(subject, message, from_email, recipient_list, html_message):
#     from django.core.mail import send_mail

#     try:
#         send_mail(
#             subject,
#             message,
#             from_email,
#             recipient_list,
#             html_message=html_message,
#             fail_silently=False,
#         )
#         print("Email sent successfully")
#     except Exception as e:
#         print('Mail exception: ', e)