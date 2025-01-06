from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, ImageField, CharField, TextField, DecimalField, DateTimeField, ForeignKey, CASCADE, \
    SlugField, SET_NULL, IntegerField, SmallIntegerField, TextChoices
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(UserManager):
    def _create_user(self, phone_number, email, password, **extra_fields):

        if not phone_number:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)


class Region(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class User(AbstractUser):
    phone_number = PhoneNumberField(region='UZ', unique=True)
    username = None
    objects = CustomUserManager()
    USERNAME_FIELD = "phone_number"
    address = CharField(max_length=255, null=True, blank=True)
    telegram_id = CharField(max_length=50, null=True, blank=True)
    description = TextField(null=True, blank=True)
    district = ForeignKey('apps.District', SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return self.phone_number


class BaseSlug(Model):
    class Meta:
        abstract = True

    name = CharField(max_length=255)
    slug = SlugField()
    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        slug = slugify(self.name)
        while self.__class__.objects.filter(slug=self.slug).exists():
            slug += "-1"
        self.slug = slug
        return super().save(*args,
                            force_insert=False,
                            force_update=False,
                            using=None,
                            update_fields=None, )


class Category(BaseSlug):
    image = CharField(max_length=500)

    def __str__(self):
        return self.name


class Product(BaseSlug):
    description = TextField()
    price = DecimalField(max_digits=9, decimal_places=2)
    image = ImageField(upload_to="products/")
    created_at = DateTimeField(auto_now_add=True)
    seller_price = IntegerField(default=0)
    quantity = IntegerField(default=1)
    category = ForeignKey('apps.Category', CASCADE, related_name='products')

    def __str__(self):
        return self.name

class WishList(Model):
    product = ForeignKey('apps.Product' , CASCADE , related_name='wishlists')
    user = ForeignKey('apps.User' , CASCADE , related_name='wishlists')


class Thread(Model):
    title = CharField(max_length=255)
    user = ForeignKey("apps.User" , CASCADE , related_name='threads')
    product = ForeignKey('apps.Product' , CASCADE , related_name="threads")
    discount_price = IntegerField(default=0)
    visit_count = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

class Order(Model):
    class StatusType(TextChoices):
        NEW = "new" , "New"
        READY_TO_START = "ready_to_start" , "Ready To Start"
        BEING_DELIVERED = "being_delivered" , "Being Delivered"
        DELIVERED = "delivered" , "Delivered"
        PHONE_CANCELED = "phone_canceled" , "Phone Canceled"
        CANCELED = "canceled" , "Canceled"
        ARCHIVE = "archive" , "Archive"

    name = CharField(max_length=255)
    phone_number = PhoneNumberField(region="UZ")
    user = ForeignKey("apps.User" , SET_NULL , null=True , blank=True , related_name="orders")
    product = ForeignKey("apps.Product" , SET_NULL ,null=True , blank=True, related_name="orders")
    quantity = SmallIntegerField(default=1)
    amount = DecimalField(max_digits=10 , decimal_places=2)
    ordered_at = DateTimeField(auto_now_add=True)
    thread = ForeignKey("apps.Thread" , SET_NULL , null=True , blank=True , related_name="orders")
    status = CharField(max_length=50 , choices=StatusType.choices , default=StatusType.NEW)

