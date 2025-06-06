from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ChangePasswordSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import CustomUser
from auctions.models import Auction, Bid, Comment, Rating
from .serializers import AuctionSerializer, BidSerializer, CommentSerializer, RatingSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
    
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
            'user': serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """Realiza el logout eliminando el RefreshToken (revocar)"""    
        try:
            # Obtenemos el RefreshToken del request
            #Se esperan que esté en el header Authorization
            refresh_token = request.data.get('refresh', None)
            if not refresh_token:
                return Response({"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST)
            
            # Revocar el RefreshToken
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"},
            status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            user = request.user
            if serializer.is_valid():
                if not user.check_password(serializer.validated_data['old_password']):
                    return Response({"old_password": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)
                        
                try:
                    validate_password(serializer.validated_data['new_password'], user)
                except ValidationError as e:
                    return Response({"new_password": e.messages},status=status.HTTP_400_BAD_REQUEST)
                
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"detail": "Password updated successfully."})
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAuctionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtenemos las subastas del usuario autenticado
        auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)

class UserBidListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtenemos las pujas del usuario autenticado
        bids = Bid.objects.filter(bidder_id=request.user)
        serializer = BidSerializer(bids, many=True)
        return Response(serializer.data)

class UserCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtenemos los ocmentarios del usuario autenticado
        comments = Comment.objects.filter(user=request.user)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class UserRatingsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtenemos las pujas del usuario autenticado
        ratings = Rating.objects.filter(rater_id=request.user)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)