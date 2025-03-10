import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BookStoreService {

  constructor(private client: HttpClient) { }

  getBooks() {
    return this.client.get('http://localhost:8000/bookStore/books/')
  }

  removeCategory(title: string, category: string, author: string) {
    const body = { title, category, author };
    return this.client.request('DELETE', 'http://localhost:8000/bookStore/books/remove_category/', { body });
  }

  addCategory(id_book: number, name_category: string){
    return this.client.post(`http://localhost:8000/bookStore/books/${id_book}/add_category/`, {
      name_category: name_category
    })
  }

  addBook(book: { title: string; author: { name: string }; categories: { name: string }[] }){
    return this.client.post(`http://localhost:8000/bookStore/books/`, book);
  }
}
