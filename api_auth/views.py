from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = get_object_or_404(User, username=request.data["username"])
    if not user.check_password(request.data["password"]):
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    token, _created = Token.objects.get_or_create(user=user)

    return Response({"token": token.key, "username": request.data["username"]})
