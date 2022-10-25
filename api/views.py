import io
import json
import re
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from main.enums import *
from main.models import *
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.management import call_command
from .serializer import *

class ScrapeRequestViewSet(viewsets.ModelViewSet):
  queryset = ScrapeRequest.objects.all()
  serializer_class = ScrapeRequestSerializer
  
  def list(self, request):
    email = request.GET.get('email', None)
    password = request.GET.get('password', None)
  
    if not email or not password:
      return Response(data = {'error': 'user credential not provided.'}, status = status.HTTP_400_BAD_REQUEST)
  
    try:
      user = User.objects.get(email = email)
    except User.DoesNotExist:
      return Response(data = {'error': 'user not found'}, status = status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
      return Response(data = {'error': 'login failed with provided credential.'}, status = status.HTTP_400_BAD_REQUEST)
    
    qs = self.queryset.filter(user = user)
    
    data = self.serializer_class(qs, many = True).data
    return Response(data=data, status = status.HTTP_200_OK)
  
  def create(self, request):
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    id_type = request.POST.get('id_type', None)
    id_list = request.POST.get('id_list', None)
    encoding = request.POST.get('encoding', 'Shift-JIS')

    if not email or not password:
      return Response(data = {'error': 'user credential not provided.'}, status = status.HTTP_400_BAD_REQUEST)
    if not id_type:
      return Response(data = {'error': 'id_type not provided.'}, status = status.HTTP_400_BAD_REQUEST)
    if not id_list:
      return Response(data = {'error': 'id_list not provided'}, status = status.HTTP_400_BAD_REQUEST)
          
    try:
      user = User.objects.get(email = email)
    except User.DoesNotExist:
      return Response(data = {'error': 'user not found'}, status = status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(password):
      return Response(data = {'error': 'login failed with provided credential.'}, status = status.HTTP_400_BAD_REQUEST)
    
    if not user.subscribing:
      return Response(data = {'error': 'user not paid'}, status = status.HTTP_400_BAD_REQUEST)
      
    id_list = id_list.split(',')
    if len(id_list) > 5:
      return Response(data = {'error': 'Exceeded maximum id count for api request.'}, status = status.HTTP_400_BAD_REQUEST)
    id_pat = "^([A-Z0-9]{10}|[0-9]{13})$"
    for a in id_list:
      if not re.fullmatch(id_pat, a):
        return Response(data = {'error': f'invalid id {a}.'}, status = status.HTTP_400_BAD_REQUEST)
    
    req = ScrapeRequest(user = user, id_type = id_type)
    req.id_text = '\r\n'.join(id_list)
    req.save()
    call_command('process_requests', id = req.id)
    data = self.serializer_class(req, many = False).data
    return Response(data = data, status = status.HTTP_200_OK)


  def destroy(self, request, *args, **kwargs):
    pass
    # return Response(data = data, status=status.HTTP_200_OK)

  def partial_update(self, request, *args, **kwargs):
    pass
    # return Response(data = data, status = status.HTTP_200_OK)
