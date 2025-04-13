from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Category, Auction, Bid
from django.utils import timezone
from django.db.models import Q
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidListCreateSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrAdmin, IsBidderOrAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

class CategoryListCreate(generics.ListCreateAPIView):   
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()] #IsAdminUser

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny] # IsAdminUser
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer

class AuctionListCreate(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionListCreateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'price']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()] # IsAuthenticated
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        search = params.get('search', None)
        min_price = params.get('min')
        max_price = params.get('max')

        if search and len(search) < 3:
            raise ValidationError(
                                    {"search": "Search query must be at least 3 characters long."},
                                    code=status.HTTP_400_BAD_REQUEST
                                )
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin] 
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer

class BidListCreate(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()] 

    serializer_class = BidListCreateSerializer

    def get_queryset(self):
        # Trae la subasta específica con el ID proporcionado en los parámetros
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])
        # Filtra las pujas por la subasta
        return Bid.objects.filter(auction=auction)

    def perform_create(self, serializer):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])

        # Validación 1: Verificar si la subasta está abierta
        if auction.closing_date <= timezone.now():
            raise ValidationError("La subasta ya está cerrada, no se puede realizar una nueva puja.")

        # Validación 2: Verificar si la nueva puja es mayor que la anterior puja ganadora
        last_bid = Bid.objects.filter(auction=auction).order_by('-price').first()
        if last_bid and serializer.validated_data['price'] <= last_bid.price:
            raise ValidationError(f"El precio de la nueva puja debe ser mayor que la puja ganadora anterior ({last_bid.price}).")

        # Si pasa las validaciones, guarda la nueva puja
        serializer.save()

class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBidderOrAdmin] 
    serializer_class = BidListCreateSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])
        return Bid.objects.filter(auction=auction)

    def perform_update(self, serializer):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])

        # Validación 1: Verificar si la subasta está abierta
        if auction.closing_date <= timezone.now():
            raise ValidationError("La subasta ya está cerrada, no se puede realizar una nueva puja.")

        # Validación 2: Verificar si la nueva puja es mayor que la anterior puja ganadora
        last_bid = Bid.objects.filter(auction=auction).order_by('-price').first()
        if last_bid and serializer.validated_data['price'] <= last_bid.price:
            raise ValidationError(f"El precio de la nueva puja debe ser mayor que la puja ganadora anterior ({last_bid.price}).")

        # Si pasa las validaciones, guarda la nueva puja
        serializer.save()

class UserAuctionListView(APIView):
    permission_classes = [IsOwnerOrAdmin]
    
    def get(self, request, *args, **kwargs):
        # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)

class UserBidListView(APIView):
    permission_classes = [IsBidderOrAdmin]
    
    def get(self, request, *args, **kwargs):
        # Obtener las subastas del usuario autenticado
        user_bids = Auction.objects.filter(bider=request.user)
        serializer = AuctionListCreateSerializer(user_bids, many=True)
        return Response(serializer.data)