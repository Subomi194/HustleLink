from rest_framework.views import APIView
from rest_framework.response import Response


class HomeView(APIView):

    permission_classes = []

    def get(self, request):

        return Response({
            "name": "HustleLink API",
            "version": "1.0",
            "docs": "/api/v1/docs/",
        })