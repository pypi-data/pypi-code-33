from rest_framework import status, viewsets
from rest_framework.response import Response

from ccc.beacons.models import Beacon
from ccc.beacons.serializers import BeaconSerializer


class BeaconViewSet(viewsets.ModelViewSet):
    """
        Class for handling Beacon request
    """
    # Will remove this permission class in next iteration, its just for testing and suport frontend development
    permission_classes = []
    serializer_class = BeaconSerializer
    model = Beacon
    queryset = Beacon.objects.all()
    paginate_by = 10

    def list(self, request, *args, **kwargs):
        # List down all the active beacons by defualt
        params = {"is_active": True}
        if request.GET.get('type', None) == "free_beacons":
            params["is_active"] = False
        beacon_list = Beacon.objects.filter(**params).order_by("-created_on")
        page = self.paginate_queryset(beacon_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(beacon_list, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        uid = self.request.data.get("uid")
        beacon = Beacon.objects.filter(uid=uid)
        if beacon.exists():
            return Response({"success": "False", "message": "Duplicate uid found."}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            Beacon.objects.create(**serializer.data)
            return Response({"success": True, "message": "Beacon Added successfully."}, status=status.HTTP_201_CREATED)
        return Response({"success": "False", "message": serializer.errors})

    def update(self, request, pk=None, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        uid = self.request.data.get("uid")
        beacon = Beacon.objects.filter(uid=uid).exclude(pk=pk)
        if beacon.exists():
            return Response({"success": "False", "message": "Duplicate uid found."}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            Beacon.objects.filter(pk=pk).update(**request.data)
            return Response({"success": True, "message": "Beacon updated successfully."}, status=status.HTTP_200_OK)
        return Response({"success": "False", "message": serializer.errors})

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            beacon = Beacon.objects.get(pk=pk)
            beacon.is_active = False
            beacon.user = None
            beacon.save()
            return Response({"success": True, "message": "Beacon deleted successfully."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"success": "False", "message": "Beacon deletion failed"})
