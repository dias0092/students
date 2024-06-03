from django.contrib import admin
from django import forms

from apps.studyplan.models import Semester, University, Subject, StudyPlan, ClassSchedule, SubjectSemester, Faculty
from apps.studyplan.form import SubjectSemesterForm


class FacultyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.university.name})"


class StudyPlanForm(forms.ModelForm):
    class Meta:
        model = StudyPlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subjects'].queryset = Subject.objects.all()
        self.fields['subjects'].help_text = "Select subjects (University - Subject Title)"

        # Overriding the labels to include the university name
        self.fields['subjects'].label_from_instance = lambda obj: f"{obj.university.name} - {obj.title}"


class SubjectAdminForm(forms.ModelForm):
    faculty = FacultyModelChoiceField(queryset=Faculty.objects.all())

    class Meta:
        model = Subject
        fields = '__all__'


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('year', 'term', 'credit_limit')
    search_fields = ('year', 'term')


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ('title', 'description', 'code', 'credits', 'university', 'get_offered_semesters', 'get_faculty_and_university')
    list_filter = ('university', 'offered_semesters', 'faculty')
    search_fields = ('title', 'code')

    def get_offered_semesters(self, obj):
        return ", ".join([f"{semester.term} {semester.year}" for semester in obj.offered_semesters.all()])
    get_offered_semesters.short_description = 'Offered Semesters'

    def get_faculty_and_university(self, obj):
        return f"{obj.faculty} ({obj.university})"
    get_faculty_and_university.short_description = 'Faculty (University)'


class StudyPlanAdmin(admin.ModelAdmin):
    form = StudyPlanForm
    list_display = ('student', 'semester', 'total_credits', 'get_subject_names')
    list_filter = ('semester',)
    search_fields = ('student__user__username',)

    def get_subject_names(self, obj):
        return ", ".join([f"{subject.university.name} - {subject.title}" for subject in obj.subjects.all()])
    get_subject_names.short_description = 'Subjects (University)'


class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'get_subject_title', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('semester', 'day_of_week', 'subject_semester__subject')
    search_fields = ('student__user__username', 'subject_semester__subject__title')

    def get_subject_title(self, obj):
        return f"{obj.subject_semester.subject.title} ({obj.subject_semester.subject.university.name})"
    get_subject_title.admin_order_field = 'subject_semester__subject'
    get_subject_title.short_description = 'Subject (University)'


class SubjectSemesterAdmin(admin.ModelAdmin):
    form = SubjectSemesterForm
    list_display = ('get_subject_with_university', 'get_faculty_name', 'semester', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('subject', 'semester', 'day_of_week', 'subject__faculty')
    search_fields = ('subject__title', 'semester__term')

    def get_subject_with_university(self, obj):
        return f"{obj.subject.title} ({obj.subject.university.name})"
    get_subject_with_university.admin_order_field = 'subject'
    get_subject_with_university.short_description = 'Subject (University)'

    def get_faculty_name(self, obj):
        return obj.subject.faculty.name if obj.subject.faculty else 'N/A'
    get_faculty_name.admin_order_field = 'subject__faculty'
    get_faculty_name.short_description = 'Faculty Name'


class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'university')
    search_fields = ('name', 'university')


admin.site.register(Semester, SemesterAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(StudyPlan, StudyPlanAdmin)
admin.site.register(ClassSchedule, ClassScheduleAdmin)
admin.site.register(SubjectSemester, SubjectSemesterAdmin)