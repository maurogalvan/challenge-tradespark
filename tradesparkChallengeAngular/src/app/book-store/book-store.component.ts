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
  newBook = { title: '', author: '', category: '' };


  constructor(private bookStoreService: BookStoreService) { }

  ngOnInit(): void {
    this.bookStoreService.getBooks().subscribe((data: any[]) => {
      this.books = data;
      this.filteredBooks = data;
    });
  }

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

  clearFilter(): void {
    this.filteredBooks = this.books;
    const inputElement = document.getElementById('filterInput') as HTMLInputElement;
    inputElement.value = '';
  }

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

  deleteCategory(bookTitle: string, category: string, author: string) {
    const confirmDelete = window.confirm(`¿Estás seguro de que deseas borrar la categoría "${category}" del libro "${bookTitle}"?`);

    if (confirmDelete) {
      this.bookStoreService.removeCategory(bookTitle, category, author).subscribe(() => {
        console.log(`Categoría ${category} eliminada del libro ${bookTitle}`);
        this.bookStoreService.getBooks().subscribe((data: any[]) => {
          this.books = data;
          this.filteredBooks = data;
        });
      });
    }
  }

  addCategory(id_book: number, name_category: string) {
    if (!name_category) return;

    this.bookStoreService.addCategory(id_book, name_category).subscribe(() => {
      this.bookStoreService.getBooks().subscribe((data: any[]) => {
        this.books = data;
        this.filteredBooks = data;
      });
    });
  }

}
