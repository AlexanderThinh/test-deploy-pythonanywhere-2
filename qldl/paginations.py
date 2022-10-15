from rest_framework.pagination import PageNumberPagination


class TourPagination(PageNumberPagination):
    page_size = 3


class TinTucPagination(PageNumberPagination):
    page_size = 5