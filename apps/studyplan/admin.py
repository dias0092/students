from django.contrib import admin
from apps.studyplan.models import Semester, University, Subject, StudyPlan, ClassSchedule


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('year', 'term', 'credit_limit')
    search_fields = ('year', 'term')


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'credits', 'get_university_name', 'get_offered_semesters')
    list_filter = ('university', 'offered_semesters')
    search_fields = ('title', 'code')

    def get_university_name(self, obj):
        return obj.university.name
    get_university_name.admin_order_field = 'university'
    get_university_name.short_description = 'University Name'

    def get_offered_semesters(self, obj):
        return ", ".join([f"{semester.term} {semester.year}" for semester in obj.offered_semesters.all()])
    get_offered_semesters.short_description = 'Offered Semesters'


class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('get_student_username', 'get_semester', 'total_credits')
    list_filter = ('semester',)
    search_fields = ('student__user__username',)

    def get_student_username(self, obj):
        return obj.student.user.username
    get_student_username.admin_order_field = 'student'
    get_student_username.short_description = 'Student Username'

    def get_semester(self, obj):
        return f"{obj.semester.term} {obj.semester.year}"
    get_semester.admin_order_field = 'semester'
    get_semester.short_description = 'Semester'


class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_student_username', 'get_semester', 'get_subject_title', 'day_of_week', 'time')
    list_filter = ('semester', 'day_of_week', 'subject')
    search_fields = ('student__user__username', 'subject__title')

    def get_student_username(self, obj):
        return obj.student.user.username
    get_student_username.admin_order_field = 'student'
    get_student_username.short_description = 'Student'

    def get_semester(self, obj):
        return f"{obj.semester.term} {obj.semester.year}"
    get_semester.admin_order_field = 'semester'
    get_semester.short_description = 'Semester'

    def get_subject_title(self, obj):
        return obj.subject.title
    get_subject_title.admin_order_field = 'subject'
    get_subject_title.short_description = 'Subject'


admin.site.register(Semester, SemesterAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(StudyPlan, StudyPlanAdmin)
admin.site.register(ClassSchedule, ClassScheduleAdmin)
