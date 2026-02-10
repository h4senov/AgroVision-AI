from django import forms
from .models import Product, Tag, Category
from django.utils.text import slugify




class ProductForm(forms.ModelForm):
    # Tag-ları daha rahat seçmək üçün checkbox istifadə edə bilərik (istəyə bağlı)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Teqlər"
    )

    class Meta:
        model = Product
        # Hansı sahələrin formda görünməsini istəyirsən?
        fields = [
            'name', 'slug', 'category', 'short_description', 
            'description', 'price', 'stock', 'is_published', 
            'is_featured', 'tags'
        ]
        
        # Hər bir sahə üçün Bootstrap class-ları və etiketlər (Labels)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Məhsulun adı'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'link-uchun-ad'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Qısa xülasə...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Geniş məlumat...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'name': 'Məhsul Adı',
            'slug': 'URL Linki',
            'category': 'Kateqoriya',
            'short_description': 'Qısa Təsvir',
            'description': 'Geniş Məzmun',
            'price': 'Qiymət (₼)',
            'stock': 'Anbar Sayı',
            'is_published': 'Dərc edilsin?',
            'is_featured': 'Ön plana çıxsın?',
        }
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock mənfi ola bilməz!")
        return stock

    def clean_price(self):
        """Qiymətin mənfi olmamasını yoxlayan sadə bir validator"""
        price = self.cleaned_data.get('price')
        
        if price is not None and price < 0:
            raise forms.ValidationError("Qiymət mənfi ola bilməz!")
        return price
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price")

        if price == "":
            cleaned_data["price"] = None

        return cleaned_data
    
    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")

        if not slug and name:
            slug = slugify(name)

        return slug
    
    def clean_name(self):
        name = self.cleaned_data["name"]

        if Product.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu adda məhsul artıq var!")

        return name



 