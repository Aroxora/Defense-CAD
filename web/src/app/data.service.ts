import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DoctrineData, EwStrategy, FactChecks, ProposedSystem } from './models';

@Injectable({ providedIn: 'root' })
export class DataService {
  private http = inject(HttpClient);
  private base = 'data';

  costBenefit(): Observable<{ systems: ProposedSystem[] }> {
    return this.http.get<{ systems: ProposedSystem[] }>(`${this.base}/cost_benefit.json`);
  }

  doctrine(): Observable<DoctrineData> {
    return this.http.get<DoctrineData>(`${this.base}/doctrine.json`);
  }

  ewStrategy(): Observable<EwStrategy> {
    return this.http.get<EwStrategy>(`${this.base}/ew_strategy.json`);
  }

  factChecks(): Observable<FactChecks> {
    return this.http.get<FactChecks>(`${this.base}/fact_checks.json`);
  }
}
