from rest_framework import serializers
from .models import CustomUser
from auctions.models import Auction, Bid, Comment, Rating

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name','email', 'birth_date', 'municipality',
        'locality', 'password')
        extra_kwargs = {
        'password': {'write_only': True},
        }

    def validate_email(self, value):
        user = self.instance # Solo tiene valor cuando se está actualizando
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk if user else None).exists():
            raise serializers.ValidationError("Email already in used.")

        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data) 

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'title', 'description', 'price', 'creation_date']

class BidSerializer(serializers.ModelSerializer):
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'price', 'creation_date', 'auction_title']

class CommentSerializer(serializers.ModelSerializer):
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'title', 'text', 'user', 'auction', 'auction_title']

class RatingSerializer(serializers.ModelSerializer):
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'rating', 'rater_id', 'auction', 'auction_title']