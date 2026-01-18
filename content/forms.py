from django import forms # pyright: ignore[reportMissingModuleSource]
from .models import ContentItem, Category

class ContentItemForm(forms.ModelForm):
    class Meta:
        model = ContentItem
        fields = ['title', 'url', 'description', 'content_type', 'category', 'status', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание контента...'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите теги через запятую',
                'data-role': 'tagsinput'
            }),
        }
        help_texts = {
            'tags': 'Введите теги через запятую (например: python, django, web)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Оптимизируем queryset для категорий
        self.fields['category'].queryset = Category.objects.all().order_by('name')