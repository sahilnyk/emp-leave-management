from django import forms
from .models import LeaveRequest
from datetime import date

class LeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for leave'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['leave_type'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')

        if start and end:
            if start > end:
                raise forms.ValidationError("Start date must be before or equal to end date.")
            if start < date.today():
                raise forms.ValidationError("Start date cannot be in the past.")
        return cleaned
