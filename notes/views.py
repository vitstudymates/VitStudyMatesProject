from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate,logout,login
from datetime import date
from .models import SignUp
# Create your views here.




from django.utils import timezone
def notes_dashboard(request):
    # You can fetch notes from the database here and pass them to the template
    return render(request, 'notes_dashboard.html')




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Notes
from .forms import NotesForm

@login_required
def upload_notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            
            # Award points to the user for uploading notes
            try:
                profile = request.user.profile
                profile.points += 10  # Award 10 points for uploading notes
                profile.save()
                messages.success(request, 'Your notes have been successfully uploaded! You earned 10 points.')
            except:
                messages.success(request, 'Your notes have been successfully uploaded!')
                
            return redirect('upload_notes')
    else:
        form = NotesForm()
    
    # Get user's recent notes
    user_notes = Notes.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    
    context = {
        'form': form,
        'user_notes': user_notes,
    }
    
    return render(request, 'upload_notes.html', context)




from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Notes

def browse_notes(request):
    # Get all approved notes
    notes_list = Notes.objects.filter(status='approved')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        notes_list = notes_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(course_name__icontains=search_query) |
            Q(course_code__icontains=search_query)
        )
    
    # Handle course code filter
    course_code = request.GET.get('course_code', '')
    if course_code:
        notes_list = notes_list.filter(course_code__icontains=course_code)
    
    # Handle sorting
    sort_by = request.GET.get('sort_by', 'recent')
    if sort_by == 'recent':
        notes_list = notes_list.order_by('-uploaded_at')
    elif sort_by == 'title_asc':
        notes_list = notes_list.order_by('title')
    elif sort_by == 'title_desc':
        notes_list = notes_list.order_by('-title')
    elif sort_by == 'popular':
        notes_list = notes_list.order_by('-downloads')  # You'll need to add a downloads field to your model
    
    # Pagination
    paginator = Paginator(notes_list, 9)  # Show 9 notes per page
    page = request.GET.get('page')
    notes = paginator.get_page(page)
    
    context = {
        'notes': notes,
    }
    
    return render(request, 'browse_notes.html', context)


# Add this view to track downloads
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import F

@require_POST
def track_download(request, note_id):
    try:
        note = Notes.objects.get(id=note_id)
        # Increment the downloads counter
        note.downloads = F('downloads') + 1
        note.save()
        return JsonResponse({'status': 'success'})
    except Notes.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)










def about(request):
    return render(request, 'about.html')

def index(request):
    return render(request, 'index.html')

def userlogin(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['emailid']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'login.html', d)



def your_profile(request):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    
    user = request.user
    try:
        data = SignUp.objects.get(user=user)
        # Count user's notes
        notes_count = Notes.objects.filter(user=user).count()
    except SignUp.DoesNotExist:
        return redirect('index')  # Or wherever appropriate
    
    return render(request, 'your_profile.html', {
        'data': data,
        'notes_count': notes_count
    })


def login_admin(request):
    return render(request, 'login_admin.html')



from django.shortcuts import render, redirect

from django.contrib import messages

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    data = SignUp.objects.get(user=user)
    error = ""
    
    if request.method == 'POST':
        # Get form data
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        contact = request.POST.get('contact')
        branch = request.POST.get('branch')
        
        try:
            # Update User model fields
            user.first_name = fname
            user.last_name = lname
            user.save()
            
            # Update SignUp model fields
            data.contact = contact
            data.branch = branch
            
            # Handle photo upload - Check if a new photo was uploaded
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                # Delete old photo if exists (optional)
                if data.photo:
                    data.photo.delete(save=False)
                data.photo = photo
                
            data.save()
            error = "no"
        except Exception as e:
            error = "yes"
            print(f"Error updating profile: {e}")
    
    context = {
        'user': user,
        'data': data,
        'error': error
    }
    return render(request, 'edit_profile.html', context)

def signUp(request):
    error = ""
    if request.method == "POST":
        try:
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            con = request.POST.get('con')
            emailid = request.POST.get('emailid')
            pwd = request.POST.get('pwd')
            branch = request.POST.get('branch')
            
            # First create the User object
            user = User.objects.create_user(
                username=emailid,  # Using email as username
                email=emailid,
                password=pwd,      # This will hash the password properly
                first_name=fname,
                last_name=lname
            )
            
            # Then create the SignUp profile and link it to the User
            photo = request.FILES.get('photo')
            student = SignUp(
                user=user,         # Link to the User object
                contact=con,
                branch=branch,
                photo=photo
            )
            student.save()
            error = "no"
        except Exception as e:
            error = "yes"
            print(f"Registration error: {e}")  # This will show the exact error in your console
    
    return render(request, 'signup.html', {'error': error})


def admin_home(request):
    if not request.user.is_staff:
        return redirect('login_admin')
    pn = Notes.objects.filter(status = "Pending").count()
    an = Notes.objects.filter(status = "Accept").count()
    rn = Notes.objects.filter(status = "Reject").count()
    alln = Notes.objects.all().count()
    d = {'pn' : pn, 'an' : an, 'rn' : rn, 'alln' : alln}
    return render(request, 'admin_home.html', d)


def login_admin(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username = u, password = p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    d = {'error' : error}
    return render(request, 'login_admin.html', d)

def Logout(request):
    logout(request)
    return redirect('index')

def profile(request):
    user = request.user  # Current logged-in user
    try:
        data = SignUp.objects.get(user=user)
    except SignUp.DoesNotExist:
        # Handle case where profile doesn't exist
        return redirect('create_profile')  # Or whatever is appropriate
        
    return render(request, 'profile.html', {'data': data})



def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    if request.method == "POST":
        o = request.POST['old']
        n = request.POST['new']
        c = request.POST['confirm']
        if c == n:
            u = User.objects.get(username__exact = request.user.username)
            u.set_password(n)
            u.save()
            error="no"
        else:
            error="yes"
    d = {'error' : error}
    return render(request, 'change_password.html', d)














# Now let's add the views in views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator


@login_required
def request_notes(request):
    if request.method == 'POST':
        form = NoteRequestForm(request.POST)
        if form.is_valid():
            note_request = form.save(commit=False)
            note_request.requested_by = request.user
            note_request.save()
            messages.success(request, 'Your request has been submitted successfully!')
            return redirect('view_all_requests')
    else:
        form = NoteRequestForm()
    
    return render(request, 'request_notes.html', {'form': form})

@login_required
def view_all_requests(request):
    # Get filter parameters
    status = request.GET.get('status', '')
    subject = request.GET.get('subject', '')
    search = request.GET.get('search', '')
    
    # Start with all requests
    requests = NoteRequest.objects.all().order_by('-date_created')
    
    # Apply filters
    if status:
        requests = requests.filter(status=status)
    if subject:
        requests = requests.filter(subject__icontains=subject)
    if search:
        requests = requests.filter(title__icontains=search)
    
    # Pagination
    paginator = Paginator(requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique subjects for filter dropdown
    subjects = NoteRequest.objects.values_list('subject', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'subjects': subjects,
        'current_status': status,
        'current_subject': subject,
        'search_query': search,
    }
    
    return render(request, 'view_all_requests.html', context)

@login_required
def request_detail(request, request_id):
    note_request = get_object_or_404(NoteRequest, id=request_id)
    responses = note_request.responses.all().order_by('date_created')
    
    if request.method == 'POST':
        form = RequestResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.note_request = note_request
            response.responder = request.user
            response.save()
            messages.success(request, 'Your response has been submitted!')
            return redirect('request_detail', request_id=request_id)
    else:
        form = RequestResponseForm()
    
    context = {
        'note_request': note_request,
        'responses': responses,
        'form': form,
    }
    
    return render(request, 'request_detail.html', context)

@login_required
def update_request_status(request, request_id):
    note_request = get_object_or_404(NoteRequest, id=request_id)
    
    # Only the request creator can update the status
    if request.user != note_request.requested_by:
        messages.error(request, 'You do not have permission to update this request.')
        return redirect('request_detail', request_id=request_id)
    
    new_status = request.POST.get('status')
    if new_status in [s[0] for s in NoteRequest.REQUEST_STATUS]:
        note_request.status = new_status
        note_request.save()
        messages.success(request, f'Request status updated to {new_status}.')
    
    return redirect('request_detail', request_id=request_id)

@login_required
def my_requests(request):
    requests = NoteRequest.objects.filter(requested_by=request.user).order_by('-date_created')
    
    # Pagination
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'my_requests.html', {'page_obj': page_obj})





def placement_dashboard(request):
    # Get all placement experiences shared by seniors
    senior_experiences = PlacementExperience.objects.all().order_by('-created_at')
    
    # Get company-wise resources
    companies = Company.objects.all()
    
    context = {
        'senior_experiences': senior_experiences,
        'companies': companies,
    }
    
    return render(request, 'placement_dashboard.html', context)












from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PlacementExperience, Company, PlacementQuestion, PlacementAnswer, PlacementComment


def placement_dashboard(request):
    # Get all placement experiences shared by seniors

    senior_experiences = PlacementExperience.objects.select_related('user__signup', 'company').all().order_by('-created_at')
    # senior_experiences = PlacementExperience.objects.all().order_by('-created_at')
    
    # Get company-wise resources
    companies = Company.objects.all()
    
    # Get placement questions for Q&A forum
    placement_questions = PlacementQuestion.objects.all().order_by('-created_at')
    
    context = {
        'senior_experiences': senior_experiences,
        'companies': companies,
        'placement_questions': placement_questions,
    }
    
    return render(request, 'placement_dashboard.html', context)

def placement_experience_detail(request, experience_id):
    experience = get_object_or_404(PlacementExperience, id=experience_id)
    comments = PlacementComment.objects.filter(experience=experience).order_by('-created_at')
    
    context = {
        'experience': experience,
        'comments': comments,
    }
    
    return render(request, 'placement_experience.html', context)

def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    experiences = PlacementExperience.objects.filter(company=company).order_by('-created_at')
    
    context = {
        'company': company,
        'experiences': experiences,
    }
    
    return render(request, 'company_detail.html', context)

@login_required
def add_placement_experience(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        job_role = request.POST.get('job_role')
        interview_date = request.POST.get('interview_date')
        package_offered = request.POST.get('package_offered')
        got_selected = request.POST.get('got_selected') == 'True'
        rounds_description = request.POST.get('rounds_description')
        technical_questions = request.POST.get('technical_questions')
        hr_questions = request.POST.get('hr_questions')
        preparation_strategy = request.POST.get('preparation_strategy')
        resources_used = request.POST.get('resources_used')
        tips_for_juniors = request.POST.get('tips_for_juniors')
        
        # Find or create the company with the provided name
        company, created = Company.objects.get_or_create(name=company_name)
        
        # Create new experience
        experience = PlacementExperience.objects.create(
            user=request.user,
            company=company,
            job_role=job_role,
            interview_date=interview_date,
            package_offered=package_offered,
            got_selected=got_selected,
            rounds_description=rounds_description,
            technical_questions=technical_questions,
            hr_questions=hr_questions,
            preparation_strategy=preparation_strategy,
            resources_used=resources_used,
            tips_for_juniors=tips_for_juniors
        )
        
        # Award points to the user for sharing placement experience
        try:
            profile = request.user.profile
            profile.points += 15  # Award 15 points for sharing a placement experience
            profile.save()
            messages.success(request, 'Your placement experience has been shared! You earned 15 points.')
        except:
            pass
            
        return redirect('placement_experience_detail', experience_id=experience.id)
    
    return redirect('placement_dashboard')

@login_required
def add_placement_question(request):
    if request.method == 'POST':
        question_text = request.POST.get('question')
        
        question = PlacementQuestion.objects.create(
            user=request.user,
            question=question_text
        )
        
    return redirect('placement_dashboard')

@login_required
def add_placement_answer(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(PlacementQuestion, id=question_id)
        answer_text = request.POST.get('answer')
        
        answer = PlacementAnswer.objects.create(
            question=question,
            user=request.user,
            answer=answer_text
        )
        
    return redirect('placement_dashboard')

@login_required
def add_placement_comment(request, experience_id):
    if request.method == 'POST':
        experience = get_object_or_404(PlacementExperience, id=experience_id)
        comment_text = request.POST.get('comment')
        
        comment = PlacementComment.objects.create(
            experience=experience,
            user=request.user,
            text=comment_text
        )
        
    return redirect('placement_experience_detail', experience_id=experience_id)





# views.py
from django.shortcuts import render



def resume_building(request):
    resources = [
        {'name': 'Harvard Resume Guide', 'url': 'https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/', 'description': 'Harvard Career Services guide for creating effective resumes'},
        {'name': 'Indeed Resume Builder', 'url': 'https://profile.indeed.com/build/name', 'description': 'Free online resume builder with professional templates'},
        {'name': 'Canva Resume Templates', 'url': 'https://www.canva.com/resumes/templates/', 'description': 'Designer resume templates for creative professions'},
        {'name': 'Overleaf LaTeX Resume', 'url': 'https://www.overleaf.com/gallery/tagged/cv', 'description': 'Professional LaTeX resume templates for tech roles'},
        {'name': 'Resume Worded', 'url': 'https://resumeworded.com/', 'description': 'AI-powered resume review and improvement suggestions'}
    ]
    return render(request, 'resume_building.html', {'resources': resources})

def technical_interview(request):
    core_subjects = [
        {'name': 'DBMS Basics', 'url': 'https://www.geeksforgeeks.org/dbms/', 'description': 'Database fundamentals: indexing, normalization, ACID, etc.'},
        {'name': 'Operating Systems', 'url': 'https://www.geeksforgeeks.org/operating-systems/', 'description': 'Processes, scheduling, deadlock, memory management'},
        {'name': 'Computer Networks', 'url': 'https://www.geeksforgeeks.org/computer-network-tutorials/', 'description': 'OSI model, TCP/IP, protocols, routing'},
        {'name': 'System Design Primer', 'url': 'https://github.com/donnemartin/system-design-primer', 'description': 'GitHub repo to learn scalable system design concepts'},
        {'name': 'SQL Practice', 'url': 'https://sqlzoo.net/', 'description': 'Interactive SQL tutorials and problem sets'},
        {'name': 'Machine Learning Basics', 'url': 'https://www.coursera.org/learn/machine-learning', 'description': 'Andrew Ng’s ML course for beginners'}
    ]

    dsa_sheets = [
        {'name': 'Striver SDE Sheet', 'url': 'https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/', 'description': 'DSA problem list from arrays to graphs'},
        {'name': 'NeetCode.io', 'url': 'https://neetcode.io/', 'description': 'Interview problems with YouTube solutions'},
        {'name': 'Love Babbar 450 Sheet', 'url': 'https://450dsa.com/', 'description': '450 top DSA problems for interviews'},
        {'name': 'Kunal Kushwaha DSA Bootcamp', 'url': 'https://github.com/kunal-kushwaha/DSA-Bootcamp-Java', 'description': 'Java DSA bootcamp with projects and assignments'},
        {'name': 'CP-Algorithms', 'url': 'https://cp-algorithms.com/', 'description': 'Algorithms and techniques used in CP'},
        {'name': 'VisuAlgo', 'url': 'https://visualgo.net/en', 'description': 'Visual walkthroughs for algorithms and data structures'}
    ]

    return render(request, 'technical_interview.html', {
        'core_subjects': core_subjects,
        'dsa_sheets': dsa_sheets
    })


def hr_interview(request):
    resources = [
        {'name': 'Big Interview', 'url': 'https://biginterview.com/', 'description': 'Video-based interview preparation platform'},
        {'name': 'Glassdoor Interview Questions', 'url': 'https://www.glassdoor.com/Interview/index.htm', 'description': 'Real interview questions from various companies'},
        {'name': 'HR Interview Questions PDF', 'url': 'https://www.tutorialride.com/hr-interview/hr-interview-questions-and-answers.htm', 'description': 'Comprehensive collection of common HR questions'},
        {'name': 'InterviewCake HR Guide', 'url': 'https://www.interviewcake.com/blog/behavioral-interview-questions', 'description': 'Tips for handling behavioral questions'},
        {'name': 'Pramp Mock Interviews', 'url': 'https://www.pramp.com/#/', 'description': 'Practice with peers through mock interviews'}
    ]
    return render(request, 'hr_interview.html', {'resources': resources})

def aptitude_tests(request):
    resources = [
        {'name': 'IndiaBix', 'url': 'https://www.indiabix.com/', 'description': 'Aptitude questions with explanations in all areas'},
        {'name': 'CareerRide', 'url': 'https://www.careerride.com/aptitude-test.aspx', 'description': 'Logical reasoning and quantitative aptitude practice'},
        {'name': 'PrepInsta', 'url': 'https://prepinsta.com/', 'description': 'Placement papers of various companies'},
        {'name': 'Sawaal', 'url': 'https://www.sawaal.com/', 'description': 'Aptitude and reasoning questions with solutions'},
        {'name': 'Testpot', 'url': 'https://testpot.com/', 'description': 'Company-specific aptitude test patterns'}
    ]
    return render(request, 'aptitude_tests.html', {'resources': resources})



# Add this function to your existing views.py

def coding_practice(request):
    platforms = [
        {'name': 'LeetCode', 'url': 'https://leetcode.com/', 'description': 'Most popular platform for coding challenges and interview prep'},
        {'name': 'Codeforces', 'url': 'https://codeforces.com/', 'description': 'Competitive programming contests and problems'},
        {'name': 'CodeChef', 'url': 'https://www.codechef.com/', 'description': 'Indian platform with long and lunchtime contests'},
        {'name': 'HackerRank', 'url': 'https://www.hackerrank.com/', 'description': 'Coding problems, domains, and skill certifications'},
        {'name': 'HackerEarth', 'url': 'https://www.hackerearth.com/', 'description': 'Practice problems and company hiring challenges'},
        {'name': 'AtCoder', 'url': 'https://atcoder.jp/', 'description': 'Japanese platform known for clean and tough problems'},
        {'name': 'TopCoder', 'url': 'https://www.topcoder.com/', 'description': 'One of the oldest and most respected CP platforms'},
        {'name': 'SPOJ', 'url': 'https://www.spoj.com/', 'description': 'Huge archive of classic algorithmic problems'},
        {'name': 'InterviewBit', 'url': 'https://www.interviewbit.com/', 'description': 'Topic-wise coding challenges in interview style'},
        {'name': 'CodeNinja', 'url': 'https://codeninja.com/', 'description': 'DSA-focused practice with structured learning paths'}
    ]

    learning_resources = [
        {'name': 'Striver A2Z DSA Sheet', 'url': 'https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/', 'description': 'Step-by-step DSA roadmap covering all key topics'},
        {'name': 'Love Babbar 450 Sheet', 'url': 'https://450dsa.com/', 'description': 'Curated set of 450 important DSA questions'},
        {'name': 'Kunal Kushwaha DSA Bootcamp', 'url': 'https://github.com/kunal-kushwaha/DSA-Bootcamp-Java', 'description': 'Beginner-friendly Java DSA bootcamp with projects'},
        {'name': 'CP-Algorithms', 'url': 'https://cp-algorithms.com/', 'description': 'In-depth competitive programming algorithms with theory'},
        {'name': 'VisuAlgo', 'url': 'https://visualgo.net/en', 'description': 'Visual explanation of DSA topics like trees, graphs, sorting'}
    ]

    return render(request, 'coding_practice.html', {
        'platforms': platforms,
        'learning_resources': learning_resources
    })














from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import NoteRequest, RequestReply, NoteFile
from .forms import NoteRequestForm, RequestReplyForm, NoteFileForm


def note_requests_list(request):
    """View for listing all note requests with filtering options"""
    all_requests = NoteRequest.objects.all()
    
    # Filter objects based on tab
    active_tab = request.GET.get('tab', 'all')
    
    if active_tab == 'my' and request.user.is_authenticated:
        all_requests = all_requests.filter(user=request.user)
    elif active_tab == 'open':
        all_requests = all_requests.filter(status='open')
    elif active_tab == 'solved':
        all_requests = all_requests.filter(status='solved')
    
    # Setup pagination
    paginator = Paginator(all_requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page', 1)
    note_requests = paginator.get_page(page_number)
    
    # Count requests for tabs
    if request.user.is_authenticated:
        my_requests_count = NoteRequest.objects.filter(user=request.user).count()
    else:
        my_requests_count = 0
        
    open_requests_count = NoteRequest.objects.filter(status='open').count()
    solved_requests_count = NoteRequest.objects.filter(status='solved').count()
    
    context = {
        'note_requests': note_requests,
        'active_tab': active_tab,
        'form': NoteRequestForm(),
        'all_count': NoteRequest.objects.count(),
        'my_count': my_requests_count,
        'open_count': open_requests_count,
        'solved_count': solved_requests_count,
    }
    
    return render(request, 'note_requests_list.html', context)


@login_required
def create_note_request(request):
    """View for creating a new note request"""
    if request.method == 'POST':
        form = NoteRequestForm(request.POST)
        if form.is_valid():
            note_request = form.save(commit=False)
            note_request.user = request.user
            note_request.save()
            messages.success(request, 'Your note request has been posted!')
            return redirect('note_request_detail', pk=note_request.pk)
    else:
        form = NoteRequestForm()
    
    return redirect('note_requests_list')


def note_request_detail(request, pk):
    """View for displaying a note request's details and replies"""
    note_request = get_object_or_404(NoteRequest, pk=pk)
    replies = note_request.replies.all()
    
    context = {
        'note_request': note_request,
        'replies': replies,
        'reply_form': RequestReplyForm(),
    }
    
    return render(request, 'note_request_detail.html', context)


@login_required
def add_reply(request, pk):
    """View for adding a reply to a note request"""
    note_request = get_object_or_404(NoteRequest, pk=pk)
    
    if request.method == 'POST':
        form = RequestReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.note_request = note_request
            reply.user = request.user
            reply.save()
            
            # Handle file uploads
            files = request.FILES.getlist('file')
            for f in files:
                note_file = NoteFile(reply=reply, file=f)
                note_file.save()
            
            # Award points for providing a helpful reply
            try:
                profile = request.user.profile
                profile.points += 5  # Award 5 points for replying to a note request
                profile.save()
                messages.success(request, 'Your reply has been posted! You earned 5 points.')
            except:
                messages.success(request, 'Your reply has been posted!')
    
    return redirect('note_request_detail', pk=pk)


@login_required
def mark_as_solved(request, pk):
    """View for marking a note request as solved"""
    note_request = get_object_or_404(NoteRequest, pk=pk)
    
    # Only allow the request owner to mark it as solved
    if request.user != note_request.user:
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    note_request.status = 'solved'
    note_request.save()
    messages.success(request, 'The request has been marked as solved!')
    
    return redirect('note_request_detail', pk=pk)


@login_required
def reopen_request(request, pk):
    """View for reopening a solved note request"""
    note_request = get_object_or_404(NoteRequest, pk=pk)
    
    # Only allow the request owner to reopen it
    if request.user != note_request.user:
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    note_request.status = 'open'
    note_request.save()
    messages.success(request, 'The request has been reopened!')
    
    return redirect('note_request_detail', pk=pk)




def contact(request):
    return render(request, 'contact.html')













# Import necessary modules
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from datetime import datetime, timedelta
import secrets



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate a secure token
            token = secrets.token_urlsafe(32)
            
            # Set expiration time (24 hours from now)
            expiry = datetime.now() + timedelta(hours=24)
            
            # Save the token in the database
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expiry
            )
            
            # Build the reset link
            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'token': token})
            )
            
            # Send email with the reset link
            subject = 'Reset Your VITStudyMates Password'
            message = f'''
            Hello {user.first_name},
            
            You've requested to reset your password for your VITStudyMates account.
            
            Please click the link below to reset your password:
            {reset_url}
            
            This link will expire in 24 hours.
            
            If you didn't request this, please ignore this email or contact support.
            
            Best regards,
            VITStudyMates Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return render(request, 'forgot_password.html', {
                'message': 'Password reset link has been sent to your email address.',
                'message_type': 'success'
            })
            
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {
                'message': 'No account found with that email address.',
                'message_type': 'error'
            })
    
    return render(request, 'forgot_password.html')
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.shortcuts import render

def reset_password(request, token):
    try:
        # Check if token exists and is valid
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        # Fixed timezone comparison
        if reset_token.expires_at < timezone.now():
            return render(request, 'reset_password.html', {
                'valid_token': False,
                'message': 'Password reset link has expired.',
                'message_type': 'error'
            })
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords
            if new_password != confirm_password:
                return render(request, 'reset_password.html', {
                    'valid_token': True,
                    'token': token,
                    'message': 'Passwords do not match.',
                    'message_type': 'error'
                })
            
            # Check password strength (implement your own logic if needed)
            if len(new_password) < 8:
                return render(request, 'reset_password.html', {
                    'valid_token': True,
                    'token': token,
                    'message': 'Password must be at least 8 characters long.',
                    'message_type': 'error'
                })
            
            # Update the user's password
            user = reset_token.user
            user.password = make_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            return render(request, 'reset_password.html', {
                'valid_token': False,
                'message': 'Your password has been reset successfully. Redirecting to login...',
                'message_type': 'success',
                'password_reset_success': True
            })
        
        return render(request, 'reset_password.html', {
            'valid_token': True,
            'token': token
        })
        
    except PasswordResetToken.DoesNotExist:
        return render(request, 'reset_password.html', {
            'valid_token': False,
            'message': 'Invalid password reset link.',
            'message_type': 'error'
        })



# q paper
# views.py
# views.py
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.contrib import messages
from django.db.models import Q
from .models import SemesterPaper, Course
from .forms import PaperUploadForm

@login_required
def semester_dashboard(request):
    course_errors = None

    # Handle upload form submission
    if request.method == 'POST' and 'upload' in request.POST:
        upload_form = PaperUploadForm(request.POST, request.FILES)
        course_code = request.POST.get('course_code', '').strip()
        course_title = request.POST.get('course_title', '').strip()

        if not course_code or not course_title:
            course_errors = "Course code and title are required."
        elif upload_form.is_valid():
            course, created = Course.objects.get_or_create(
                code=course_code,
                defaults={'title': course_title}
            )

            if not created and course.title != course_title:
                course.title = course_title
                course.save()

            paper = upload_form.save(commit=False)
            paper.course = course
            paper.uploaded_by = request.user
            paper.year = 2025
            paper.semester = 'FALL'
            paper.save()
            
            # Award points to the user for uploading semester paper
            try:
                profile = request.user.profile
                profile.points += 20  # Award 20 points for uploading a semester paper
                profile.save()
                messages.success(request, "Paper uploaded successfully! You earned 20 points.")
            except:
                messages.success(request, "Paper uploaded successfully!")
                
            return redirect('semester_dashboard')
    else:
        upload_form = PaperUploadForm()

    # Rest of your view remains the same
    course_search = request.GET.get('course_search', '').strip()
    papers = SemesterPaper.objects.all().order_by('-upload_date')

    if course_search:
        papers = papers.filter(
            Q(course__code__iexact=course_search) | 
            Q(course__title__icontains=course_search)
        )

    context = {
        'upload_form': upload_form,
        'papers': papers,
        'course_search': course_search,
        'course_errors': course_errors,
    }

    return render(request, 'semester_dashboard.html', context)

@login_required
def download_paper(request, paper_id):
    paper = get_object_or_404(SemesterPaper, id=paper_id)
    return FileResponse(paper.file, as_attachment=True)





# points
from django.contrib.auth.models import User
from .models import Profile  # Ensure Profile is imported

@login_required
def leaderboard(request):
    top_users = Profile.objects.select_related('user').order_by('-points')[:5]
    return render(request, 'leaderboard.html', {'top_users': top_users})




#logout
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('login')  # or whatever page you want to redirect to
