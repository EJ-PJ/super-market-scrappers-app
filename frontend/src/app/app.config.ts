import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, withHashLocation } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // hash urls (#/products?q=leche): the desktop app loads index.html from file://,
    // where urls like /products don't exist
    provideRouter(routes, withHashLocation()),
    provideHttpClient(),
  ]
};
