from rest_framework import serializers
from .models import Category, Auction, Bid
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema_field


class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = '__all__'

    def validate_closing_date(self, value):
        if value <= timezone.now() + timedelta(days=15): # usamos timezone.now() porque todavia creation date no se ha creado
            raise serializers.ValidationError("Closing date must be greater than 15 days from now.")
        return value

    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()


class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = '__all__'

    def validate_closing_date(self, value):
        creation_date = self.instance.creation_date
        if value <= creation_date + timedelta(days=15):
            raise serializers.ValidationError("Closing date must be greater than 15 days from the creation date.")
        return value

    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj):
        return obj.closing_date > timezone.now()

class BidListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'

class BidDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'
