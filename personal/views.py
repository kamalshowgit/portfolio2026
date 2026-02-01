from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Profile, QuickLink, Project, Note, ContactMessage, Experience, Education
from .forms import ProfileForm, QuickLinkForm, ProjectForm, NoteForm, ContactForm, ExperienceForm, EducationForm
from django.conf import settings
from django.http import JsonResponse

# Dummy credentials (adjustable)
DUMMY_USERNAME = 'admin'
DUMMY_PASSWORD = 'changeme'


def index(request):
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create(name='Kamal Soni')
    links = profile.links.all()
    projects = profile.projects.all()
    experiences = profile.experiences.all()
    educations = profile.educations.all()
    # Only show notes to logged-in users
    notes = profile.notes.order_by('-created_at') if request.session.get('personal_logged_in') else []
    return render(request, 'personal/index.html', {
        'profile': profile,
        'links': links,
        'projects': projects,
        'notes': notes,
        'experiences': experiences,
        'educations': educations,
        'is_logged_in': request.session.get('personal_logged_in', False),
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
            request.session['personal_logged_in'] = True
            # If AJAX, return JSON success
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('personal:edit')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
            return render(request, 'personal/login.html', {'error': 'Invalid credentials'})
    return render(request, 'personal/login.html')


def update_profile(request):
    # AJAX endpoint to update profile fields (requires session login)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if not request.session.get('personal_logged_in'):
        return JsonResponse({'error': 'Authentication required'}, status=403)

    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create(name='Kamal Soni')

    # accept both form-encoded and multipart (for photo)
    name = request.POST.get('name')
    title = request.POST.get('title')
    bio = request.POST.get('bio')
    email = request.POST.get('email')
    linkedin = request.POST.get('linkedin')
    github = request.POST.get('github')
    location = request.POST.get('location')
    phone = request.POST.get('phone')

    if name is not None:
        profile.name = name
    if title is not None:
        profile.title = title
    if bio is not None:
        profile.bio = bio
    if email is not None:
        profile.email = email
    if linkedin is not None:
        profile.linkedin = linkedin
    if github is not None:
        profile.github = github
    if location is not None:
        profile.location = location
    if phone is not None:
        profile.phone = phone

    if request.FILES.get('photo'):
        profile.photo = request.FILES.get('photo')

    profile.save()

    return JsonResponse({'success': True, 'profile': {
        'name': profile.name,
        'title': profile.title,
        'bio': profile.bio,
        'email': profile.email,
        'linkedin': profile.linkedin,
        'github': profile.github,
        'location': profile.location,
        'phone': profile.phone,
        'photo_url': profile.photo.url if profile.photo else ''
    }})


def logout_view(request):
    request.session.pop('personal_logged_in', None)
    return redirect('personal:index')


def contact_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Message sent! Thank you for reaching out.'})
            return redirect('personal:index')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Please fill in all fields correctly.'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=405)


def edit_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('personal_logged_in'):
            return redirect('personal:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@edit_required
def edit(request):
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create(name='Kamal Soni')

    if request.method == 'POST':
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if pform.is_valid():
            pform.save()
            return redirect('personal:edit')
    else:
        pform = ProfileForm(instance=profile)

    qform = QuickLinkForm()
    prform = ProjectForm()
    exform = ExperienceForm()
    edform = EducationForm()
    nform = NoteForm()

    links = profile.links.all()
    projects = profile.projects.all()
    experiences = profile.experiences.all()
    educations = profile.educations.all()
    notes = profile.notes.order_by('-created_at')

    return render(request, 'personal/edit.html', {
        'profile': profile,
        'pform': pform,
        'qform': qform,
        'prform': prform,
        'exform': exform,
        'edform': edform,
        'nform': nform,
        'links': links,
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
        'notes': notes,
    })


@edit_required
def add_link(request):
    profile = Profile.objects.first()
    if request.method == 'POST':
        form = QuickLinkForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
    return redirect('personal:edit')


@edit_required
def delete_link(request, pk):
    link = get_object_or_404(QuickLink, pk=pk)
    link.delete()
    return redirect('personal:edit')


@edit_required
def add_project(request):
    profile = Profile.objects.first()
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
    return redirect('personal:edit')


@edit_required
def delete_project(request, pk):
    pr = get_object_or_404(Project, pk=pk)
    pr.delete()
    return redirect('personal:edit')


@edit_required
def add_experience(request):
    profile = Profile.objects.first()
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
    return redirect('personal:edit')


@edit_required
def delete_experience(request, pk):
    ex = get_object_or_404(Experience, pk=pk)
    ex.delete()
    return redirect('personal:edit')


@edit_required
def add_education(request):
    profile = Profile.objects.first()
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
    return redirect('personal:edit')


@edit_required
def delete_education(request, pk):
    ed = get_object_or_404(Education, pk=pk)
    ed.delete()
    return redirect('personal:edit')


@edit_required
def add_note(request):
    profile = Profile.objects.first()
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
    return redirect('personal:edit')


@edit_required
def toggle_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.completed = not note.completed
    note.save()
    return redirect('personal:edit')


@edit_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return redirect('personal:edit')
