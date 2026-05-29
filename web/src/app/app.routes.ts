import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'portfolio', pathMatch: 'full' },
  {
    path: 'calculators',
    loadComponent: () => import('./features/calculators.component').then((m) => m.CalculatorsComponent),
  },
  {
    path: 'calculators/:id',
    loadComponent: () => import('./features/calculators.component').then((m) => m.CalculatorsComponent),
  },
  {
    path: 'portfolio',
    loadComponent: () => import('./features/portfolio.component').then((m) => m.PortfolioComponent),
  },
  {
    path: 'ew',
    loadComponent: () => import('./features/ew.component').then((m) => m.EwComponent),
  },
  {
    path: 'cad-derived',
    loadComponent: () => import('./features/cad-derived.component').then((m) => m.CadDerivedComponent),
  },
  {
    path: 'doctrine',
    loadComponent: () => import('./features/doctrine.component').then((m) => m.DoctrineComponent),
  },
  {
    path: 'methodology',
    loadComponent: () => import('./features/methodology.component').then((m) => m.MethodologyComponent),
  },
  { path: '**', redirectTo: 'portfolio' },
];
