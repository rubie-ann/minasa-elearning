from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .models import Section, Category, Quiz, Question, Answer, MinasaProduct, MinigameLevel, QuizAttempt, MinigameAttempt
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
from .models import GrowthStage
from django.contrib.auth import logout
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from .models import Section
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.http import require_http_methods




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
def user_performance(request):
    """Admin page to show user performance metrics with quiz and minigame data."""
    if request.user.username == 'admin' or request.user.is_superuser:
        all_users = User.objects.all().order_by('-date_joined')
        
        # Build user performance data
        user_performance_data = []
        for user in all_users:
            # Get quiz attempts
            quiz_attempts = QuizAttempt.objects.filter(user=user)
            quizzes_completed = quiz_attempts.values('quiz').distinct().count()
            quiz_count = Quiz.objects.count()
            
            # Get minigame attempts
            minigame_attempts = MinigameAttempt.objects.filter(user=user, completed=True)
            minigames_completed = minigame_attempts.count()
            minigame_count = MinigameLevel.objects.count()
            
            user_performance_data.append({
                'user': user,
                'quizzes_completed': quizzes_completed,
                'quiz_count': quiz_count,
                'minigames_completed': minigames_completed,
                'minigame_count': minigame_count,
            })
        
        context = {
            'all_users': all_users,
            'user_performance_data': user_performance_data,
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'blocked_users': sum(1 for u in all_users if hasattr(u, 'profile') and u.profile.is_blocked()),
        }
        return render(request, 'adminpage/userperformance.html', context)
    else:
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
            'total_minasa_products': MinasaProduct.objects.count(),
            'total_quizzes': Quiz.objects.count(),
            'total_minigame_levels': MinigameLevel.objects.count(),
        }
        return render(request, 'adminpage/admin-dashboard.html', context)
    else:
        # Redirect non-admin, non-superuser users
        return redirect('home')


@login_required
def admin_profile(request):
    # Simple admin profile page; allow admin or superuser only
    if request.user.username == 'admin' or request.user.is_superuser:
        context = {
            'user': request.user,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, 'adminpage/admin-profile.html', context)
    else:
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
    quizzes = list(Quiz.objects.all().order_by('created_at'))
    minigame_levels = list(MinigameLevel.objects.all().order_by('created_at'))

    user = request.user if request.user.is_authenticated else None

    # Build quizzes_data: {'quiz': Quiz, 'index': n, 'unlocked': bool, 'last_score': int|None, 'completed': bool}
    quizzes_data = []
    prev_completed = True  # first quiz unlocked by default
    for idx, quiz in enumerate(quizzes, start=1):
        last_score = None
        completed = False
        if user:
            last_attempt = QuizAttempt.objects.filter(user=user, quiz=quiz).order_by('-completed_at').first()
            if last_attempt:
                last_score = last_attempt.score
                # Consider any attempt as completion for progression; change logic if pass threshold required
                completed = True

        unlocked = prev_completed
        quizzes_data.append({
            'quiz': quiz,
            'index': idx,
            'unlocked': unlocked,
            'last_score': last_score,
            'completed': completed,
        })
        prev_completed = completed

    # Build minigame_data: similar progression
    minigame_data = []
    prev_completed = True
    for idx, level in enumerate(minigame_levels, start=1):
        completed = False
        if user:
            att = MinigameAttempt.objects.filter(user=user, level=level, completed=True).first()
            if att:
                completed = True

        unlocked = prev_completed
        minigame_data.append({
            'level': level,
            'index': idx,
            'unlocked': unlocked,
            'completed': completed,
        })
        prev_completed = completed

    context = {
        'quizzes': quizzes,
        'minigame_levels': minigame_levels,
        'quizzes_data': quizzes_data,
        'minigame_data': minigame_data,
    }
    return render(request, 'users/activities.html', context)




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

@login_required
def content_manager(request):
    # Allow admin user access regardless of superuser status
    if request.user.username == 'admin' or request.user.is_superuser:
        # Handle CRUD operations
        if request.method == 'POST':
            action = request.POST.get('action')
            section_id = request.POST.get('section_id')
            
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
            
            # EDIT SECTION
            elif action == 'edit' and section_id:
                section = get_object_or_404(Section, id=section_id)
                section.title = request.POST.get('title')
                section.category = request.POST.get('category')
                section.description = request.POST.get('description')
                section.link = request.POST.get('link')

                if request.FILES.get('image'):
                    section.image = request.FILES['image']
                if request.FILES.get('attachment'):
                    section.attachment = request.FILES['attachment']

                section.save()
                messages.success(request, f'Section "{section.title}" updated successfully.')
                return redirect('adminpage-content-manager')

            # DELETE SINGLE
            elif action == 'delete' and section_id:
                section = get_object_or_404(Section, id=section_id)
                section.delete()
                messages.success(request, 'Section deleted successfully.')
                return redirect('adminpage-content-manager')

            # DELETE MULTIPLE
            elif action == 'delete_multiple':
                ids = request.POST.get('section_id', '')
                id_list = [int(i) for i in ids.split(',') if i.isdigit()]
                Section.objects.filter(id__in=id_list).delete()
                messages.success(request, 'Selected sections deleted successfully.')
                return redirect('adminpage-content-manager')
        
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
        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'add':
                product_name = request.POST.get('product_name')
                description = request.POST.get('description')
                price = request.POST.get('price')  # ADD THIS LINE
                image = request.FILES.get('image')

                if product_name and description and price:  # UPDATE THIS LINE
                    product = MinasaProduct.objects.create(
                        product_name=product_name,
                        description=description,
                        price=price  # ADD THIS LINE
                    )
                    if image:
                        product.image = image
                        product.save()
                    messages.success(request, f'Product "{product_name}" has been added successfully.')
                else:
                    messages.error(request, 'Please fill in all required fields.')

            elif action == 'edit':
                product_id = request.POST.get('product_id')
                try:
                    product = MinasaProduct.objects.get(id=product_id)
                    product.product_name = request.POST.get('product_name')
                    product.description = request.POST.get('description')
                    product.price = request.POST.get('price')  # ADD THIS LINE

                    if request.FILES.get('image'):
                        product.image = request.FILES.get('image')

                    product.save()
                    messages.success(request, f'Product "{product.product_name}" has been updated successfully.')
                except MinasaProduct.DoesNotExist:
                    messages.error(request, 'Product not found.')

            elif action == 'delete':
                product_id = request.POST.get('product_id')
                try:
                    product = MinasaProduct.objects.get(id=product_id)
                    product_name = product.product_name
                    product.delete()
                    messages.success(request, f'Product "{product_name}" has been deleted successfully.')
                except MinasaProduct.DoesNotExist:
                    messages.error(request, 'Product not found.')

            elif action == 'delete_multiple':
                product_ids = request.POST.getlist('selected_products')
                if product_ids:
                    MinasaProduct.objects.filter(id__in=product_ids).delete()
                    messages.success(request, f'{len(product_ids)} product(s) deleted successfully!')
                else:
                    messages.warning(request, 'No products selected for deletion!')

        # Get all products
        products = MinasaProduct.objects.all().order_by('-id')

        context = {
            'products': products,
            'total_products': products.count(),
        }

        return render(request, 'adminpage/adminpage-minasa-products.html', context)
    return redirect('home')
@login_required
def quiz_view(request, quiz_id):
    if request.user.username == 'admin' or request.user.is_superuser:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all().order_by('order')
        context = {
            'quiz': quiz,
            'questions': questions,
        }
        return render(request, 'adminpage/quiz_view.html', context)
    return redirect('home')

@login_required
def quiz_edit(request, quiz_id):
    if request.user.username == 'admin' or request.user.is_superuser:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if request.method == 'POST':
            # Handle quiz update
            quiz.title = request.POST.get('quiz_title')
            quiz.description = request.POST.get('quiz_description')
            quiz.save()

            # Delete existing questions and answers
            quiz.questions.all().delete()

            # Process updated questions
            question_texts = request.POST.getlist('question_text')
            correct_answers = []
            for i in range(len(question_texts)):
                correct_answers.append(request.POST.get(f'correct_answer_{i}'))

            for i, question_text in enumerate(question_texts):
                if question_text.strip():
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

            messages.success(request, f'Quiz "{quiz.title}" has been updated successfully!')
            return redirect('adminpage-activities')

        # Prepare data for editing
        questions = quiz.questions.all().order_by('order')
        questions_data = []
        for question in questions:
            answers = question.answers.all()
            answer_dict = {}
            correct_answer = None
            for answer in answers:
                if answer.is_correct:
                    correct_answer = 'A' if answer.text == answers[0].text else 'B' if answer.text == answers[1].text else 'C' if answer.text == answers[2].text else 'D'
                if len(answers) > 0 and answer == answers[0]:
                    answer_dict['A'] = answer.text
                elif len(answers) > 1 and answer == answers[1]:
                    answer_dict['B'] = answer.text
                elif len(answers) > 2 and answer == answers[2]:
                    answer_dict['C'] = answer.text
                elif len(answers) > 3 and answer == answers[3]:
                    answer_dict['D'] = answer.text
            questions_data.append({
                'text': question.text,
                'answers': answer_dict,
                'correct': correct_answer
            })

        context = {
            'quiz': quiz,
            'questions_data': questions_data,
        }
        return render(request, 'adminpage/quiz_edit.html', context)
    return redirect('home')

@login_required
def quiz_delete(request, quiz_id):
    if request.user.username == 'admin' or request.user.is_superuser:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if request.method == 'POST':
            quiz_title = quiz.title
            quiz.delete()
            messages.success(request, f'Quiz "{quiz_title}" has been deleted successfully!')
            return redirect('adminpage-activities')
        context = {
            'quiz': quiz,
        }
        return render(request, 'adminpage/quiz_delete.html', context)
    return redirect('home')

def quiz_api(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().order_by('order')

    quiz_data = {
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'questions': []
    }

    for question in questions:
        answers = question.answers.all().order_by('id')
        question_data = {
            'id': question.id,
            'text': question.text,
            'answers': [],
            'correct_answer': None
        }

        for answer in answers:
            question_data['answers'].append({
                'text': answer.text,
                'is_correct': answer.is_correct
            })
            if answer.is_correct:
                # Find which option this is (A, B, C, D)
                answer_index = list(answers).index(answer)
                question_data['correct_answer'] = chr(65 + answer_index)  # A=0, B=1, etc.

        quiz_data['questions'].append(question_data)

    return JsonResponse(quiz_data)


@login_required
@require_http_methods(["POST"])
def save_quiz_attempt(request, quiz_id):
    """Save user's quiz attempt"""
    import json
    
    try:
        data = json.loads(request.body)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Calculate score
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        
        # Save the attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Quiz attempt saved successfully',
            'attempt_id': attempt.id
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def save_minigame_attempt(request, level_id):
    """Save user's minigame level attempt"""
    import json
    
    try:
        data = json.loads(request.body)
        level = get_object_or_404(MinigameLevel, id=level_id)
        
        completed = data.get('completed', False)
        
        # Get or create the attempt
        attempt, created = MinigameAttempt.objects.get_or_create(
            user=request.user,
            level=level
        )
        
        # Update the attempt
        if completed:
            attempt.completed = True
            attempt.completed_at = timezone.now()
        
        attempt.attempts_count = data.get('attempts_count', attempt.attempts_count + 1)
        attempt.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Minigame attempt saved successfully',
            'attempt_id': attempt.id
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def signup(request):
    if request.method == 'POST':
        from .forms import CustomUserCreationForm
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Return success context instead of redirecting
            new_form = CustomUserCreationForm()
            return render(request, 'registration/signup.html', {
                'form': new_form,
                'success': True,
                'success_message': f'Account created successfully! Your account is now ready. Please log in with your credentials.'
            })
        else:
            # Show form with errors
            return render(request, 'registration/signup.html', {'form': form, 'success': False})
    else:
        from .forms import CustomUserCreationForm
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form, 'success': False})

def find_minasa(request):
    # Retrieve all Minasa products from the database
    products = MinasaProduct.objects.all().order_by('-id')
    
    context = {
        'products': products,
    }
    
    return render(request, 'users/find_minasa.html', context)

@login_required
def admin_minigame(request):
    if request.user.username == 'admin' or request.user.is_superuser:
        from .models import MinigameLevel
        from .forms import MinigameLevelForm
        levels = MinigameLevel.objects.all().order_by('id')
        form = MinigameLevelForm()
        context = {
            'levels': levels,
            'total_levels': levels.count(),
            'form': form,
        }
        return render(request, 'adminpage/admin-minigame.html', context)
    else:
        return redirect('home')

@login_required
def add_minigame_level(request):
    if request.user.username == 'admin' or request.user.is_superuser:
        from .forms import MinigameLevelForm
        from django.http import JsonResponse

        if request.method == 'POST':
            form = MinigameLevelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, 'Minigame level added successfully!')
                return redirect('adminpage-minigame')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Form validation failed'})
        else:
            form = MinigameLevelForm()

        return render(request, 'minigame_add_level.html', {'form': form})
    else:
        return redirect('home')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def edit_minigame_level(request, level_id):
    if request.user.username == 'admin' or request.user.is_superuser:
        from .models import MinigameLevel
        from .forms import MinigameLevelForm
        level = get_object_or_404(MinigameLevel, id=level_id)

        if request.method == 'POST':
            form = MinigameLevelForm(request.POST, request.FILES, instance=level)
            if form.is_valid():
                form.save()
                messages.success(request, 'Minigame level updated successfully!')
                return redirect('adminpage-minigame')
        else:
            form = MinigameLevelForm(instance=level)

        context = {
            'form': form,
            'level': level,
            'is_edit': True,
        }
        return render(request, 'minigame_add_level.html', context)
    else:
        return redirect('home')

@login_required
def delete_minigame_level(request, level_id):
    if request.user.username == 'admin' or request.user.is_superuser:
        from .models import MinigameLevel
        from django.http import JsonResponse

        if request.method == 'POST':
            try:
                level = MinigameLevel.objects.get(id=level_id)
                level.delete()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, 'Minigame level deleted successfully!')
                return redirect('adminpage-minigame')
            except MinigameLevel.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Level not found'})
                messages.error(request, 'Level not found.')
                return redirect('adminpage-minigame')
        else:
            return redirect('adminpage-minigame')
    else:
        return redirect('home')

@login_required
def get_minigame_level_data(request, level_id):
    from .models import MinigameLevel
    from django.http import JsonResponse

    try:
        level = MinigameLevel.objects.get(id=level_id)
        # Increment attempts when level is accessed
        level.increment_attempts()
        data = {
            'id': level.id,
            'answer': level.answer,
            'image1_url': level.image1.url if level.image1 else '',
            'image2_url': level.image2.url if level.image2 else '',
            'image3_url': level.image3.url if level.image3 else '',
            'image4_url': level.image4.url if level.image4 else '',
        }
        return JsonResponse(data)
    except MinigameLevel.DoesNotExist:
        return JsonResponse({'error': 'Level not found'}, status=404)

def growth_timeline(request):
    events = list(GrowthStage.objects.all().order_by('date', 'order'))
    # For slider bounds
    if events:
        min_date = events[0].date
        max_date = events[-1].date
    else:
        min_date = max_date = date.today()

    context = {
        'timeline_events': events,
        'min_date': min_date.isoformat(),
        'max_date': max_date.isoformat()
    }
    return render(request, 'users/growth_timeline.html', context)

def generate_content_report(request):
    search = request.POST.get('search', '').lower()
    category = request.POST.get('category', 'all').lower()

    sections = Section.objects.all()

    if search:
        sections = sections.filter(title__icontains=search)
    if category != 'all':
        sections = sections.filter(category__iexact=category)

    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="educational_sections_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Educational Sections Report")
    p.setAuthor("Minasa E-Learning System")
    p.setSubject("Generated Educational Content Report")
    width, height = letter
    y = height - 80

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "Educational Sections Report")
    y -= 40

    # Body
    for section in sections:
        if y < 120:
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 12)

        # Title (bold)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, section.title)
        y -= 15

        # Category
        p.setFont("Helvetica", 11)
        p.drawString(50, y, f"Category: {section.category}")
        y -= 15

        # Description (wrapped text)
        p.setFont("Helvetica", 10)
        text = section.description if section.description else "No description available."
        wrapped_text = simpleSplit(text, "Helvetica", 10, width - 100)  # wrap width
        for line in wrapped_text:
            if y < 100:
                p.showPage()
                y = height - 60
                p.setFont("Helvetica", 10)
            p.drawString(50, y, line)
            y -= 12

        y -= 15  # space before next section

    p.showPage()
    p.save()
    return response

def generate_user_report(request):
    from io import BytesIO
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from django.contrib.auth.models import User
    from datetime import datetime

    # Fetch users
    users = User.objects.all()

    # PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title="User Management Report",
        author="Minasa E-Learning System"
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>User Management Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 10))

    # Table headers
    data = [["Username", "Email address", "First Name", "Last Name", "Staff", "Superuser", "Date Joined"]]

    # Table rows
    for user in users:
        staff_status = "Yes" if user.is_staff else "No"
        superuser_status = "Yes" if user.is_superuser else "No"
        date_joined = user.date_joined.strftime("%b %d, %Y")

        data.append([
            user.username,
            user.email or "No email",
            user.first_name or "-",
            user.last_name or "-",
            staff_status,
            superuser_status,
            date_joined
        ])

    # Create the table
    table = Table(data, repeatRows=1, colWidths=[80, 150, 80, 80, 60, 60, 80])

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f97316")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))

    elements.append(table)
    doc.build(elements)

    # Date generated
    gen_date = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    elements.append(Paragraph(f"Generated on: {gen_date}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Return PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_report.pdf"'
    return response

