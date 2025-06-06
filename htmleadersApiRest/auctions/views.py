from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Category, Auction, Bid, Comment, Rating, Wallet
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidListCreateSerializer, CommentSerializer, RatingDetailSerializer, RatingListCreateSerializer, WalletTransactionSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrAdmin, IsBidderOrAdmin, IsCommentAuthorOrAdmin, IsRaterOrAdmin, IsWalletOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Avg

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
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['category', 'price']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()] # IsAuthenticated
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Auction.objects.all().annotate(average_rating=Avg('ratings__rating'))
        params = self.request.query_params
        search = params.get('search', None)
        min_price = params.get('min')
        max_price = params.get('max')
        min_rating = self.request.query_params.get('min_rating')
        status = self.request.query_params.get('status', None)

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

        if min_rating:
            min_rating = float(min_rating)
            queryset = queryset.filter(average_rating__gte=min_rating)

        if status == 'open':
            queryset = queryset.filter(closing_date__gt=timezone.now())
        elif status == 'closed':
            queryset = queryset.filter(closing_date__lte=timezone.now())

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
    

class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        auction_id = self.kwargs["auction_pk"]
        return Comment.objects.filter(auction_id=auction_id).order_by('-created_at')

    def perform_create(self, serializer):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])
        serializer.save(user=self.request.user, auction=auction)

class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsCommentAuthorOrAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        auction_id = self.kwargs["auction_pk"]
        return Comment.objects.filter(auction_id=auction_id)
    

class RatingListCreate(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()] 

    serializer_class = RatingListCreateSerializer

    def get_queryset(self):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])
        return Rating.objects.filter(auction=auction)

    def perform_create(self, serializer):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])
        user = self.request.user
        
        existing_rating = Rating.objects.filter(auction=auction, rater=user).first()
        if existing_rating:
            raise ValidationError("Solo puedes valorar una vez esta subasta.")

        # Guarda pasando los datos necesarios
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Overriding to return the created object in the response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RatingRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsRaterOrAdmin] 
    serializer_class = RatingListCreateSerializer

    def get_queryset(self):
        auction = get_object_or_404(Auction, id=self.kwargs["auction_pk"])
        return Rating.objects.filter(auction=auction)

    def perform_update(self, serializer):
        # Si pasa las validaciones, guarda la nueva puja
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class WalletTopUpWithdraw(APIView):
    permission_classes = [IsWalletOwnerOrAdmin]

    def post(self, request, action):
        serializer = WalletTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet = request.user.wallet
        data = serializer.validated_data

        # Verificar que coincide el número de tarjeta con la guardada
        if data['card_number'] != wallet.card_number:
            return Response(
                {'card_number': 'Este número no coincide con el registrado en tu monedero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        amt = data['amount']
        if action == 'topup':
            wallet.balance += amt
        else:  # withdraw
            if wallet.balance < amt:
                return Response(
                    {'amount': 'Saldo insuficiente para retirar esta cantidad.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            wallet.balance -= amt

        wallet.save()
        return Response({'balance': wallet.balance}, status=status.HTTP_200_OK)
    

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ¿Existe ya una cartera?
        try:
            wallet = request.user.wallet
            return Response({"balance": wallet.balance})
        except Wallet.DoesNotExist:
            return Response(
                {"detail": "Wallet does not exist. Please provide card number via POST to create it."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        # Solo se permite crearla si aún no existe
        try:
            wallet = request.user.wallet
            return Response(
                {"detail": "Wallet already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Wallet.DoesNotExist:
            card_number = request.data.get("card_number")
            if not card_number:
                return Response({"detail": "Card number is required."}, status=status.HTTP_400_BAD_REQUEST)

            wallet = Wallet.objects.create(user=request.user, card_number=card_number)
            return Response({"detail": "Wallet created successfully.", "balance": wallet.balance})