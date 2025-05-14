from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

class IsOwnerOrAdmin(BasePermission):
    """
    Permite editar/eliminar una subasta solo si el usuario es el propietario
    o es administrador. Cualquiera puede consultar (GET).
    """
    def has_object_permission(self, request, view, obj):
        # Permitir acceso de lectura a cualquier usuario (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # Permitir si el usuario es el creador o es administrador
        return obj.auctioneer == request.user or request.user.is_staff

class IsBidderOrAdmin(permissions.BasePermission):
    """
    Permite editar/eliminar una puja solo si el usuario es el propietario
    o es administrador. Cualquiera puede consultar (GET).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.bidder_id == request.user or request.user.is_staff
    

class IsCommentAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.user == request.user or request.user.is_staff
    
class IsRaterOrAdmin(permissions.BasePermission):
    """
    Permite editar/eliminar un rating solo si el usuario es el propietario
    o es administrador. Cualquiera puede consultar (GET).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.rater_id == request.user or request.user.is_staff

class IsWalletOwnerOrAdmin(BasePermission):
    """
    Permite acceder al saldo del monedero solo si el usuario es el propietario
    o es un administrador.
    """
    def has_object_permission(self, request, view, obj):
        # Si el método es GET, permitimos acceso solo si el usuario es propietario del monedero
        if request.method == 'GET':
            return obj.user == request.user or request.user.is_staff
        return False