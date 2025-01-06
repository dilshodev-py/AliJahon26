from datetime import datetime, timedelta, timezone

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView

from apps.forms import LoginForm, ProfileModelForm, OrderForm
from apps.models import Product, Category, User, Region, District, WishList, Order, Thread


# Create your views here.
class HomeListView(ListView):
    queryset = Product.objects.all().order_by('-created_at')
    template_name = 'apps/site/home.html'
    context_object_name = "products"

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        data['categories'] = Category.objects.all()
        return data


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'apps/order/product-detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

class OrderFormView(FormView):
    form_class = OrderForm
    template_name = "apps/order/success.html"
    success_url = reverse_lazy("order")

    def form_valid(self, form):
        data  = form.cleaned_data
        Order.objects.create(**data , user = self.request.user)
        return super().form_valid(form)



class MarketListView(ListView):
    queryset = Category.objects.all()
    template_name = 'apps/site/market.html'
    context_object_name = "categories"

    def get_context_data(self, *, object_list=None, **kwargs):
        slug = self.kwargs.get('slug')
        data= super().get_context_data(object_list=object_list, **kwargs)
        products = Product.objects.all().order_by('-created_at')
        if slug != "all":
            products = products.filter(category__slug=slug)
        data['products'] = products
        data['slug'] = slug
        return data




class CategoryListView(ListView):
    queryset = Category.objects.all()
    template_name = 'apps/site/category-list.html'
    context_object_name = "categories"

    def get(self, request, *args, **kwargs):
        self.slug = kwargs.get('slug')
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        slug = self.slug
        products = Product.objects.select_related('category').all()
        if slug != 'all':
            products = products.filter(category__slug=slug)
        data['products'] = products
        data['slug'] = slug
        return data

# ====================== TODO auth ======================================
class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'apps/auth/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        data = form.cleaned_data
        phone_number = data.get("phone_number")
        password = form.data.get("password")
        hash_password = data.get("password")
        query_set = User.objects.filter(phone_number = phone_number)
        if query_set.exists():
            user = query_set.first()
            if user.check_password(password):
                login(self.request , user)
            else:
                messages.error(self.request , "Parol xato !")
                return redirect('login')
        else:
            user = User.objects.create(password=hash_password,phone_number = phone_number)
            login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request , "\n".join([error[0] for error in form.errors.values()]))
        return super().form_invalid(form)


class ProfileFormView(FormView):
    form_class =ProfileModelForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        data =  super().get_context_data(**kwargs)
        data['regions'] = Region.objects.all()
        return data

    def form_valid(self, form):
        user = self.request.user
        User.objects.filter(id=user.id).update(**form.cleaned_data)
        return super().form_valid(form)
def get_districts(request):
    region_id = request.GET.get('region_id')
    if region_id:
        districts = District.objects.filter(region_id=region_id).values('id', 'name')
        return JsonResponse(list(districts), safe=False)
    return JsonResponse({'error': 'No region selected'}, status=400)


def wishlist_view(request):
    product_id = request.POST.get('product_id')
    query_set = request.user.wishlists.filter(product_id=product_id)
    response = False
    if query_set.exists():
        query_set.delete()
    else:
        query_set.create(product_id = product_id , user = request.user)
        response = True
    return JsonResponse({"response" : response})




class WishListView(ListView):
    queryset = WishList.objects.all()
    template_name = 'apps/site/wish-list.html'
    context_object_name = 'wishlists'

    def get_queryset(self):
        query =  super().get_queryset()
        return query.filter(user = self.request.user)


# ========================== statistic thread ========================

# class ThreadStatisticListView(LoginRequiredMixin,ListView):
#     queryset = Thread.objects.all()
#     login_url = reverse_lazy('login')
#     template_name = 'apps/order/statistic-list.html'
#     context_object_name = "threads"
#
#     def get_context_data(self, *args, **kwargs):
#         data = super().get_context_data(*args , **kwargs)
#         query = self.get_queryset().aggregate(
#             new_all = Sum("new_order"),
#         )
#         print(query)
#         data.update(query)
#         return data
#
#     def get_queryset(self):
#         query = super().get_queryset()
#         user = self.request.user
#         period = self.request.GET.get('period')
#         today = datetime.now().date()
#         time_condition = Q(orders__ordered_at__date__lte = today)
#         if period:
#             time_dict = {
#                 'today': (today, today),
#                 'last_day': (today - timedelta(days=1), today - timedelta(days=1)),
#                 'wekly': (today - timedelta(days=7), today),
#                 'monthly': (today - timedelta(days=30), today)
#             }
#             time_condition = Q(orders__ordered_at__date__range=time_dict.get(period))
#
#         query = query.filter(user=user).annotate(
#             new_order = Count("orders" , filter=Q(orders__status=Order.StatusType.NEW) & time_condition),
#         ).values("title" , "product__name" , "visit_count" , "new_order" , "orders__ordered_at")
#         return query

class ThreadStatisticListView(LoginRequiredMixin, ListView):
    queryset = Thread.objects.all()
    template_name = 'apps/order/statistic-list.html'
    context_object_name = 'threads'

    def get_queryset(self, *args, **kwargs):
        now = datetime.now()
        period = self.request.GET.get('period')

        periods = {
            'today': now.replace(hour=0, minute=0, second=0),
            'last_day': now.replace(hour=0, minute=0, second=0) - timedelta(days=1),
            'wekly': now - timedelta(days=now.weekday()),
            'monthly': now.replace(day=30),
        }
        start_date = periods.get(period)

        qs = super().get_queryset().filter(user=self.request.user)
        if start_date:
            qs = qs.filter(orders__ordered_at__gte=start_date)
        qs = qs.annotate(
            new=Count('orders', filter=Q(orders__status=Order.StatusType.NEW)),
            # ready=Count('orders', filter=Q(orders__status=Order.StatusType.READY)),
            # deliver=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERING)),
            # delivered=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERED)),
            # cant_phone=Count('orders', filter=Q(orders__status=Order.StatusType.CANT_PHONE)),
            # broken=Count('orders', filter=Q(orders__status=Order.StatusType.BROKEN)),
            # canceled=Count('orders', filter=Q(orders__status=Order.StatusType.CANCELED)),
            # archived=Count('orders', filter=Q(orders__status=Order.StatusType.ARCHIVED)),
        )
        qs.thread = qs.aggregate(
            all_visit=Sum('visit_count'),
            new_all=Sum(Order.StatusType.NEW),
            # total_ready_count=Sum(Order.StatusType.READY),
            # total_deliver_count=Sum('deliver'),
            # total_delivered_count=Sum(Order.StatusType.DELIVERED),
            # total_cant_phone_count=Sum(Order.StatusType.CANT_PHONE),
            # total_broken_count=Sum(Order.StatusType.BROKEN),
            # total_canceled_count=Sum(Order.StatusType.CANCELED),
            # total_archived_count=Sum(Order.StatusType.ARCHIVED),
        )
        return qs



# Check user role == operator:
#     menudan operator panel degan button qoshilsin
#     operator html ochib berilsin !








