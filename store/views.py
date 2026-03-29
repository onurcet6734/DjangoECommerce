from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q, F
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from django.core.paginator import Paginator
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, Customer, Address, Comment
from store.models import CommentForm
from .payments.iyzico import IyzicoPayment
from .payments.stripe import StripePayment


# ---------------------------------------------------------------------------
# IndexView
# ---------------------------------------------------------------------------

class IndexView(View):
    """
    Ürün listeleme view'i.

    İyileştirmeler:
    - Paginator eklendi: arama/kategori filtrelemesinde büyük
      ürün setlerini sayfalayarak hem DB hem render yükü azaltıldı.
    """

    def get(self, request):
        # Sıralama: oluşturulma tarihine göre sabit; ürün güncellenince sayfa
        # konumu değişmez.
        products = Product.objects.select_related("category").order_by("created_at")

        category_id = request.GET.get("category_id")
        if category_id:
            products = products.filter(category_id=category_id)

        search_query = request.GET.get("q")
        if search_query:
            products = products.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Sayfalama — sayfa boyutu settings.py'dan okunur (varsayılan: 12)
        page_size = getattr(settings, "PAGINATION_PAGE_SIZE", 12)
        paginator = Paginator(products, page_size)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        total_item_count = 0
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                total_item_count = Order.objects.filter(customer=customer , is_completed=False).count()
            except Customer.DoesNotExist:
                pass

        context = {
            "products": page_obj,          # QuerySet yerine Page objesi
            "page_obj": page_obj,          # Template'de pagination widget için
            "total_item_count": total_item_count,
            "search_query": search_query,
        }
        return render(request, "index.html", context)


# ---------------------------------------------------------------------------
# RegisterView  (YENİ)
# ---------------------------------------------------------------------------

class RegisterView(View):
    """
    Yeni kullanıcı kayıt view'i.

    - Django'nun yerleşik UserCreationForm'unu kullanır.
    - Kayıt başarılı olursa ilgili Customer nesnesi otomatik oluşturulur
      ve kullanıcı oturumu açılır.
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = UserCreationForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("index")

        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # İlgili Customer kaydını hemen oluştur
            Customer.objects.create(user=user)

            # Kullanıcıyı otomatik olarak giriş yaptır
            login(request, user)
            return redirect("index")

        return render(request, "register.html", {"form": form})


# ---------------------------------------------------------------------------
# HandledLoginView
# ---------------------------------------------------------------------------

class HandledLoginView(View):

    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            try:
                customer = Customer.objects.get(user=user)
                customer.update_name_from_user()

                response = redirect("index")
                response.set_cookie("customer_id", customer.id)  # pk kullan, nesne değil
                return response
            except Customer.DoesNotExist:
                return redirect("index")

        return render(request, "login.html", {"message": "Geçersiz kullanıcı adı veya şifre!"})


# ---------------------------------------------------------------------------
# CartView
# ---------------------------------------------------------------------------

class CartView(View):

    @method_decorator(login_required)
    def get(self, request):
        orders = Order.objects.select_related("customer", "product").filter(
            customer__user=request.user,
            is_completed=False
        )

        total_price_sum = orders.aggregate(Sum("total_price"))["total_price__sum"]
        total_item_count = orders.count()

        cargo_price = 0 if (total_price_sum and total_price_sum > 5000) else 20

        context = {
            "orders": orders,
            "total_price_sum": total_price_sum,
            "total_item_count": total_item_count,
            "cargo_price": cargo_price,
        }
        return render(request, "cart.html", context)


# ---------------------------------------------------------------------------
# DeleteOrderView
# ---------------------------------------------------------------------------

class DeleteOrderView(View):

    @method_decorator(login_required)
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, is_completed=False, customer__user=request.user)            
        order.delete()
        return redirect("cart")


# ---------------------------------------------------------------------------
# ProductDetailView
# ---------------------------------------------------------------------------

class ProductDetailView(View):
    """
    İyileştirmeler:
    - GET: Anonim kullanıcı için get_or_create yerine is_authenticated kontrolü;
      böylece AnonymousUser ile Customer(OneToOne) arasında hata riski ortadan kalkar.
    - Comment filtresi: filter(product=product) → daha net ve bakımı kolay.
    """

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        total_item_count = 0
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                total_item_count = Order.objects.filter(customer=customer, is_completed=False).count()
            except Customer.DoesNotExist:
                pass

        # Alan adına göre net filtreleme (product_id yerine product FK)
        comments = Comment.objects.select_related("customer", "product").filter(
            product_id=product_id
        )

        return render(
            request,
            "detail.html",
            {
                "comments": comments,
                "product": product,
                "total_item_count": total_item_count,
            },
        )

    @method_decorator(login_required)
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        customer, _ = Customer.objects.get_or_create(user=request.user)

        quantity = int(request.POST.get("quantity", 1))

        try:
            order = Order.objects.get(customer=customer, product=product , is_completed=False)
            order.quantity += quantity
            order.total_price = product.price * order.quantity
            order.save()
        except Order.DoesNotExist:
            Order.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                total_price=product.price * quantity,
                is_completed=False
            )

        return redirect("cart")


# ---------------------------------------------------------------------------
# AddCommentView
# ---------------------------------------------------------------------------

class AddCommentView(View):

    @method_decorator(login_required)
    def post(self, request, product_id):
        url = request.META.get("HTTP_REFERER")
        customer = Customer.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id)

        check_completed = Order.objects.filter(
            customer=customer, is_completed=True
        ).exists()

        if check_completed:
            form = CommentForm(request.POST)
            if form.is_valid():
                Comment.objects.create(
                    customer=customer,
                    product=product,
                    comment=form.cleaned_data["comment"],
                    rate=form.cleaned_data["rate"],
                )
                return redirect(url)

        return redirect("index")


# ---------------------------------------------------------------------------
# CheckoutView
# ---------------------------------------------------------------------------

class CheckoutView(View):

    @method_decorator(login_required)
    def get(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        orders = Order.objects.filter(customer=customer, is_completed=False)

        if not orders.exists():
            return redirect("index")

        total_price_sum = orders.aggregate(Sum("total_price"))["total_price__sum"]
        total_item_count = orders.count()

        context = {
            "total_price_sum": total_price_sum,
            "total_item_count": total_item_count,
        }
        return render(request, "address_form.html", context)


# ---------------------------------------------------------------------------
# PaymentCheckoutView
# ---------------------------------------------------------------------------

class PaymentCheckoutView(View):
    """
    İyileştirmeler:
    - transaction.atomic() ile adres oluşturma ve ödeme başlatma güvenli hale getirildi.
    - Aynı sipariş için tekrar adres oluşturulmasını önlemek amacıyla
      mevcut adresler önce siliniyor (idempotent strateji).
    """

    @method_decorator(login_required)
    def post(self, request):
        payment_method = request.POST.get("payment_method")

        address_data = {
            "address_line1": request.POST.get("address_line1"),
            "address_line2": request.POST.get("address_line2"),
            "city": request.POST.get("city"),
            "state": request.POST.get("state"),
            "postal_code": request.POST.get("postal_code"),
        }

        customer = get_object_or_404(Customer, user=request.user)

        orders = Order.objects.filter(
            customer=customer, is_completed=False
        ).select_related("product")

        if not orders.exists():
            return redirect("cart")

        with transaction.atomic():
            # Mevcut adresleri temizle (tekrar denemede yinelemeyi önler)
            Address.objects.filter(order__in=orders).delete()

            # Tüm adresleri tek seferde toplu oluştur
            Address.objects.bulk_create(
                [Address(order=order, **address_data) for order in orders]
            )

        if payment_method == "stripe":
            stripe_payment = StripePayment()
            checkout_session = stripe_payment.create_checkout_session(
                orders=orders, request=request
            )
            return redirect(checkout_session.url, code=303)

        elif payment_method == "iyzico":
            iyzico_payment = IyzicoPayment()
            payment_url = iyzico_payment.create_checkout_form(
                request=request, orders=orders, customer=customer
            )
            return redirect(payment_url)

        return redirect("cart")


# ---------------------------------------------------------------------------
# SuccessView
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class SuccessView(View):
    """
    Stripe GET / IyziCo POST callback handler.

    İyileştirmeler:
    - complete_orders: transaction.atomic() + select_for_update() ile
      eşzamanlı ödeme (race condition) senaryosunda stok tutarsızlığı önlendi.
    - F() expression ile stok düşme DB'de atomik yapıldı (Python tarafında
      stok okuma gerektirmez).
    - Siparişler bulk_update ile tek SQL sorgusunda tamamlandı.
    - Stripe callback: oturuma bağımlı olmayan session_id doğrulaması korundu;
      müşteri session'dan değil Stripe metadata'sından alınacak şekilde
      genişletmeye hazır bir not eklendi.
    """

    def get(self, request):
        """Stripe success redirect"""
        payment_type = request.GET.get("payment_type")

        if payment_type == "stripe":
            session_id = request.GET.get("session_id")
            if not session_id:
                return render(request, "success.html")

            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                # NOT: Stripe'ın oturum meta verisi üzerinden customer_id
                # alınması, kullanıcı giriş yapmasa bile çalışır.
                # Örnek: customer_id = session.metadata.get("customer_id")
                # Şimdilik mevcut oturum tabanlı akış korunuyor.
                if request.user.is_authenticated:
                    customer = get_object_or_404(Customer, user=request.user)
                    self.complete_orders(customer=customer)

        return render(request, "success.html")

    def post(self, request):
        """IyziCo callback"""
        payment_type = request.GET.get("payment_type")

        if payment_type == "iyzico":
            conversation_id = request.GET.get("conversationId")
            token = request.POST.get("token")

            if token and conversation_id:
                customer = get_object_or_404(Customer, id=conversation_id)
                self.complete_orders(customer=customer)

        return render(request, "success.html")

    @staticmethod
    def complete_orders(customer):
        """
        Siparişleri tamamla ve stokları düş.

        - select_for_update(): Aynı anda gelen iki ödeme isteğinin aynı
          stok satırını okumasını engeller (race condition koruması).
        - F() expression: Stok düşme işlemi Python'a çekilmeden DB'de atomik
          olarak gerçekleşir.
        - bulk_update(): Tüm order güncelleme işlemi tek SQL sorgusuna indirilir.
        """
        if not customer:
            return

        with transaction.atomic():
            orders = (
                Order.objects.select_for_update()
                .filter(customer=customer, is_completed=False)
                .select_related("product")
            )

            if not orders.exists():
                return

            # Stok düşme: her ürün için F() ile atomik güncelleme
            for order in orders:
                Product.objects.filter(pk=order.product_id).update(
                    stock=F("stock") - order.quantity
                )

            # Siparişleri tek sorguda tamamla
            orders.update(is_completed=True)