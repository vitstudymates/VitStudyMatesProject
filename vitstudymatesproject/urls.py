from django.urls import path
from notes.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    
    # Auth & Profile
    path('login', userlogin, name='login'),
    path('signup', signUp, name='signup'),
    path('logout', logout_view, name='logout'),
    path('profile', profile, name='profile'),
    path('your_profile/', your_profile, name='your_profile'),
    path('edit_profile', edit_profile, name='edit_profile'),
    path('change_password/', change_password, name='password_change'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', reset_password, name='reset_password'),

    # Notes
    path('notes/', notes_dashboard, name='notes_dashboard'),
    path('upload-notes/', upload_notes, name='upload_notes'),
    path('browse-notes/', browse_notes, name='browse_notes'),
    path('track-download/<int:note_id>/', track_download, name='track_download'),

    # Note Requests
    path('request-notes/', request_notes, name='request_notes'),
    path('view-all-requests/', view_all_requests, name='view_all_requests'),
    path('request-detail/<int:request_id>/', request_detail, name='request_detail'),
    path('update-request-status/<int:request_id>/', update_request_status, name='update_request_status'),
    path('my-requests/', my_requests, name='my_requests'),

    # Note Requests (Public Forum-style)
    path('requests/', note_requests_list, name='note_requests_list'),
    path('create/', create_note_request, name='create_note_request'),
    path('<int:pk>/', note_request_detail, name='note_request_detail'),
    path('<int:pk>/reply/', add_reply, name='add_reply'),
    path('<int:pk>/mark-solved/', mark_as_solved, name='mark_as_solved'),
    path('<int:pk>/reopen/', reopen_request, name='reopen_request'),

    # Placement
    path('placement_dashboard/', placement_dashboard, name='placement_dashboard'),
    path('placement/experience/<int:experience_id>/', placement_experience_detail, name='placement_experience_detail'),
    path('placement/company/<int:company_id>/', company_detail, name='company_detail'),
    path('placement/add-experience/', add_placement_experience, name='add_placement_experience'),
    path('placement/add-question/', add_placement_question, name='add_placement_question'),
    path('placement/add-answer/<int:question_id>/', add_placement_answer, name='add_placement_answer'),

    # Resume & Interview Help
    path('resume_building/', resume_building, name='resume_building'),
    path('technical_interview/', technical_interview, name='technical_interview'),
    path('hr_interview/', hr_interview, name='hr_interview'),
    path('aptitude_tests/', aptitude_tests, name='aptitude_tests'),
    path('coding_practice/', coding_practice, name='coding_practice'),

    # Academics
    path('semester-exam/', semester_dashboard, name='semester_dashboard'),
    path('download-paper/<int:paper_id>/', download_paper, name='download_paper'),

    # Other
    path('about', about, name='about'),
    path('contact/', contact, name='contact'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]

# Static & Media (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
