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
from .models import Profile
from .forms import ClaimForm
from django.core.mail import send_mail
from .models import Notification
from .utils.matching import match_items
from django.contrib.auth import login
from django.contrib.auth import logout
from .forms import RegisterForm
from .models import Profile


def logout_user(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Profile already auto-created via signal
            profile = user.profile

            # Only store phone later; nothing required now
            profile.save()

            login(request, user)
            return redirect('home')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

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
            return redirect('home') #Prevents duplicate form submission
    else:
        form = ItemForm()
    return render(request, 'create_item.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    
    my_items = Item.objects.filter(user=user) #Uses Django ORM filter with foreign key relationship
    open_found = Item.objects.found().open().exclude(user = user)  #chain methods
    open_lost = Item.objects.lost().open().exclude(user=user)
    
    claims_made = Claim.objects.filter(claimer = user)
    claims_received = Claim.objects.filter(item__user=user, status='PENDING')
    
    matched_results = []

    user_lost_items = my_items.filter(item_type='LOST')  # adjust field if different

    for lost_item in user_lost_items:
        #Skip invalid embeddings
        if not lost_item.text_embedding: # Description is mandatory
            continue
        
        #Smart filtering
        category_matched = open_found.filter(category=lost_item.category)
        
        #Fallback if no same category items
        candidates = category_matched if category_matched.exists() else open_found
        
        matches = match_items(lost_item, candidates)
        top_matches = matches[:5]  # top 5 only
        
        if top_matches:
            matched_results.append({
                "item": lost_item,
                "matches": top_matches
            })
    
    notifications = request.user.notifications.order_by('-created_at')[:10]
    # request.user.notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'my_items': my_items,
        'open_found': open_found,
        'open_lost': open_lost,
        'claims_made': claims_made,
        'claims_received': claims_received,
        'notifications': notifications, 
        'matched_results': matched_results,
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
            send_mail(
                "New claim received",
                f"{request.user.username} has submitted a claim on your item '{item.title}'.",
                None,
                [item.user.email],
                fail_silently=True,
            )
            Notification.objects.create(
                user=item.user,
                message=f"{request.user.username} submitted a claim on your item '{item.title}'."
            )
            return redirect('home')
    else:
        form = ClaimForm()

    return render(request, 'submit_claim.html', {'form': form, 'item': item})

@login_required
def approve_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    try:
        claim.approve(acting_user=request.user)
        
        subject = "Your claim has been approved!"
        
        try:
            phone = Profile.objects.get(user=claim.item.user).phone_number
        except Profile.DoesNotExist:
                phone = 'N/A'
        
        message = (
            f"Hi {claim.claimer.username},\n\n"
            f"Great news! Your claim for '{claim.item.title}' has been approved.\n\n"
            f"Item Details:\n"
            f"- Title: {claim.item.title}\n"
            f"- Location: {claim.item.location}\n\n"
            
            f"Owner Contact:\n"
            f"- Username: {claim.item.user.username}\n"
            f"- Email: {claim.item.user.email}\n"
            f"- Phone: {phone}\n\n"

            f"Your Message:\n{claim.message}\n\n"

            f"Please contact the owner to arrange return.\n\n"
            f"— Lost & Found System"
        )

        send_mail(
            subject,
            message,
            None,
            [claim.claimer.email],
            fail_silently=True,
        )
        
        Notification.objects.create(
            user=claim.claimer,
            message=f"Your claim for '{claim.item.title}' has been approved."
        )
        
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
        
        subject = "Your claim has been rejected"
        message = (
            f"Hi {claim.claimer.username},\n\n"
            f"Your claim for '{claim.item.title}' was rejected.\n\n"
            f"You may try providing more details.\n\n"
            f"Thanks."
        )

        send_mail(
            subject,
            message,
            None,
            [claim.claimer.email],
            fail_silently=True,
        )
        
        Notification.objects.create(
            user=claim.claimer,
            message=f"Your claim for '{claim.item.title}' was rejected."
        )
        
        messages.success(request, f"Claim on '{claim.item.title}' rejected!")
    except PermissionDenied as e:
        messages.error(request, str(e))
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('home')

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.user != request.user:
        return redirect('home')

    notification.is_read = True
    notification.save()

    return redirect('home')


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if item.user != request.user:
        return redirect('home')

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('home')

    return render(request, 'confirm_delete.html', {'item': item})