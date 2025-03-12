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
        """ [serializer] Chequeamos que funcione el crar libro """
        # Primero hacemos el post para crear el libro
        response = self.client.post(self.url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Vemos que el libro fue creado
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.first().title, 'Libro 1')
        print("[serializer] test_create_book OK")

    def test_create_duplicate_book(self):
        """ [serializer] Chequeamos que de error cuando ya exista un libro con el mismo titulo y autor """
        
        self.client.post(self.url, self.book_data, format='json')

        # Intentamos crear el mismo libro
        response = self.client.post(self.url, self.book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('El libro con este titulo y autor ya existe.', str(response.data))
        
        print("[serializer] test_create_duplicate_book OK")


# Test para probar los endpoints que se crearon en la views
class BookCategoryTest(APITestCase):
    def setUp(self):
        # Creamos los autores
        self.author1 = Author.objects.create(name="Mauro", bio="bio", date_of_birth="1998-09-28")
        self.author2 = Author.objects.create(name="Juan", bio="bio", date_of_birth="1990-06-15")

        # Creamos las categorias
        self.category1 = Category.objects.create(name="Categoria 1", description="Descripcion 1")
        self.category2 = Category.objects.create(name="Categoria 2", description="Descripcion 2")
        self.category3 = Category.objects.create(name="Categoria 3", description="Descripcion 3")

        # Creamos los libros
        self.book1 = Book.objects.create(title="Libro 1", author=self.author1)
        self.book2 = Book.objects.create(title="Libro 1", author=self.author2)
        self.book3 = Book.objects.create(title="Libro 2", author=self.author1)

        # Asocio las categorias a los libros
        self.book1.categories.add(self.category1, self.category2)
        self.book2.categories.add(self.category1)
        self.book3.categories.add(self.category3)

        self.url_remove_category = reverse('book-remove_category')
        self.url_add_category = lambda book_id: reverse('book-add_category', kwargs={'pk': book_id})

    def test_remove_category_success(self):
        """ [remove_category] Elimina una categoria de un libro, en este caso especificamos el author"""
        data = {"title": "Libro 1", "category": "Categoria 1", "author": "Mauro"}
        response = self.client.delete(self.url_remove_category, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertNotIn(self.category1, self.book1.categories.all())
        print("[remove_category] test_remove_category_success OK")

    def test_missing_title_or_category(self):
        """ [remove_category] No se envia el titulo o la categoria para que falle"""
        data = {"title": "Libro 1"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"category": "Categoria 1"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[remove_category] test_missing_title_or_category OK")

    def test_book_not_found(self):
        """ [remove_category] Probamos con un libro que no existe """
        data = {"title": "Desconocido", "category": "Categoria 1"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[remove_category] test_book_not_found OK")

    def test_multiple_books_without_author(self):
        """ [remove_category] Probamos un libro con el mismo titulo, y que no se especifica el autor """
        data = {"title": "Libro 1", "category": "Categoria 1"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_300_MULTIPLE_CHOICES)
        print("[remove_category] test_multiple_books_without_author OK")

    def test_book_with_author_not_found(self):
        """ [remove_category] Probamos especifica un autor, pero no coincide con ningún libro """
        data = {"title": "Libro 1", "category": "Categoria 1", "author": "Desconocido"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("[remove_category] test_book_with_author_not_found OK")

    def test_category_not_found(self):
        """ [remove_category] Probamos con una categoria que no existe """
        data = {"title": "Libro 1", "category": "Inexistente", "author": "Mauro"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[remove_category] test_category_not_found OK")

    def test_category_not_associated_with_book(self):
        """ [remove_category] Probamos con una categoria que no esta asociada al libro """
        data = {"title": "Libro 1", "category": "Categoria 3", "author": "Mauro"}
        response = self.client.delete(self.url_remove_category, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[remove_category] test_category_not_associated_with_book OK")






    def test_add_existing_category_to_book(self):
        """ [add_category] Agregamos una categoria que ya existe en un libro"""
        data = {"name_category": "Categoria 3"}

        response = self.client.post(self.url_add_category(self.book1.id), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ya existia y fue asociada", response.data["detail"])
        self.book1.refresh_from_db()
        self.assertIn(self.category3, self.book1.categories.all())
        print("[add_category] test_add_existing_category_to_book OK")

    def test_create_new_category_and_associate_to_book(self):
        """ [add_category] Creamos una nueva categoria y la asociamos a un libro"""
        data = {"name_category": "Categoria nueva"}

        response = self.client.post(self.url_add_category(self.book2.id), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("fue creada y asociada", response.data["detail"])
        self.book2.refresh_from_db()
        self.assertTrue(Category.objects.filter(name="Categoria nueva").exists())
        self.assertIn(Category.objects.get(name="Categoria nueva"), self.book2.categories.all())
        print("[add_category] test_create_new_category_and_associate_to_book OK")

    def test_add_already_associated_category(self):
        """ [add_category] Intentamos agregar una categoria que ya esta en el libro """
        data = {"name_category": "Categoria 1"}

        response = self.client.post(self.url_add_category(self.book1.id), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ya esta asociada al libro", response.data["detail"])
        print("[add_category] test_add_already_associated_category OK")

    def test_add_category_without_name(self):
        """ [add_category] Intentamos agregar una categoria sin nada"""
        data = {}

        response = self.client.post(self.url_add_category(self.book3.id), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Se requiere el nombre de la categoria", response.data["error"])
        print(" [add_category] test_add_category_without_name OK")
