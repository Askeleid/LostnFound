from django.shortcuts import render, redirect #render for webpage view
# redirect for preventing accidental double form submissions
from django.contrib.auth.decorators import login_required
#redirects unauthenticated users to the login page
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
    my_items = Item.objects.filter(user=request.user) #Uses Django ORM filter with foreign key relationship
    open_found = Item.objects.found().open() #chain methods
    open_lost = Item.objects.lost().open()

    return render(request, 'dashboard.html', {
        'my_items': my_items,
        'open_found': open_found,
        'open_lost': open_lost,
    })
    

@login_required
def submit_claim(request, item_id):
    item = Item.objects.get(id=item_id)

    if request.method == 'POST': #HTTP method used to send data to the server to create or update a resource
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item #set foreign keys(Item, current user)
            claim.claimer = request.user
            claim.save()
            return redirect('dashboard')
    else:
        form = ClaimForm()

    return render(request, 'submit_claim.html', {'form': form, 'item': item})