from django.urls import path
from .views import CreateCourse, CourseDetailView, CourseUpdateView,\
    CourseDeleteView, CourseModuleUpdateView, ContentCreateUpdateView, student_enrollment, \
    StudentCourseDetailView, course_by_subject

app_name = 'courses'

urlpatterns = [
    path('create', CreateCourse.as_view(), name='create-course'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail'),
    path('edit/<slug:slug>/', CourseUpdateView.as_view(), name='course-edit'),
    path('delete/<slug:slug>/', CourseDeleteView.as_view(), name='course-delete'),
    path('<pk>/module/', CourseModuleUpdateView.as_view(), name='course-modules-update'),
    path('module/<int:module_id>/content/<model_name>/create/',
         ContentCreateUpdateView.as_view(),
         name='module-content-create'),
    path('<slug:course_slug>/enrollment', student_enrollment, name='student-enrollment'),
    path('course/<pk>/', StudentCourseDetailView.as_view(), name='student-course-view'),
    path('category/<slug>', course_by_subject, name='courses-by-subject')
]
