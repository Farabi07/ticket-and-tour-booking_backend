
from django.test import TestCase



from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token
from authentication.models import User
from .models import Bus  # Import your model(s)

class BusViewTests(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(name="Test Bus", type="Test Type", owner_name="Test Owner", primary_phone="1234567890")
        self.user = User.objects.create_user(email='testuser', password='testpassword',first_name="gggs", last_name="hshhs")


        # Initialize the API client with authentication
     #    self.token, _ = Token.objects.get_or_create(user=self.user)

        # Initialize the API client with authentication
        self.client = APIClient()
     #    self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_get_all_bus(self):
        url = reverse('getAllBus')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    

    def test_get_a_bus(self):
        url = reverse('getABus', args=[self.bus.id]) 
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add more assertions as needed

    def test_create_bus(self):
        url = reverse('createBus')  # Use the name of your view function
        data = {
            "name": "New Bus",
            "type": "New Type",
            "owner_name": "New Owner",
            "primary_phone": "9876543210",
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         # Add more assertions as needed

#     def test_update_bus(self):
#         url = reverse('updateBus', args=[self.bus.id])  # Use the name of your view function and provide the object's ID
#         data = {
#             "name": "Updated Bus",
#             "type": "Updated Type",
#             "owner_name": "Updated Owner",
#             "primary_phone": "5555555555",
#         }
#         response = self.client.put(url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Add more assertions as needed

#     def test_delete_bus(self):
#         url = reverse('deleteBus', args=[self.bus.id])  # Use the name of your view function and provide the object's ID
#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Add more assertions as needed

    def test_search_bus(self):
        url = reverse('searchBus')  # Use the name of your view function
        data = {
            "key": "Test",
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add more assertions as needed

    def test_get_a_bus_with_date_and_time(self):
        url = reverse('getABusWithDateAndTime', args=[self.bus.id, '2023-09-05', '08:00'])  # Use the name of your view function and provide the object's ID, date, and time
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add more assertions as needed
