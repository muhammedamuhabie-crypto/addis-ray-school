from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from .final_views import (
    PromotionAPIView,
    StudentReportAPIView,
    ClassReportAPIView,
    SchoolPerformanceAPIView,
    AttendanceReportAPIView,
)

from .views import (
    StudentViewSet,
    TeacherViewSet,
    CurrentUserView,

    DirectorAuthorizationView,
    TeacherAuthorizationView,
    StudentAuthorizationView,

    StudentsServiceAuthorizationView,
    TeachersServiceAuthorizationView,
    AcademicsServiceAuthorizationView,
    AttendanceServiceAuthorizationView,
    PromotionServiceAuthorizationView,
    ReportsServiceAuthorizationView,
    SettingsServiceAuthorizationView,

    SubjectViewSet,
    ClassRoomViewSet,
    GradeRecordViewSet,
    StudentResultsAPIView,
    StudentAverageAPIView,
    RankingAPIView,
    AttendanceViewSet,
)


router = DefaultRouter()

router.register(
    r'students',
    StudentViewSet,
    basename='student'
)

router.register(
    r'teachers',
    TeacherViewSet,
    basename='teacher'
)

router.register(
    r'academics/subjects',
    SubjectViewSet,
    basename='subject'
)

router.register(
    r'academics/classes',
    ClassRoomViewSet,
    basename='classroom'
)

router.register(
    r'academics/grades',
    GradeRecordViewSet,
    basename='grade'
)

router.register(
    r'attendance',
    AttendanceViewSet,
    basename='attendance'
)

urlpatterns = [

    # ==========================================
    # AUTHENTICATION
    # ==========================================

    path(
        'auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path(
        'auth/me/',
        CurrentUserView.as_view(),
        name='current_user'
    ),


    # ==========================================
    # AUTHORIZATION
    # ==========================================

    path(
        'authorization/director/',
        DirectorAuthorizationView.as_view(),
        name='authorization_director'
    ),

    path(
        'authorization/teacher/',
        TeacherAuthorizationView.as_view(),
        name='authorization_teacher'
    ),

    path(
        'authorization/student/',
        StudentAuthorizationView.as_view(),
        name='authorization_student'
    ),


    # ==========================================
    # SERVICE AUTHORIZATION
    # ==========================================

    path(
        'services/students/',
        StudentsServiceAuthorizationView.as_view(),
        name='service_students'
    ),

    path(
        'services/teachers/',
        TeachersServiceAuthorizationView.as_view(),
        name='service_teachers'
    ),

    path(
        'services/academics/',
        AcademicsServiceAuthorizationView.as_view(),
        name='service_academics'
    ),

    path(
        'services/attendance/',
        AttendanceServiceAuthorizationView.as_view(),
        name='service_attendance'
    ),

    path(
        'services/promotion/',
        PromotionServiceAuthorizationView.as_view(),
        name='service_promotion'
    ),

    path(
        'services/reports/',
        ReportsServiceAuthorizationView.as_view(),
        name='service_reports'
    ),

    path(
        'services/settings/',
        SettingsServiceAuthorizationView.as_view(),
        name='service_settings'
    ),


    # ==========================================
    # ACADEMIC RESULTS
    # ==========================================

    path(
        'academics/results/<int:student_id>/',
        StudentResultsAPIView.as_view(),
        name='student_results_api'
    ),

    path(
        'academics/average/<int:student_id>/',
        StudentAverageAPIView.as_view(),
        name='student_average_api'
    ),

    path(
        'academics/ranking/',
        RankingAPIView.as_view(),
        name='ranking_api'
    ),
]


# ==========================================
# PROMOTION
# ==========================================

urlpatterns += [
    path(
        'promotion/',
        PromotionAPIView.as_view(),
        name='promotion_api'
    ),

    # ==========================================
    # REPORTS
    # ==========================================

    path(
        'reports/student/',
        StudentReportAPIView.as_view(),
        name='student_report_api'
    ),

    path(
        'reports/class/',
        ClassReportAPIView.as_view(),
        name='class_report_api'
    ),

    path(
        'reports/school/',
        SchoolPerformanceAPIView.as_view(),
        name='school_performance_api'
    ),

    path(
        'reports/attendance/',
        AttendanceReportAPIView.as_view(),
        name='attendance_report_api'
    ),
]


urlpatterns += router.urls


