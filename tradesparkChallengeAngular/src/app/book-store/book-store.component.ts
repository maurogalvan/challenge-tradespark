import { Component, OnInit, ViewChild } from '@angular/core';
import { BookStoreService } from '../book-store.service';

@Component({
  selector: 'app-book-store',
  templateUrl: './book-store.component.html',
  styleUrls: ['./book-store.component.css']
})
export class BookStoreComponent implements OnInit {

  books: any[] = [];
  filteredBooks: any[] = [];
  isAddingCategory: { [key: number]: boolean } = {};

  isModalOpen: boolean = false;
  newBook = {
    title: '',
    author: '',
    categories: [] as string[]
  };
  
  newCategory: string = '';

  allCategories: any[] = [];
  filteredCategories: any[] = [];

  constructor(private bookStoreService: BookStoreService) { }

  ngOnInit(): void {
    this.bookStoreService.getBooks().subscribe((data: any[]) => {
      this.books = data;
      this.filteredBooks = data;
    });
    
    this.bookStoreService.getCategories().subscribe((categories: any[]) => {
      this.allCategories = categories;
    });
  }

  // Metodo para filtrar libros
  filterBooks(event: Event): void {
    const value = (event.target as HTMLInputElement).value.toLowerCase();
    if(!value) {
      this.filteredBooks = this.books;
    } else {
      this.filteredBooks = this.books.filter(book =>
        book.title.toLowerCase().includes(value) ||
        book.author.name.toLowerCase().includes(value) ||
        book.categories.some((category: any) => 
          category.name.toLowerCase().includes(value)
        )
      );
    }
  }

  // Metodo para eliminar el input del buscar
  clearFilter(): void {
    this.filteredBooks = this.books;
    const inputElement = document.getElementById('filterInput') as HTMLInputElement;
    inputElement.value = '';
  }

  // Metodo para pasar las categorias a un string separadas por comas
  categoriesToString(categories: any[]): string {
    let categoriesString = "";
    categories.forEach((category, index) => {
      categoriesString += category.name;
      if (index < categories.length - 1) {
        categoriesString += ", ";
      }
    });
    return categoriesString;
  }

  // Metodo para eliminar categoria de un libro
  deleteCategory(bookTitle: string, category: string, author: string) {
    const confirmDelete = window.confirm(`¿Estás seguro de que deseas borrar la categoría "${category}" del libro "${bookTitle}"?`);

    if (confirmDelete) {
      this.bookStoreService.removeCategory(bookTitle, category, author).subscribe(() => {
       
        this.bookStoreService.getBooks().subscribe((data: any[]) => {
          this.books = data;
          this.filteredBooks = data;
        });
      });
    }
  }

  filterCategories(event: Event): void {
    const value = (event.target as HTMLInputElement).value.toLowerCase();
    
    if (!value) {
      this.filteredCategories = this.allCategories; 
    } else {
      this.filteredCategories = this.allCategories.filter(category => 
        category.name.toLowerCase().includes(value)
      );
    }
    
  }

  // Metodo para agregar categoria a un libro
  addCategory(bookId: number, categoryName: string): void {
    if (categoryName.trim()) {
      // Verificar si la categoría ya está asociada al libro
      const book = this.books.find(b => b.id === bookId);
      const isCategoryAlreadyAdded = book?.categories.some(cat => cat.name.toLowerCase() === categoryName.toLowerCase());

      if (isCategoryAlreadyAdded) {
        alert('Esta categoría ya está asociada a este libro.');
        return;
      }

      // Llamar al servicio para agregar la categoría
      this.bookStoreService.addCategory(bookId, categoryName).subscribe(() => {
        // Actualizar la lista de libros después de agregar la categoría
        this.bookStoreService.getBooks().subscribe((data: any[]) => {
          this.books = data;
          this.filteredBooks = data;
        });
      });
    }
  }


  // Metodos para controlar el modal
  openModal() {
    this.isModalOpen = true;
  }
  closeModal() {
    this.isModalOpen = false;
  }


  // Metodo para agregar categorias a el libro nuevo
  addCategoryToNewBook(event: KeyboardEvent) {
    event.preventDefault(); // Evita que el formulario se envie al presionar Enter, ya que con esto agrego categorias
  
    // Comprobar si existe la categoria y si ya no la agrege antes
    if (this.newCategory.trim() && !this.newBook.categories.includes(this.newCategory.trim())) {
      this.newBook.categories.push(this.newCategory.trim());  
      this.newCategory = '';
    } else {
      alert('La categoría ya existe o esta vacio.');
    }
  }
  removeCategory(category: string): void {
    this.newBook.categories = this.newBook.categories.filter(c => c !== category);
  }
  

  addBook(): void {
    // Construir el objeto con la estructura esperada
    const bookData = {
      title: this.newBook.title,
      author: {
        name: this.newBook.author
      },
      categories: this.newBook.categories.map(category => ({ name: category })) 
    };
  
    // Hacer el post para agregar
    this.bookStoreService.addBook(bookData).subscribe(
      (response) => {
        console.log('Libro agregado exitosamente:', response);
        this.closeModal();
  
        // Recargar la lista de libros
        this.bookStoreService.getBooks().subscribe((data: any[]) => {
          this.books = data;
          this.filteredBooks = data; 
        });
      },
      (error) => {
        console.error('Error al agregar el libro:', error);
      }
    );
  }

  deleteBook(id_book: number): void {
    const confirmDelete = window.confirm(`¿Estás seguro de que deseas borrar el libro?`);
    if (confirmDelete) {
      this.bookStoreService.deleteBook(id_book).subscribe(() => {
       
        this.bookStoreService.getBooks().subscribe((data: any[]) => {
          this.books = data;
          this.filteredBooks = data;
        });
      });
    }
  }

  // Activa el modo de edición para el campo seleccionado
  editField(book: any, field: string): void {
    if (field === 'title') {
      book.isEditingTitle = true;
    } else if (field === 'author') {
      book.isEditingAuthor = true;
    }
  }

  // Guarda los cambios después de editar
  saveChanges(book: any, field: string): void {
    const updatedData = {};
    if (field === 'title') {
      updatedData['title'] = book.title;
      book.isEditingTitle = false;  // Sale del modo de edición
    } else if (field === 'author') {
      updatedData['author'] = book.author.name;
      book.isEditingAuthor = false;  // Sale del modo de edición
    }

    // Enviar el PATCH al backend
    this.bookStoreService.updateBook(book.id, updatedData).subscribe(
      (response) => {
        // Recargar la lista de libros
        this.bookStoreService.getBooks().subscribe((data: any[]) => {
          this.books = data;
          this.filteredBooks = data; 
        });
      }
    );
  }
}
