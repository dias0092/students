from django import forms
from apps.studyplan.models import Subject, SubjectSemester

class SubjectSemesterForm(forms.ModelForm):
    class Meta:
        model = SubjectSemester
        fields = ['subject', 'semester', 'day_of_week', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.select_related('university').all()
        self.fields['subject'].label_from_instance = self.label_from_instance

    def label_from_instance(self, obj):
        return f"{obj.title} ({obj.university.name})"