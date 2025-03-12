import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BookStoreService {

  constructor(private client: HttpClient) { }

  // Get para obtener todos los libros
  getBooks() {
    return this.client.get('http://localhost:8000/bookStore/books/')
  }

  // Delete para elimininar la categoria asociada a un libro
  removeCategory(title: string, category: string, author: string) {
    const body = { title, category, author };
    return this.client.request('DELETE', 'http://localhost:8000/bookStore/books/remove_category/', { body });
  }

  // Get para obtener todas las categorias
  getCategories() {
    return this.client.get('http://localhost:8000/bookStore/categories/');
  }

  // Post para agregar una categoria asociada a un libro
  addCategory(id_book: number, name_category: string){
    return this.client.post(`http://localhost:8000/bookStore/books/${id_book}/add_category/`, {
      name_category: name_category
    })
  }

  // Post para agregar un libro
  addBook(book: { title: string; author: { name: string }; categories: { name: string }[] }) {
    return this.client.post('http://localhost:8000/bookStore/books/', book);
  }

  // Delete para eliminar un libro
  deleteBook(id_book: number){
    return this.client.request('DELETE', `http://localhost:8000/bookStore/books/${id_book}/`);
  }

  // Patch para modificar un dato de un libro
  updateBook(id_book: number, updatedData: any) {
    return this.client.patch(`http://localhost:8000/bookStore/books/${id_book}/`, updatedData);
  }

  // Patch para modificar un dato de un autor
  updateAuthor(id_author: number, updatedData: any) {
    return this.client.patch(`http://localhost:8000/bookStore/authors/${id_author}/`, updatedData);
  }

}
