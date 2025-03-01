from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
# Create your tests here.
from member.models import Member


class MemberTest(APITestCase):
    def setUp(self):
        Member.objects.create(
            name='Casper')

    def test_member_breed(self):
        member = Member.objects.get(name='Casper')
        self.assertEqual(
            member.get_breed(), "Casper belongs to Bull Dog breed.")
