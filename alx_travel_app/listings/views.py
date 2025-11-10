from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Listing instances.
    Provides CRUD operations: list, create, retrieve, update, destroy
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Booking instances.
    Provides CRUD operations: list, create, retrieve, update, destroy
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer