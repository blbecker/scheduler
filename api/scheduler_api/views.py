from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def shift_detail(request, id):
    return JsonResponse({
        'id': id,
        'reversed_id': id[::-1]  # Reverse the ID string
    })
