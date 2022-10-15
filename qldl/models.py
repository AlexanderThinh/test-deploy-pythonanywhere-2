from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ngay_sinh = models.DateTimeField(auto_now_add=True)
    gioi_tinh = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='uploads/%Y/%m', default=None)
    so_dien_thoai = models.CharField(max_length=20)
    role = models.ForeignKey('Role', related_name='users', on_delete=models.SET_NULL, null=True)


class Role(models.Model):
    role_name = models.CharField(max_length=50, null=False, unique=True)

    def __str__(self):
        return self.role_name


class LoaiTour(models.Model):
    ten_loai_tour = models.CharField(max_length=50, null=False, unique=True)

    def __str__(self):
        return self.ten_loai_tour

class Tour(models.Model):
    ten_tour = models.CharField(max_length=50, null=False)
    ngay_bat_dau = models.DateTimeField(auto_now_add=True)
    ngay_ket_thuc = models.DateTimeField(auto_now_add=True)
    thoi_gian = models.IntegerField(default=0)
    don_gia = models.FloatField(default=0)
    so_cho = models.IntegerField(default=0)
    noi_khoi_hanh = models.CharField(max_length=50, null=False)
    hinh_anh = models.ImageField(upload_to='uploads/%Y/%m', default=None)
    loai_tour = models.ForeignKey(LoaiTour, related_name='tours', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.ten_tour


class TourImage(models.Model):
    name = models.CharField(max_length=50, null=True)
    hinh_anh = models.ImageField(upload_to='uploads/%Y/%m', default=None)
    tour = models.ForeignKey(Tour, related_name='images', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class LichTrinh(models.Model):
    ngay = models.IntegerField(default=1)
    tieu_de = models.TextField(null=False)
    noi_dung = models.TextField(null=False)
    tour = models.ForeignKey(Tour, related_name='lichtrinh', on_delete=models.CASCADE)

    def __str__(self):
        return self.tieu_de


class LoaiVe(models.Model):
    loai_ve = models.CharField(max_length=50, null=False)
    don_gia = models.FloatField(default=0)

    def __str__(self):
        return self.loai_ve


class DonDatTour(models.Model):
    loai_ve = models.ForeignKey(LoaiVe, related_name='dondattour', on_delete=models.SET_NULL, null=True)
    don_gia = models.FloatField(default=0)
    so_luong = models.IntegerField(default=0)
    tong_tien = models.FloatField(default=0, null=True, blank=True)
    khach_hang = models.ForeignKey(User, related_name='dondattour', on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, related_name='dondattour', on_delete=models.CASCADE)
    da_thanh_toan = models.BooleanField(default=False)


class TinTuc(models.Model):
    chu_de = models.TextField(null=False)
    short_desc = models.TextField(null=True)
    noi_dung = models.TextField(null=False)
    hinh_anh = models.ImageField(upload_to='uploads/%Y/%m', default=None)
    ngay_dang = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.chu_de


class TinTucImage(models.Model):
    name = models.CharField(max_length=50, null=False)
    hinh_anh = models.ImageField(upload_to='uploads/%Y/%m', default=None)
    tin_tuc = models.ForeignKey(TinTuc, related_name='images', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name


class BaseAction(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CommentTour(BaseAction):
    noi_dung = models.TextField()
    khach_hang = models.ForeignKey(User, related_name='commenttour', on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, related_name='commenttour', on_delete=models.CASCADE)

    def __str__(self):
        return self.noi_dung


class CommentTinTuc(BaseAction):
    noi_dung = models.TextField()
    khach_hang = models.ForeignKey(User, related_name='commenttin', on_delete=models.CASCADE)
    tin_tuc = models.ForeignKey(TinTuc, related_name='commenttin', on_delete=models.CASCADE)

    def __str__(self):
        return self.noi_dung


class Rating(BaseAction):
    rate = models.PositiveSmallIntegerField(default=0)
    khach_hang = models.ForeignKey(User, related_name='rating', on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, related_name='rating', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('khach_hang', 'tour')


class Like(BaseAction):
    liked = models.BooleanField(default=False)
    khach_hang = models.ForeignKey(User, related_name='like', on_delete=models.CASCADE)
    tin_tuc = models.ForeignKey(TinTuc, related_name='like', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('khach_hang', 'tin_tuc')

