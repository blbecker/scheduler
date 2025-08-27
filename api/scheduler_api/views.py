from django.http import JsonResponse
from rest_framework.decorators import api_view

# Static shift data
SHIFTS = [
    {"id": "shift1", "reversed_id": "1tfihs", "flerp": "Morning Shift"},
    {"id": "shift2", "reversed_id": "2tfihs", "flerp": "Afternoon Shift"},
    {"id": "shift3", "reversed_id": "3tfihs", "flerp": "Night Shift"},
]

@api_view(["GET"])
def shift_detail(request, id):
    # Find the shift with matching ID
    shift = next((s for s in SHIFTS if s["id"] == id), None)
    
    if shift:
        return JsonResponse(shift)
    else:
        return JsonResponse({"error": "Shift not found"}, status=404)
