from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View

from .forms import ModuleFormSet
from .models import Course, Module, Content


class CreateCourse(LoginRequiredMixin, PermissionRequiredMixin,
                   CreateView):
    model = Course
    fields = ['title', 'subject', 'slug', 'overview', 'course_image']
    template_name = 'courses/create_course.html'
    permission_required = 'courses.add_course'
    login_url = reverse_lazy('users:login')
    raise_exception = True
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_page.html'
    context_object_name = 'course'
    # login_url = reverse_lazy('users:login')


class CourseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'courses/update_course.html'
    model = Course
    permission_required = 'courses.change_course'
    login_url = reverse_lazy('users:login')
    raise_exception = True
    context_object_name = 'course'
    fields = ['title', 'subject', 'slug', 'overview', 'course_image']
    success_url = reverse_lazy('home')


class CourseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Course
    permission_required = 'courses.delete_course'
    template_name = 'courses/delete_course.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('users:login')


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/add_modules_course.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('home')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/module_contents.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                       id=module_id,
                                       course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            print(self.module.course.id)
            return redirect('courses:course-detail', self.module.course.slug)

        return self.render_to_response({'form': form,
                                        'object': self.obj})


@login_required
def student_enrollment(request, course_slug):
    if request.method == 'POST':
        print('get post req')
        try:
            course = Course.objects.get(slug=course_slug)
            if course is not None:
                students = course.students.all()
                print(students)
                if request.user not in students:
                    course.students.add(request.user)
                    return redirect(reverse_lazy('users:profile'))
                else:
                    messages.add_message(request, messages.WARNING, 'You already enrolled in this course.')
                    return redirect(reverse_lazy('home'))
            else:
                messages.add_message(request, messages.WARNING, 'Course does not exist!')
                return redirect(reverse_lazy('home'))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, 'Course not found!')
            return redirect(reverse_lazy('home'))


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_student_view.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                                    id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context


def course_by_subject(request, slug):
    if request.method == 'GET':
        context = {}
        try:
            courses = Course.objects.filter(subject__slug=slug)
            context['courses'] = courses
            return render(request, 'courses/courses_by_subject.html', context)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, 'Could not found any course.')
            return redirect(reverse_lazy('home'))

