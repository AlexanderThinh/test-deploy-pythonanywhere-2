from django.contrib.auth.models import Group
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import *


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField(source='avatar')

    def get_avatar(self, obj):
        request = self.context['request']
        if obj.avatar and not obj.avatar.name.startswith("/static"):
            path = '/static/%s' % obj.avatar.name

            return request.build_absolute_uri(path)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'ngay_sinh', 'so_dien_thoai', 'role']
        # Khong do DL password ra ngoai
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(validated_data['password'])
        user.role_id = 3
        user.save()

        return user


class TourSerializer(ModelSerializer):
    hinh_anh = SerializerMethodField(source='hinh_anh')

    def get_hinh_anh(self, tour):
        request = self.context['request']

        name = tour.hinh_anh.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    class Meta:
        model = Tour
        fields = '__all__'


class LoaiTourSerializer(ModelSerializer):
    tours = TourSerializer

    class Meta:
        model = LoaiTour
        fields = '__all__'


class TourDetailSerializer(TourSerializer):
    rate = SerializerMethodField(source='rating')
    hinh_anh = SerializerMethodField(source='hinh_anh')
    loai_tour = LoaiTourSerializer()

    def get_hinh_anh(self, tour):
        request = self.context['request']

        name = tour.hinh_anh.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    def get_rate(self, tour):
        request = self.context['request']

        if request and request.user.is_authenticated:
            r = tour.rating.filter(khach_hang=request.user).first()
            if r:
                return r.rate
        return -1

    class Meta:
        model = TourSerializer.Meta.model
        fields =TourSerializer.Meta.fields


class TourImageSerializer(ModelSerializer):
    tour = TourSerializer()
    hinh_anh = SerializerMethodField(source='hinh_anh')

    def get_hinh_anh(self, tour):
        request = self.context['request']

        name = tour.hinh_anh.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    class Meta:
        model = TourImage
        fields = '__all__'


class LoaiVeSerializer(ModelSerializer):
    class Meta:
        model = LoaiVe
        fields = '__all__'


class DonDatTourSerializer(ModelSerializer):
    class Meta:
        model = DonDatTour
        fields = '__all__'


class TinTucSerializer(ModelSerializer):
    class Meta:
        model = TinTuc
        fields = '__all__'

class TinTucDetailSerializer(TinTucSerializer):
    like = SerializerMethodField()
    hinh_anh = SerializerMethodField(source='hinh_anh')

    def get_hinh_anh(self, tour):
        request = self.context['request']

        name = tour.hinh_anh.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    def get_like(self, tin_tuc):
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            l = tin_tuc.like.filter(khach_hang=request.user).first()
            if l:
                return l.liked

        return False

    class Meta:
        model = TinTucSerializer.Meta.model
        fields = TinTucSerializer.Meta.fields

class TinTucImageSerializer(ModelSerializer):
    tin_tuc = TinTucSerializer()

    class Meta:
        model = TinTucImage
        fields = '__all__'


class CreateCommentTourSerializer(ModelSerializer):
    class Meta:
        model = CommentTour
        fields = ['id', 'noi_dung', 'khach_hang', 'tour', 'created_date']


class CommentTourSerializer(ModelSerializer):
    khach_hang = UserSerializer()

    class Meta:
        model = CommentTour
        fields = ['id', 'noi_dung', 'khach_hang', 'tour', 'created_date']


class CommentTinTucSerializer(ModelSerializer):
    khach_hang = UserSerializer()

    class Meta:
        model = CommentTinTuc
        fields = '__all__'


class LikeTinTucSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class LichTrinhSerializer(ModelSerializer):
    class Meta:
        model = LichTrinh
        fields = '__all__'


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

