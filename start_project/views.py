
from django.http import HttpResponse

def index(request):
	return HttpResponse("Welcome to Our Tour booking site UK.")