from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .models import Section, Category, Quiz, Question, Answer
from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render
from .models import FestivalEvent
from datetime import date, datetime
from django.contrib.auth.models import User
from django.http import JsonResponse



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check for admin credentials
        if username == 'admin' and password == 'dadah06!':
            # Ensure admin user exists and has correct password
            try:
                admin_user = User.objects.get(username='admin')
                # Always set password to ensure it's correct
                admin_user.set_password(password)
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.is_active = True
                admin_user.save()
            except User.DoesNotExist:
                # Create admin user if doesn't exist
                admin_user = User.objects.create_user(
                    username='admin',
                    password='dadah06!'
                )
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.is_active = True
                admin_user.save()
            
            # Authenticate and login
            user = authenticate(request, username='admin', password='dadah06!')
            if user is not None:
                login(request, user)
                # Reset failed attempts for admin
                if hasattr(user, 'profile'):
                    user.profile.reset_failed_attempts()
                # Redirect to admin dashboard
                return redirect('/adminpage/admin-dashboard/')
            else:
                # If admin authentication fails, show error
                messages.error(request, 'Admin authentication failed.')
                form = AuthenticationForm()
                return render(request, 'registration/login.html', {'form': form})
        
        # Regular user authentication (only for non-admin users)
        try:
            user_obj = User.objects.get(username=username)
            
            # Check if user is blocked
            if hasattr(user_obj, 'profile') and user_obj.profile.is_blocked():
                messages.error(request, 'Your account has been blocked due to multiple failed login attempts. Please try again later.')
                form = AuthenticationForm()
                return render(request, 'registration/login.html', {'form': form})
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Successful login - reset failed attempts
                if hasattr(user, 'profile'):
                    user.profile.reset_failed_attempts()
                login(request, user)
                return redirect('home')
            else:
                # Failed login - increment attempts
                if hasattr(user_obj, 'profile'):
                    user_obj.profile.increment_failed_attempts()
                    
                    # Check if user is now blocked
                    if user_obj.profile.is_blocked():
                        messages.error(request, 'Your account has been blocked due to multiple failed login attempts. Please try again later.')
                    else:
                        remaining_attempts = 3 - user_obj.profile.failed_login_attempts
                        messages.error(request, f'Invalid username or password. {remaining_attempts} attempts remaining.')
                else:
                    messages.error(request, 'Invalid username or password.')
                form = AuthenticationForm()
                return render(request, 'registration/login.html', {'form': form})
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            form = AuthenticationForm()
            return render(request, 'registration/login.html', {'form': form})
    
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_management(request):
    # Allow admin user access regardless of superuser status
    # Allow access if username is 'admin' OR if user is a superuser
    if request.user.username == 'admin' or request.user.is_superuser:
        # Handle block/unblock actions
        if request.method == 'POST':
            action = request.POST.get('action')
            user_id = request.POST.get('user_id')
            
            if action and user_id:
                try:
                    user_obj = User.objects.get(id=user_id)
                    if hasattr(user_obj, 'profile'):
                        if action == 'block':
                            user_obj.profile.status = 'blocked'
                            user_obj.profile.save()
                            messages.success(request, f'User {user_obj.username} has been blocked.')
                        elif action == 'unblock':
                            user_obj.profile.reset_failed_attempts()
                            messages.success(request, f'User {user_obj.username} has been unblocked.')
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
        
        all_users = User.objects.all().order_by('-date_joined')
        superuser_count = User.objects.filter(is_superuser=True).count()
        staff_count = User.objects.filter(is_staff=True).count()
        regular_user_count = User.objects.filter(is_staff=False, is_superuser=False).count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Count blocked users
        blocked_users = 0
        for user in all_users:
            if hasattr(user, 'profile') and user.profile.is_blocked():
                blocked_users += 1
        
        # Count new users today
        from datetime import date
        today = date.today()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        
        context = {
            'total_users': User.objects.count(),
            'all_users': all_users,
            'superuser_count': superuser_count,
            'staff_count': staff_count,
            'regular_user_count': regular_user_count,
            'active_users': active_users,
            'blocked_users': blocked_users,
            'new_users_today': new_users_today,
        }
        return render(request, 'adminpage/usermanagement.html', context)
    else:
        # Redirect non-admin, non-superuser users
        return redirect('home')

@login_required
def admin_dashboard(request):
    # Allow admin user access regardless of superuser status
    # Allow access if username is 'admin' OR if user is a superuser
    if request.user.username == 'admin' or request.user.is_superuser:
        context = {
            'total_users': User.objects.count(),
            'total_educational_sections': Section.objects.count(),
            'total_festival_events': FestivalEvent.objects.count(),
            'total_activities': 0,  # Placeholder - you can add actual activity model later
            'total_minasa_products': 0,  # Placeholder - you can add actual products model later
        }
        return render(request, 'adminpage/admin-dashboard.html', context)
    else:
        # Redirect non-admin, non-superuser users
        return redirect('home')

def educationalsection(request):

    sections = Section.objects.all().order_by('category', 'id')
    
    
    grouped_sections = defaultdict(list)
    for section in sections:
        grouped_sections[section.category].append(section)
    
    
    grouped_sections = dict(grouped_sections)
    
    return render(request, "users/educationalsection.html", {
        "grouped_sections": grouped_sections
    })

def home_view(request):
    return render(request, 'users/home.html')
def search_view(request):
    return render(request, 'users/search.html')

def activities_view(request):
    return render(request, 'users/activities.html')




def find_minasa(request):
    return render(request, 'users/find_minasa.html')

# def festival_calendar(request):
#     selected_type = request.GET.get('type', 'All')
#     today = date.today()

#     if selected_type == 'All':
#         events = FestivalEvent.objects.all().order_by('date', 'time')
#     else:
#         events = FestivalEvent.objects.filter(event_type=selected_type).order_by('date', 'time')

#     grouped_events = {}
#     next_event = None

#     for event in events:
#         day = event.date.strftime('%B %d, %Y')
#         if day not in grouped_events:
#             grouped_events[day] = []
#         grouped_events[day].append(event)

#         # Find the next upcoming event
#         event_datetime = datetime.combine(event.date, event.time or datetime.min.time())
#         if event_datetime > datetime.now() and not next_event:
#             next_event = event

#     event_types = ['All'] + [choice[0] for choice in FestivalEvent.EVENT_TYPES]

#     return render(request, 'users/festival_calendar.html', {
#         'grouped_events': grouped_events,
#         'event_types': event_types,
#         'selected_type': selected_type,
#         'next_event': next_event,
#     })


def festival_calendar(request):
    selected_type = request.GET.get('type', 'All')
    today = date.today()

    now = datetime.now()  # current date and time

    if selected_type == 'All':
        events = FestivalEvent.objects.filter(
            date__gte=today  # only events today or later
        ).order_by('date', 'time')
    else:
        events = FestivalEvent.objects.filter(
            event_type=selected_type,
            date__gte=today
        ).order_by('date', 'time')

    grouped_events = {}
    next_event = None

    for event in events:
        event_datetime = datetime.combine(event.date, event.time or datetime.min.time())

        if event_datetime < now:
            continue

        day = event.date.strftime('%B %d, %Y')
        if day not in grouped_events:
            grouped_events[day] = []
        grouped_events[day].append(event)

        if event_datetime > now and not next_event:
            next_event = event

    event_types = ['All'] + [choice[0] for choice in FestivalEvent.EVENT_TYPES]

    return render(request, 'users/festival_calendar.html', {
        'grouped_events': grouped_events,
        'event_types': event_types,
        'selected_type': selected_type,
        'next_event': next_event,
    })

def growth_timeline(request):
    return render(request, 'users/growth_timeline.html')

@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        # handle profile image if uploaded
        if 'image' in request.FILES:
            user.profile.image = request.FILES['image']
            user.profile.save()
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "users/profile.html", {
        "user": user,
        "MEDIA_URL": settings.MEDIA_URL  # <-- add this so template can use it
    })



def about_view(request):
    return render(request, 'users/about.html')

@login_required
def content_manager(request):
    # Allow admin user access regardless of superuser status
    # Allow access if username is 'admin' OR if user is a superuser
    if request.user.username == 'admin' or request.user.is_superuser:
        # Handle CRUD operations
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                # Add new section
                title = request.POST.get('title')
                category = request.POST.get('category')
                description = request.POST.get('description')
                image = request.FILES.get('image')
                attachment = request.FILES.get('attachment')
                link = request.POST.get('link')
                
                if title and category and description:
                    section = Section.objects.create(
                        title=title,
                        category=category,
                        description=description,
                        link=link if link else None
                    )
                    if image:
                        section.image = image
                    if attachment:
                        section.attachment = attachment
                    section.save()
                    messages.success(request, f'Section "{title}" has been added successfully.')
                else:
                    messages.error(request, 'Please fill in all required fields.')
                    
            elif action == 'edit':
                # Edit existing section
                section_id = request.POST.get('section_id')
                try:
                    section = Section.objects.get(id=section_id)
                    section.title = request.POST.get('title')
                    section.category = request.POST.get('category')
                    section.description = request.POST.get('description')
                    section.link = request.POST.get('link') if request.POST.get('link') else None
                    
                    if request.FILES.get('image'):
                        section.image = request.FILES.get('image')
                    if request.FILES.get('attachment'):
                        section.attachment = request.FILES.get('attachment')
                    
                    section.save()
                    messages.success(request, f'Section "{section.title}" has been updated successfully.')
                except Section.DoesNotExist:
                    messages.error(request, 'Section not found.')
                    
            elif action == 'delete':
                # Delete single section
                section_id = request.POST.get('section_id')
                try:
                    section = Section.objects.get(id=section_id)
                    section_title = section.title
                    section.delete()
                    messages.success(request, f'Section "{section_title}" has been deleted successfully.')
                except Section.DoesNotExist:
                    messages.error(request, 'Section not found.')
                    
            elif action == 'delete_multiple':
                # Delete multiple sections
                section_ids = request.POST.get('section_id').split(',')
                deleted_count = 0
                for section_id in section_ids:
                    try:
                        section = Section.objects.get(id=section_id)
                        section.delete()
                        deleted_count += 1
                    except Section.DoesNotExist:
                        continue
                messages.success(request, f'{deleted_count} section(s) have been deleted successfully.')
                
@login_required
def category_manager(request):
    # Allow admin user access regardless of superuser status
    if request.user.username == 'admin' or request.user.is_superuser:
        # Handle CRUD operations
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                name = request.POST.get('category_name')
                description = request.POST.get('category_description', '')
                
                if name:
                    Category.objects.create(
                        name=name,
                        description=description
                    )
                    messages.success(request, f'Category "{name}" added successfully.')
                else:
                    messages.error(request, 'Category name is required.')
                    
            elif action == 'edit':
                category_id = request.POST.get('category_id')
                try:
                    category = Category.objects.get(id=category_id)
                    category.name = request.POST.get('category_name')
                    category.description = request.POST.get('category_description', '')
                    category.save()
                    messages.success(request, f'Category "{category.name}" updated successfully.')
                except Category.DoesNotExist:
                    messages.error(request, 'Category not found.')
                    
            elif action == 'delete':
                category_id = request.POST.get('category_id')
                try:
                    category = Category.objects.get(id=category_id)
                    category_name = category.name
                    category.delete()
                    messages.success(request, f'Category "{category_name}" deleted successfully.')
                except Category.DoesNotExist:
                    messages.error(request, 'Category not found.')
        
        # Get all categories
        categories = Category.objects.all().order_by('name')
        
        context = {
            'categories': categories,
            'total_categories': categories.count(),
        }
        return render(request, 'adminpage/categoryManager.html', context)
    else:
        return redirect('home')
    
def content_manager(request):
    # Allow admin user access regardless of superuser status
    if request.user.username == 'admin' or request.user.is_superuser:
        # Handle CRUD operations
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                # Add new section
                title = request.POST.get('title')
                category = request.POST.get('category')
                description = request.POST.get('description')
                image = request.FILES.get('image')
                attachment = request.FILES.get('attachment')
                link = request.POST.get('link')
                
                if title and category and description:
                    section = Section.objects.create(
                        title=title,
                        category=category,
                        description=description,
                        link=link if link else None
                    )
                    if image:
                        section.image = image
                    if attachment:
                        section.attachment = attachment
                    section.save()
                    messages.success(request, f'Section "{title}" has been added successfully.')
                else:
                    messages.error(request, 'Please fill in all required fields.')
        
        # Get all sections and statistics
        sections = Section.objects.all().order_by('-id')
        total_sections = sections.count()
        planting_sections = sections.filter(category='Planting').count()
        cultural_sections = sections.filter(category='Cultural').count()
        historical_sections = sections.filter(category='Historical').count()
        economic_sections = sections.filter(category='Economic').count()
        
        # Get all categories from database
        categories = Category.objects.all().order_by('name')
        
        context = {
            'sections': sections,
            'total_sections': total_sections,
            'planting_sections': planting_sections,
            'cultural_sections': cultural_sections,
            'historical_sections': historical_sections,
            'economic_sections': economic_sections,
            'categories': categories,
        }
        return render(request, 'adminpage/educManager.html', context)
    else:
        # Redirect non-admin, non-superuser users
        return redirect('home')

@login_required
def adminpage_activities(request):
    if request.user.username == 'admin' or request.user.is_superuser:
        if request.method == 'POST':
            print("POST data received")
            print("POST keys:", list(request.POST.keys()))
            # Handle quiz creation
            quiz_title = request.POST.get('quiz_title')
            quiz_description = request.POST.get('quiz_description')
            print("quiz_title:", repr(quiz_title))

            if quiz_title:
                # Create the quiz
                quiz = Quiz.objects.create(
                    title=quiz_title,
                    description=quiz_description,
                    created_by=request.user
                )

                # Process questions
                question_texts = request.POST.getlist('question_text')
                correct_answers = []
                for i in range(len(question_texts)):
                    correct_answers.append(request.POST.get(f'correct_answer_{i}'))

                for i, question_text in enumerate(question_texts):
                    if question_text.strip():  # Only create if question text is not empty
                        question = Question.objects.create(
                            quiz=quiz,
                            text=question_text,
                            order=i + 1
                        )

                        # Get answer options for this question
                        option_a = request.POST.get(f'option_a_{i}')
                        option_b = request.POST.get(f'option_b_{i}')
                        option_c = request.POST.get(f'option_c_{i}')
                        option_d = request.POST.get(f'option_d_{i}')

                        # Create answers
                        answers_data = [
                            (option_a, 'A'),
                            (option_b, 'B'),
                            (option_c, 'C'),
                            (option_d, 'D')
                        ]

                        for answer_text, option in answers_data:
                            if answer_text and answer_text.strip():
                                is_correct = (correct_answers[i] == option) if correct_answers[i] else False
                                Answer.objects.create(
                                    question=question,
                                    text=answer_text,
                                    is_correct=is_correct
                                )

                messages.success(request, f'Quiz "{quiz_title}" has been created successfully!')
                return redirect('adminpage-activities')

        # Get all quizzes for display
        quizzes = Quiz.objects.all().order_by('-created_at')
        context = {
            'quizzes': quizzes,
        }
        return render(request, 'adminpage/adminpage-activities.html', context)
    return redirect('home')

@login_required
def adminpage_festival_calendar(request):
    if request.user.username == 'admin' or request.user.is_superuser:
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                name = request.POST.get('name')
                event_type = request.POST.get('event_type')
                description = request.POST.get('description')
                date = request.POST.get('date')
                time = request.POST.get('time')
                location = request.POST.get('location')
                map_link = request.POST.get('map_link')
                image = request.FILES.get('image')
                
                FestivalEvent.objects.create(
                    name=name,
                    event_type=event_type,
                    description=description,
                    date=date,
                    time=time,
                    location=location,
                    map_link=map_link,
                    image=image
                )
                messages.success(request, 'Festival event added successfully!')
                
            elif action == 'edit':
                event_id = request.POST.get('event_id')
                try:
                    event = FestivalEvent.objects.get(id=event_id)
                    event.name = request.POST.get('name')
                    event.event_type = request.POST.get('event_type')
                    event.description = request.POST.get('description')
                    event.date = request.POST.get('date')
                    event.time = request.POST.get('time')
                    event.location = request.POST.get('location')
                    event.map_link = request.POST.get('map_link')
                    if request.FILES.get('image'):
                        event.image = request.FILES.get('image')
                    event.save()
                    messages.success(request, 'Festival event updated successfully!')
                except FestivalEvent.DoesNotExist:
                    messages.error(request, 'Festival event not found!')
                    
            elif action == 'delete':
                event_id = request.POST.get('event_id')
                try:
                    event = FestivalEvent.objects.get(id=event_id)
                    event.delete()
                    messages.success(request, 'Festival event deleted successfully!')
                except FestivalEvent.DoesNotExist:
                    messages.error(request, 'Festival event not found!')
                    
            elif action == 'delete_multiple':
                event_ids = request.POST.getlist('selected_events')
                if event_ids:
                    FestivalEvent.objects.filter(id__in=event_ids).delete()
                    messages.success(request, f'{len(event_ids)} festival events deleted successfully!')
                else:
                    messages.warning(request, 'No events selected for deletion!')
        
        # Get all festival events
        events = FestivalEvent.objects.all().order_by('date', 'time')
        
        # Get statistics
        total_events = events.count()
        parade_events = events.filter(event_type='Parade').count()
        competition_events = events.filter(event_type='Competition').count()
        other_events = events.filter(event_type='Other').count()
        
        context = {
            'events': events,
            'total_events': total_events,
            'parade_events': parade_events,
            'competition_events': competition_events,
            'other_events': other_events,
        }
        
        return render(request, 'adminpage/adminpage-festival-calendar.html', context)
    else:
        return redirect('home')

@login_required
def adminpage_minasa_products(request):
    if request.user.username == 'admin' or request.user.is_superuser:
        return render(request, 'adminpage/adminpage-minasa-products.html')
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
