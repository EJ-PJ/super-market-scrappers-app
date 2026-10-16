import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Search } from './components/search/search';

@Component({
  imports: [RouterOutlet, Search],
  selector: 'app-root',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('supermarket-scrappers');
}
