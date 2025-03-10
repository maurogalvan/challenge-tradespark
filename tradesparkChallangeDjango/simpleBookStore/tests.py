from rest_framework.test import APITestCase
from rest_framework import status
from simpleBookStore.models import Book, Category, Author
from django.urls import reverse

# Vamos a testear el cambio en el serializer, lo que agregamos fue que al intentar agregar el mismo libro o sea mismo titulo con el mismo author, 
# este sea rechazado desde el serializer
class BookSerializerTest(APITestCase):
    def setUp(self):
        # Creamos el author
        self.author_data = {
            'name': 'Mauro',
            'bio': 'bio',
            'date_of_birth': '1998-09-28',
        }
        self.author = Author.objects.create(**self.author_data)
        
        # Creamos dos categorias
        self.category1 = Category.objects.create(name='Categoria 1', description='Descripcion 1')
        self.category2 = Category.objects.create(name='Categoria 2', description='Descripcion 2')

        # Ahora creamos el libro como tal
        self.book_data = {
            'title': 'Libro 1',
            'author': {'name': self.author.name}, 
            'categories': [{'name': self.category1.name}, {'name': self.category2.name}],
        }
        
        self.url = reverse('book-list')

    def test_create_book(self):
        # Primero hacemos el post para crear el libro
        response = self.client.post(self.url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Vemos que el libro fue creado
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.first().title, 'Libro 1')
        print("test_create_book OK")

    def test_create_duplicate_book(self):
        # Creamos el libro
        self.client.post(self.url, self.book_data, format='json')

        # Intentamos crear el mismo libro
        response = self.client.post(self.url, self.book_data, format='json')

        # Vemos que da error, y el error esperado
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('El libro con este título y autor ya existe.', str(response.data))
        
        print("test_create_duplicate_book OK")