from django.contrib import admin
from  django.contrib.auth.models import Group
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.urls import path, re_path
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django import forms

from .models import *

class QLDLAppAdminSite(admin.AdminSite):
    site_header = 'Quản Lý Tour Du Lịch'
    index_title = 'Công cụ quản trị'

    class Media:
        css = {
            'all': ('/static/css/style.css',)
        }
    
    def get_urls(self):
        return [
            path('tour-stats/', self.tour_stats)
        ] + super().get_urls()

    def tour_stats(self, request):

        tour_amount = Tour.objects.count()
        tour_total_money = Tour.objects.annotate(sum=Sum('dondattour__tong_tien')).values('id', 'ten_tour', 'sum').all()

        # Lay query_pram
        day = request.GET.get('day')
        month = request.GET.get('month')
        year = request.GET.get('year')
        # Lay query_pram

        if day:
            tour_total_money = tour_total_money.filter(ngay_bat_dau__day=day)
        if month:
            tour_total_money = tour_total_money.filter(ngay_bat_dau__month=month)
        if year:
            tour_total_money = tour_total_money.filter(ngay_bat_dau__year=year)

        response = TemplateResponse(request, 'admin/tour-stats.html', {
            'tour_amount': tour_amount,
            'tour_total_money': tour_total_money,
            'day': day,
            'month': month,
            'year': year
        })
        return response

admin_site = QLDLAppAdminSite('Manage travel tour')


class TourImageInline(admin.StackedInline):
    model = TourImage
    pk_name = 'tour'


class TourAdmin(admin.ModelAdmin):
    inlines = (TourImageInline, )


class TourInline(admin.StackedInline):
    model = Tour
    pk_name = 'loai_tour'
    readonly_fields = ['picture']

    def picture(self, obj):
        if obj:
            return mark_safe(
                '<img src="/static/{url}" width="420" />' \
                    .format(url=obj.hinh_anh.name)
            )


class LoaiTourAdmin(admin.ModelAdmin):
    inlines = (TourInline, )


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined']
    readonly_fields = ['avatar_user']
    ordering = ['-id']

    def avatar_user(self, obj):
        if obj:
            return mark_safe(
            '<img src="/static/{url}" width="120" />'\
            .format(url=obj.avatar.name)
    )


class TourImageAdmin(admin.ModelAdmin):
    readonly_fields = ['picture']

    def picture(self, obj):
        if obj:
            return mark_safe(
                '<img src="/static/{url}" width="420" />' \
                    .format(url=obj.hinh_anh.name)
            )


class TinTucImageInline(admin.StackedInline):
    model = TinTucImage
    pk_name = 'tin_tuc'


class TinTucAdmin(admin.ModelAdmin):
    inlines = (TinTucImageInline,)
    readonly_fields = ['picture']

    def picture(self, obj):
        if obj:
            return mark_safe(
                '<img src="/static/{url}" width="420" />' \
                    .format(url=obj.hinh_anh.name)
            )

admin_site.register(Tour, TourAdmin)
admin_site.register(TourImage, TourImageAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(TinTuc, TinTucAdmin)
admin_site.register(LoaiTour)
