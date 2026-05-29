import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { CadDerived, DoctrineData, EwStrategy, FactChecks, ProposedSystem } from './models';

@Injectable({ providedIn: 'root' })
export class DataService {
  private http = inject(HttpClient);
  private base = 'data';

  private fetch<T>(file: string, fallback: T): Observable<T> {
    return this.http.get<T>(`${this.base}/${file}`).pipe(
      catchError((e) => {
        console.error(`Failed to load ${file}:`, e);
        return of(fallback);
      }),
    );
  }

  costBenefit(): Observable<{ systems: ProposedSystem[] }> {
    return this.fetch('cost_benefit.json', { systems: [] });
  }

  doctrine(): Observable<DoctrineData> {
    return this.fetch<DoctrineData>('doctrine.json', { pla: null as never, dod: null as never });
  }

  ewStrategy(): Observable<EwStrategy> {
    return this.fetch<EwStrategy>('ew_strategy.json', null as never);
  }

  factChecks(): Observable<FactChecks> {
    return this.fetch<FactChecks>('fact_checks.json', { generated: 'unavailable', facts: [] });
  }

  cadDerived(): Observable<CadDerived> {
    return this.fetch<CadDerived>('cad_derived.json', {});
  }
}
