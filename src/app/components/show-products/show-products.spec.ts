import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { ShowProducts } from './show-products';

describe('ShowProducts', () => {
  let component: ShowProducts;
  let fixture: ComponentFixture<ShowProducts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ShowProducts],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(ShowProducts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
