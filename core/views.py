from django.shortcuts import render, redirect #render for webpage view
# redirect for preventing accidental double form submissions
from django.contrib.auth.decorators import login_required
#redirects unauthenticated users to the login page
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Item
from .forms import ItemForm
from .models import Claim
from .forms import ClaimForm


@login_required
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        #request.POST contains form text data
        #request.FILES contains uploaded files(e.g. images)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect('dashboard') #Prevents duplicate form submission
    else:
        form = ItemForm()
    return render(request, 'create_item.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    
    my_items = Item.objects.filter(user=user) #Uses Django ORM filter with foreign key relationship
    open_found = Item.objects.found().open() #chain methods
    open_lost = Item.objects.lost().open()
    
    claims_made = Claim.objects.filter(claimer = user)
    claims_received = Claim.objects.filter(item__user=user, status='PENDING')
    
    context = {
        'my_items': my_items,
        'open_found': open_found,
        'open_lost': open_lost,
        'claims_made': claims_made,
        'claims_received': claims_received,
    }

    return render(request, 'dashboard.html', context)
    

@login_required
def submit_claim(request, item_id):
    item = get_object_or_404(Item, pk = item_id)
    
    if item.user == request.user:
        return redirect('home')

    if request.method == 'POST': #HTTP method used to send data to the server to create or update a resource
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item #set foreign keys(Item, current user)
            claim.claimer = request.user
            claim.save()
            return redirect('home')
    else:
        form = ClaimForm()

    return render(request, 'submit_claim.html', {'form': form, 'item': item})

@login_required
def approve_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    try:
        claim.approve(acting_user=request.user)
        messages.success(request, f"Claim on '{claim.item.title}' approved!")
    except PermissionDenied as e:
        messages.error(request, str(e))
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('home')


@login_required
def reject_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    try:
        claim.reject(acting_user=request.user)
        messages.success(request, f"Claim on '{claim.item.title}' rejected!")
    except PermissionDenied as e:
        messages.error(request, str(e))
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('home')