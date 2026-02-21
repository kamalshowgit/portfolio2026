from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, QuickLink, Project, Note, ContactMessage, Experience, Education, CalendarTodo
from .forms import ProfileForm, QuickLinkForm, ProjectForm, NoteForm, ContactForm, ExperienceForm, EducationForm
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.core.mail import EmailMessage
from datetime import date
import re

MONTH_TO_NUM = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def _get_profile():
    profile = Profile.objects.first()
    if not profile:
        profile = Profile.objects.create(name='Kamal Soni')
    return profile


def _normalize_section(section):
    aliases = {
        'experience': 'experience',
        'experiences': 'experience',
        'education': 'education',
        'educations': 'education',
        'projects': 'projects',
        'project': 'projects',
        'links': 'links',
        'link': 'links',
        'notes': 'notes',
        'note': 'notes',
    }
    return aliases.get((section or '').strip().lower())


def _redirect_edit(section=None, obj_id=None):
    url = reverse('personal:edit')
    section_name = _normalize_section(section)
    if section_name:
        url += f'?section={section_name}'
        if obj_id:
            url += f'&id={obj_id}'
    return redirect(url)


def _parse_period_sort_key(value):
    text = (value or '').strip()
    month_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(19|20)\d{2}', text, re.I)
    if month_match:
        month_name = month_match.group(1).lower()
        year = int(re.search(r'(19|20)\d{2}', month_match.group(0)).group(0))
        return year, MONTH_TO_NUM.get(month_name, 0)
    year_match = re.search(r'(19|20)\d{2}', text)
    if year_match:
        return int(year_match.group(0)), 0
    return 0, 0


def index(request):
    profile = _get_profile()
    links = profile.links.all()
    projects = profile.projects.all()
    experiences = profile.experiences.order_by('-id')
    educations = profile.educations.order_by('-year', '-id')
    # Only show notes to logged-in users
    notes = profile.notes.order_by('-created_at') if request.session.get('personal_logged_in') else []

    timeline = []
    for ex in experiences:
        yr, mon = _parse_period_sort_key(ex.start or ex.end)
        timeline.append({
            'kind': 'Work',
            'title': ex.title or ex.employer,
            'subtitle': ex.employer,
            'period': f"{ex.start or ''}{' - ' + ex.end if ex.end else ''}".strip(' -'),
            'year': yr,
            'month': mon,
        })
    for ed in educations:
        yr, mon = _parse_period_sort_key(ed.year)
        timeline.append({
            'kind': 'Education',
            'title': ed.degree or ed.institution,
            'subtitle': ed.institution,
            'period': ed.year,
            'year': yr,
            'month': mon,
        })
    timeline = sorted(timeline, key=lambda x: (x['year'], x['month']), reverse=True)

    skills_by_group = [
        {'group': 'Programming & Data', 'items': 'Python, SQL, SAS, PySpark, Excel/VBA'},
        {'group': 'Machine Learning', 'items': 'Logistic Regression, XGBoost, LightGBM, Random Forest, Decision Trees'},
        {'group': 'Model Risk & Validation', 'items': 'PSI, CSI, KS Statistic, ROC-AUC, Lift Analysis, Drift Detection'},
        {'group': 'Analytics Techniques', 'items': 'Customer Segmentation, A/B Testing, Uplift Modeling, Campaign Analytics'},
        {'group': 'Visualization & BI', 'items': 'Power BI, Qlik, Matplotlib, Seaborn, Plotly'},
    ]
    achievements = [
        '1st Place Worldwide - Kaggle Bankruptcy Prediction Challenge',
        'Employee of the Year (Rising Star) - HSBC (2025)',
        'Top 1% in State (Class XII) - Fully Sponsored B.E.',
        'Certifications: CS50 (Harvard), Python for Data Science (IIT Madras), DSA (IIT Madras), SEBI/NISM',
    ]

    return render(request, 'personal/index.html', {
        'profile': profile,
        'links': links,
        'projects': projects,
        'notes': notes,
        'experiences': experiences,
        'educations': educations,
        'timeline': timeline,
        'skills_by_group': skills_by_group,
        'achievements': achievements,
        'is_logged_in': request.session.get('personal_logged_in', False),
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == settings.PERSONAL_EDIT_USERNAME and password == settings.PERSONAL_EDIT_PASSWORD:
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

    profile = _get_profile()

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
            message_obj = form.save()
            profile = _get_profile()
            receiver_email = settings.CONTACT_RECEIVER_EMAIL or profile.email

            if not receiver_email:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(
                        {'success': False, 'error': 'Message saved, but inbox email is not configured.'},
                        status=500
                    )
                return redirect('personal:index')

            try:
                mail = EmailMessage(
                    subject=f"[Portfolio Contact] {message_obj.subject}",
                    body=(
                        f"New portfolio contact message\n\n"
                        f"From: {message_obj.name} <{message_obj.email}>\n"
                        f"Submitted: {message_obj.created_at}\n\n"
                        f"Message:\n{message_obj.message}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[receiver_email],
                    reply_to=[message_obj.email]
                )
                mail.send(fail_silently=False)
            except Exception:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(
                        {'success': False, 'error': 'Message saved, but email could not be delivered.'},
                        status=502
                    )
                return redirect('personal:index')
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
    profile = _get_profile()

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

    # Optional focus params to pre-select or pre-fill a form on the edit page
    focus_section = _normalize_section(request.GET.get('section'))
    focus_id = request.GET.get('id')
    if focus_section and focus_id:
        try:
            if focus_section == 'experience':
                obj = Experience.objects.get(pk=focus_id, profile=profile)
                exform = ExperienceForm(instance=obj)
            elif focus_section == 'education':
                obj = Education.objects.get(pk=focus_id, profile=profile)
                edform = EducationForm(instance=obj)
            elif focus_section == 'projects':
                obj = Project.objects.get(pk=focus_id, profile=profile)
                prform = ProjectForm(instance=obj)
            elif focus_section == 'links':
                obj = QuickLink.objects.get(pk=focus_id, profile=profile)
                qform = QuickLinkForm(instance=obj)
            elif focus_section == 'notes':
                obj = Note.objects.get(pk=focus_id, profile=profile)
                nform = NoteForm(instance=obj)
        except Exception:
            # ignore errors and render default forms
            focus_section = None
            focus_id = None

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
        'focus_section': focus_section,
        'focus_id': focus_id,
    })


@edit_required
def add_link(request):
    profile = _get_profile()
    if request.method == 'POST':
        link_id = request.POST.get('link_id')
        instance = get_object_or_404(QuickLink, pk=link_id, profile=profile) if link_id else None
        form = QuickLinkForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return _redirect_edit('links', obj.pk)
    return _redirect_edit('links')


@edit_required
def delete_link(request, pk):
    profile = _get_profile()
    if request.method == 'POST':
        link = get_object_or_404(QuickLink, pk=pk, profile=profile)
        link.delete()
    return _redirect_edit('links')


@edit_required
def add_project(request):
    profile = _get_profile()
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        instance = get_object_or_404(Project, pk=project_id, profile=profile) if project_id else None
        form = ProjectForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return _redirect_edit('projects', obj.pk)
    return _redirect_edit('projects')


@edit_required
def delete_project(request, pk):
    profile = _get_profile()
    if request.method == 'POST':
        pr = get_object_or_404(Project, pk=pk, profile=profile)
        pr.delete()
    return _redirect_edit('projects')


@edit_required
def add_experience(request):
    profile = _get_profile()
    if request.method == 'POST':
        experience_id = request.POST.get('experience_id')
        instance = get_object_or_404(Experience, pk=experience_id, profile=profile) if experience_id else None
        form = ExperienceForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return _redirect_edit('experience', obj.pk)
    return _redirect_edit('experience')


@edit_required
def delete_experience(request, pk):
    profile = _get_profile()
    if request.method == 'POST':
        ex = get_object_or_404(Experience, pk=pk, profile=profile)
        ex.delete()
    return _redirect_edit('experience')


@edit_required
def add_education(request):
    profile = _get_profile()
    if request.method == 'POST':
        education_id = request.POST.get('education_id')
        instance = get_object_or_404(Education, pk=education_id, profile=profile) if education_id else None
        form = EducationForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return _redirect_edit('education', obj.pk)
    return _redirect_edit('education')


@edit_required
def delete_education(request, pk):
    profile = _get_profile()
    if request.method == 'POST':
        ed = get_object_or_404(Education, pk=pk, profile=profile)
        ed.delete()
    return _redirect_edit('education')


@edit_required
def add_note(request):
    profile = _get_profile()
    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        instance = get_object_or_404(Note, pk=note_id, profile=profile) if note_id else None
        form = NoteForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return _redirect_edit('notes', obj.pk)
    return _redirect_edit('notes')


@edit_required
def toggle_note(request, pk):
    profile = _get_profile()
    if request.method == 'POST':
        note = get_object_or_404(Note, pk=pk, profile=profile)
        note.completed = not note.completed
        note.save()
    return _redirect_edit('notes')


@edit_required
def delete_note(request, pk):
    profile = _get_profile()
    if request.method == 'POST':
        note = get_object_or_404(Note, pk=pk, profile=profile)
        note.delete()
    return _redirect_edit('notes')


def calendar_todos(request):
    if not request.session.get('personal_logged_in'):
        return JsonResponse({'error': 'Authentication required'}, status=403)

    profile = _get_profile()
    month_param = request.GET.get('month', '')
    try:
        year, month = [int(x) for x in month_param.split('-')]
    except Exception:
        today = date.today()
        year, month = today.year, today.month

    items = CalendarTodo.objects.filter(
        profile=profile,
        day__year=year,
        day__month=month
    ).order_by('day', 'completed', '-created_at')

    payload = [
        {
            'id': obj.pk,
            'day': obj.day.isoformat(),
            'text': obj.text,
            'completed': obj.completed,
        }
        for obj in items
    ]
    return JsonResponse({'success': True, 'items': payload})


def add_calendar_todo(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not request.session.get('personal_logged_in'):
        return JsonResponse({'error': 'Authentication required'}, status=403)

    profile = _get_profile()
    day_str = (request.POST.get('day') or '').strip()
    text = (request.POST.get('text') or '').strip()
    if not day_str or not text:
        return JsonResponse({'error': 'Both day and text are required.'}, status=400)
    try:
        todo_day = date.fromisoformat(day_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)

    obj = CalendarTodo.objects.create(profile=profile, day=todo_day, text=text[:220])
    return JsonResponse({
        'success': True,
        'item': {'id': obj.pk, 'day': obj.day.isoformat(), 'text': obj.text, 'completed': obj.completed}
    })


def toggle_calendar_todo(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not request.session.get('personal_logged_in'):
        return JsonResponse({'error': 'Authentication required'}, status=403)

    profile = _get_profile()
    obj = get_object_or_404(CalendarTodo, pk=pk, profile=profile)
    obj.completed = not obj.completed
    obj.save(update_fields=['completed'])
    return JsonResponse({'success': True, 'completed': obj.completed})


def delete_calendar_todo(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not request.session.get('personal_logged_in'):
        return JsonResponse({'error': 'Authentication required'}, status=403)

    profile = _get_profile()
    obj = get_object_or_404(CalendarTodo, pk=pk, profile=profile)
    obj.delete()
    return JsonResponse({'success': True})
