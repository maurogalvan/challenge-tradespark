from rest_framework import serializers
from .models import Author, Category, Book

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'categories']

    def create(self, validated_data):
        
        author_data = validated_data.pop('author')
        categories_data = validated_data.pop('categories')
        if not Author.objects.filter(**author_data).exists():
            Author.objects.create(**author_data)
        author = Author.objects.get(**author_data)

        # Se agrego esto para controlar que no haya libros con el autor iguales
        if Book.objects.filter(title=validated_data['title'], author=author).exists():
            raise serializers.ValidationError("El libro con este titulo y autor ya existe.")
        
        book = Book.objects.create(author=author, **validated_data)
        for category_data in categories_data:
            if not Category.objects.filter(**category_data).exists():
                Category.objects.create(**category_data)
            category = Category.objects.get(**category_data)
            book.categories.add(category)
        return book