from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["GET"])
def shift_detail(request, id):
    # Declare an array of statically defined Shift objects based on models/shift.py. Return the shift object with the requested ID AI!
    return JsonResponse(
        {"id": id, "reversed_id": id[::-1], "flerp": "derp"},  # Reverse the ID string
    )
