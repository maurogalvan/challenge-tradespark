from sqlite3 import IntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Author, Category, Book
from .serializers import AuthorSerializer, CategorySerializer, BookSerializer

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    # Asociar una categoria a un libro
    @action(detail=True, methods=['POST'], url_path='add_category', url_name='add_category')
    def add_category(self, request, pk=None):
        # Se obtiene el id del book de la url, y el nombre de la categoria por json
        book = self.get_object()
        name_category = request.data.get("name_category")

        # Chequeamos que exista la catetgoria
        if not name_category:
            return  Response({"error": "Se requiere el nombre de la categoria"}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            # Si existe la categoria la usamos, si no existe la creamos
            category, created = Category.objects.get_or_create(name=name_category)
        except IntegrityError:
            return Response({"error": "Error de integridad en la base de datos."}, status=status.HTTP_400_BAD_REQUEST)

        # Chequeamos que ya no este asociada al libro
        if category in book.categories.all():
            return Response({"detail": f"La categoria '{name_category}' ya esta asociada al libro"}, status= status.HTTP_200_OK)
        try:
            # Asociamos la categoria al libro
            book.categories.add(category)

            message = f"La categoria '{name_category}' fue creada y asociada al libro." if created else f"La categoria '{name_category}' ya existia y fue asociada al libro."
            return Response({"detail": message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Eliminar categoria asociada a un libro
    @action(detail=False, methods=['DELETE'], url_path='remove_category', url_name='remove_category')
    def remove_category(self, request):

        # Recibimos estos datos mediante un JSON
        title_book = request.data.get('title')
        name_category = request.data.get('category')
        author_book = request.data.get('author') # Opcional

        # Controlamos que por lo menos el titulo y la categoria esten
        if not title_book or not name_category:
            return Response({"error": "Se requiere el titulo y la categoria"}, status = status.HTTP_400_BAD_REQUEST)

        # Buscamos el libro por su nombre
        books = Book.objects.filter(title = title_book)

        # Si el libro no existe arrojamos un error
        if not books.exists():
            return Response({"detail": f"El libro '{title_book}' no existe"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Si hay mas libros con el mismo nombre arrojamos error y mostramos los libros con el mismo titulo
        # ademas pedimos que especifique el author para saber exactamente el libro
        if books.count()>1 and not author_book:
            book_list =  [{"id": book.id, "title": book.title, "author": book.author.name} for book in books]
            return Response({ "detail": f"Se encontro mas de un libro con el titulo '{title_book}'. Por favor especifica el autor.", "books": book_list }, status=status.HTTP_300_MULTIPLE_CHOICES)
        
        # Si tenemos el author quiere decir que hay libros con el mismo nombre, entonces por esos libros filtramos tambien el author 
        if author_book:
            books = books.filter(author__name=author_book)

            if not books.exists():
                return Response({ "detail": f"No existe el libro '{title_book}' con el autor '{author_book}'." }, status=status.HTTP_404_NOT_FOUND)
        
        # En esta instancia ya queda un solo libro
        book = books.first()

        try:
            # Nos traemos la categoria por el nombre
            category = Category.objects.get(name=name_category)
        except Category.DoesNotExist:
            return Response({"detail": f"Categoria '{name_category}' no existe"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Controlamos que la categoria este asociada con el libro
        if category not in book.categories.all():
            return Response({"detail": f"La categoria '{name_category}' no esta asociado a ese libro."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Eliminamos la categoria asociada al libro
            book.categories.remove(category)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": f"La categoria '{name_category}' del libro '{title_book}' fue eliminada"}, status=status.HTTP_200_OK)