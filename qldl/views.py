from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, generics, status, permissions, serializers
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import F, Q, Func

from .models import *
from .serializers import *
from .paginations import *


class UserViewSet(viewsets.ViewSet, generics.ListAPIView,
                  generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(self, request):
        return Response(data=self.serializer_class(request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


class LoaiTourViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = LoaiTour.objects.all().order_by('id')
    serializer_class = LoaiTourSerializer

    @action(methods=['get'], detail=True, url_path='tours')
    def get_tours(self, request, pk):
        loai_tour = LoaiTour.objects.get(pk=pk)
        tours = loai_tour.tours.all()

        return Response(data=TourSerializer(tours, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class TourViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    serializer_class = TourDetailSerializer
    pagination_class = TourPagination

    def get_queryset(self):
        tours = Tour.objects.all()

        ten_tour = self.request.query_params.get('ten-tour')
        if ten_tour:
            tours = tours.filter(ten_tour__icontains=ten_tour)

        loai_tour = self.request.query_params.get('loai-tour')
        if loai_tour:
            tours = tours.filter(loai_tour=loai_tour)

        from_price = self.request.query_params.get('from-price')
        if from_price:
            tours = tours.filter(don_gia__gte=from_price)

        to_price = self.request.query_params.get('to-price')
        if to_price:
            tours = tours.filter(don_gia__lte=to_price)

        length = self.request.query_params.get('length')
        if length:
            tours = tours.filter(thoi_gian=length)

        return tours

    @action(methods=['get'], detail=True, url_path='lich-trinh')
    def get_lich_trinh(self, request, pk):
        tour = Tour.objects.get(pk=pk)
        lich_trinh = tour.lichtrinh.all()

        return Response(data=LichTrinhSerializer(lich_trinh, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='booking')
    def booking(self, request, pk):
        tour = Tour.objects.get(pk=pk)

        loai_ve_1 = request.data.get('loai_ve_1')
        loai_ve_2 = request.data.get('loai_ve_2')

        don_gia_1 = request.data.get('don_gia_1')
        so_luong_1 = request.data.get('so_luong_1')

        don_gia_2 = request.data.get('don_gia_2')
        so_luong_2 = request.data.get('so_luong_2')

        if don_gia_1 and so_luong_1 and loai_ve_1:
            lv1 = LoaiVe.objects.get(pk=loai_ve_1)
            tong_tien_1 = int(don_gia_1)*int(so_luong_1)
            ddt1 = DonDatTour.objects.create(loai_ve=lv1, don_gia=don_gia_1,
                                             so_luong=so_luong_1, tong_tien=tong_tien_1,
                                             khach_hang=request.user, tour=self.get_object())
            tour.dondattour.add(ddt1)

            if loai_ve_2 == '2':
                lv2 = LoaiVe.objects.get(pk=loai_ve_2)
                tong_tien_2 = int(don_gia_2)*int(so_luong_2)
                ddt2 = DonDatTour.objects.create(loai_ve=lv2, don_gia=don_gia_2,
                                                so_luong=so_luong_2, tong_tien=tong_tien_2,
                                                 khach_hang=request.user, tour=self.get_object())
                tour.dondattour.add(ddt2)
            tour.save()

            return Response(data=DonDatTourSerializer(ddt1).data,
                                status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        tour = Tour.objects.get(pk=pk)
        comments = tour.commenttour.all()

        return Response(data=CommentTourSerializer(comments, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='images')
    def get_images(self, request, pk):
        tour = Tour.objects.get(pk=pk)
        images = tour.images.all()

        return Response(data=TourImageSerializer(images, many=True, context={'request': request}).data,
                status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='add-comments')
    def add_comments(self, request, pk):
        tour = Tour.objects.get(pk=pk)
        khach_hang = request.user
        noi_dung = request.data.get('noi_dung')

        if noi_dung:
            c = CommentTour.objects.create(noi_dung=noi_dung, khach_hang=khach_hang,
                                             tour=tour)
            tour.commenttour.add(c)
            tour.save()

            return Response(data=CommentTourSerializer(c, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='rating')
    def rating(self, request, pk):
        tour = Tour.objects.get(pk=pk)
        khach_hang = request.user

        r, created = Rating.objects.get_or_create(khach_hang=khach_hang, tour=tour)
        r.rate = request.data.get('rate')
        try:
            r.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=RatingSerializer(r, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ['book', 'add_comments', 'rating']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class TourImageViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = TourImage.objects.all()
    serializer_class = TourImageSerializer


class TinTucViewSet(viewsets.ViewSet, generics.ListAPIView,
                    generics.RetrieveAPIView):
    queryset = TinTuc.objects.all()
    serializer_class = TinTucDetailSerializer
    pagination_class = TinTucPagination

    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        tin_tuc = TinTuc.objects.get(pk=pk)
        khach_hang = request.user

        l, created = Like.objects.get_or_create(khach_hang=khach_hang, tin_tuc=tin_tuc)
        l.liked = not l.liked
        try:
            l.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=LikeTinTucSerializer(l, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        tin_tuc = TinTuc.objects.get(pk=pk)
        comments = tin_tuc.commenttin.all()

        return Response(data=CommentTinTucSerializer(comments, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='images')
    def get_images(self, request, pk):
        tin_tuc = TinTuc.objects.get(pk=pk)
        images = tin_tuc.images.all()

        return Response(data=TinTucImageSerializer(images, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='add-comment')
    def add_comments(self, request, pk):
        tin_tuc = TinTuc.objects.get(pk=pk)
        khach_hang = request.user
        noi_dung = request.data.get('noi_dung')

        if noi_dung:
            c = CommentTinTuc.objects.create(noi_dung=noi_dung, khach_hang=khach_hang,
                                             tin_tuc=tin_tuc)
            tin_tuc.commenttin.add(c)
            tin_tuc.save()

            return Response(data=CommentTinTucSerializer(c, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='add-tin-tuc')
    def add_tin_tuc(self, request):
        chu_de = request.data.get('chu_de')
        noi_dung = request.data.get('noi_dung')

        if chu_de and noi_dung:
            tt = TinTuc.objects.create(chu_de=chu_de, noi_dung=noi_dung)
            tt.save()

            return Response(data=TinTucSerializer(tt, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    def get_permissions(self):
        if self.action in ['like', 'add_comments', 'add_tin_tuc']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class DonDatTourViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = DonDatTour.objects.all()
    serializer_class = DonDatTourSerializer


class CommentTourViewSet(viewsets.ViewSet, generics.CreateAPIView,
                         generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = CommentTour.objects.all()
    serializer_class = CreateCommentTourSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().khach_hang:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().khach_hang:
            return super().partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


def index(request):
    return HttpResponse('Hello Alexnder Thinh To Quan Ly Du Lich Website')
