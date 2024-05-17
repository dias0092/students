from django.contrib import admin
from apps.studyplan.models import Semester, University, Subject, StudyPlan, ClassSchedule, SubjectSemester, Faculty
from apps.studyplan.form import SubjectSemesterForm


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('year', 'term', 'credit_limit')
    search_fields = ('year', 'term')


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'code', 'credits', 'university', 'get_offered_semesters', 'faculty')
    list_filter = ('university', 'offered_semesters', 'faculty')
    search_fields = ('title', 'code')

    def get_offered_semesters(self, obj):
        return ", ".join([f"{semester.term} {semester.year}" for semester in obj.offered_semesters.all()])
    get_offered_semesters.short_description = 'Offered Semesters'


class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'total_credits')
    list_filter = ('semester',)
    search_fields = ('student__user__username',)


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