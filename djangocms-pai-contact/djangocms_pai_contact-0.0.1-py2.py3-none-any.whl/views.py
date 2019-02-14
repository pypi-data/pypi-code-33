from django.shortcuts import render
from django.views.generic.edit import View
from django.contrib import messages
from django.shortcuts import redirect
from django.core.validators import validate_email
from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Contact
from .serializers import ContactSerializer


class ContactAPIView(APIView):
    """
    Creates a contact messages
    """

    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
