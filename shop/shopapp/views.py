from decimal import Decimal
from django.shortcuts import render,redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import auth
from django.contrib import messages
from . import forms 
from . import models
from . import sentiment
import urllib.parse
import qrcode
from io import BytesIO
import base64
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


def index(request):
        categories = models.Category.objects.all()
        latest_products = models.Product.objects.order_by('-created_at')[:12]
        featured_products = models.Product.objects.order_by('-sentiment_score')[:12]
        if request.user.is_authenticated:
            user_type = request.user.user_type
            username = request.user
            return render(request, 'index.html',{
                      'categories':categories,
                      'latest_products':latest_products,
                      'featured_products':featured_products, 
                      'user_type':user_type, 
                      'username':username})
        else:
          return render(request, 'index.html',{
                      'categories':categories,
                      'latest_products':latest_products,
                      'featured_products':featured_products})   


def product_upload(request):
        form = forms.productUploadForm()
        if request.method == 'POST':

                form = forms.productUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    product = form.save(commit=False)
                    product.trader_name = request.user 
                    product.save()
                    return redirect("traders.html")
                else:
                        form = forms.productUploadForm()
                        return render(request, "productupload.html", {"form": form})
                        
        else:
                return render(request, 'productupload.html', {"form": form})
        
def traders_page(request, username):
    trader = get_object_or_404(models.customuser, username=username, user_type='Trader')
    user_type = request.user.user_type
    products = models.Product.objects.filter(trader_name=trader).order_by('-sentiment_score')

    return render(request, 'traders.html', {'products': products, 'trader': trader, 'user_type':user_type})

def search(request):
       if request.method == 'POST':
              searched = request.POST['searched']
              matches = models.Product.objects.filter(name__contains=searched)
              number = len(matches)
              return render(request, 'search.html', {'searched': searched, 'matches':matches, 'number':number})
       else:
              return render(request, 'search.html')
       

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        user_type = request.POST['user_type']


        if password == password2:
            if models.customuser.objects.filter(email=email).exists():
                messages.info(request, 'Email already in use!')
                return redirect('signup')
            elif models.customuser.objects.filter(username=username).exists():
                messages.info(request, 'Username already in use!')
                return redirect('signup')
            else:
                user = models.customuser.objects.create_user(username=username, email=email, password=password, user_type=user_type)
                user.save();
                return redirect('login')

            
        else:
            messages.info(request, 'Passwords do not match!')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = models.customuser.objects.get(username=username)
            user_type = user.user_type

            user = auth.authenticate(username=username, password=password)
        except Exception:
            messages.info(request, 'Invalid Credentials!')
            return redirect('login')
        

        if user is not None:
            auth.login(request, user)
            if user_type == 'Trader':
                return redirect('traders_page', username=username)
            else:
                return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials!')
            return redirect('login')
        
    else:
        return render(request, 'login.html')
    
def logout(request):
    auth.logout(request)
    return redirect('/')


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    product = get_object_or_404(models.Product, id=product_id)
    cart, created = models.Cart.objects.get_or_create(
            user=request.user
        )
    cart_item, created = models.cartItems.objects.get_or_create(
         cart=cart,
         product=product
                 )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()


def page_view(request, slug):
    category = get_object_or_404(models.Category, slug=slug)
    products = models.Product.objects.filter(category=category).order_by('-sentiment_score')
    user_type = request.user.user_type
    return render(request, 'category.html', {'category': category, 'products': products, 'user_type' : user_type})


def category_view(request):
    categories = models.Category.objects.all()
    user_type = request.user.user_type
    return render(request, 'categories.html', {'categories':categories,
                                                'user_type' : user_type})


def product_page(request, slug):
    product = get_object_or_404(models.Product, slug=slug)
    user_type = request.user.user_type
    return render(request, 'product_detail.html', {'product': product,
                                                   'user_type' : user_type})


def my_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    cart_items = models.cartItems.objects.filter(user=request.user)
    total1 = Decimal()
    total2 = Decimal()
    for item in cart_items:
        total1 = item.product.price * item.quantity
        total2 += item.product.price * item.quantity

    return render(request, 'mycart.html', {'cart_items': cart_items, 'total1':total1, 'total2':total2})



def edit_product(request, product_id):
    
    product = get_object_or_404(models.Product, id=product_id, user=request.user)

    if request.method == 'POST':
        form = forms.productUploadForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('traders_page', username=request.user.username)
    else:
        form = forms.productUploadForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})


def submit_review(request, product_id):
    if request.method == 'POST':
        review_text = request.POST.get('review')
        product = get_object_or_404(models.Product, id=product_id)

        # Analyze the sentiment of the review
        sentiment_category, compound_score = sentiment.analyze_review(review_text)

        # Save the review with the sentiment
        review = models.Review.objects.create(
            user=request.user,
            product=product,
            review_text=review_text,
            sentiment=sentiment_category )
        review.save()
        rating = int((compound_score + 1) * 5)
        product.sentiment_score = rating
        product.save()

        # Update trader's average rating
        trader = product.trader_name
        trader_products = models.Product.objects.filter(trader=trader)
        
        trader.average_rating = trader_products.aggregate(models.Avg('sentiment_score'))['sentiment_score__avg']
        trader.save()

        
        return redirect('product_page', product_id=product.id)


@api_view(['POST'])
def create_solana_payment(request):
    """
    Generates a Solana Pay payment link and QR code.
    """
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "User not authenticated"}, status=401)

    # Retrieve cart and calculate total amount
    cart = get_object_or_404(models.Cart, user=user, checked_out=False)
    total_amount = sum(item.product.price * item.quantity for item in cart.cartitems.all())

    if total_amount <= 0:
        return Response({"error": "Invalid amount"}, status=400)

    receiver_wallet = "8N2sV5LNeoY5QmeRiPfgyCQi1T3VALFRfDJv7XcnhDto"

    # Construct Solana Pay URL (properly encoded)
    base_url = f"solana:{receiver_wallet}?amount={total_amount}&spl-token=sol&label=Marketplace+Payment"
    encoded_url = urllib.parse.quote(base_url, safe=":/?=&")

    # Generate QR Code
    qr = qrcode.make(encoded_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return Response({
        "payment_url": encoded_url,
        "qr_code": qr_base64
    })


    

def confirm_payment(request, pk):
    cart = models.Cart.objects.get(id=pk, user=request.user)
    
    if cart.checked_out:
        messages.error(request, 'This cart has already been checked out.')
        return redirect('index')

    response = create_solana_payment(request)
    
    if response.status_code == 200:
        cart.checked_out = True
        cart.save()
        messages.success(request, 'Payment initiated. Please confirm in your Solana wallet.')
    else:
        messages.error(request, 'Payment failed. Please try again.')

    return redirect('index')
