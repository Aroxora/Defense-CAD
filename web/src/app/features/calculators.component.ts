import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { CALCULATORS, CALC_BY_ID, BLURBS } from '../calc-defs';
import { CalculatorComponent } from '../calculator.component';

@Component({
  selector: 'app-calculators',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, CalculatorComponent],
  template: `
    <div class="wrap">
      <section class="intro">
        <h2>Interactive physics calculators</h2>
        <p>
          Live, browser-side recomputation of the same equations used by the <code>osint_cad</code> models &mdash; each
          parity-checked against the Python source of truth in CI. Move the sliders to build intuition; every result shows
          its formula, a swept chart, and why it matters. For study/education &mdash; <b>not operational guidance</b>.
        </p>
      </section>

      <!-- hub: search/filter + grid -->
      <ng-container *ngIf="!selected()">
        <div class="filters">
          <label>Search
            <input type="text" [ngModel]="query()" (ngModelChange)="query.set($event)"
                   placeholder="radar, jamming, orbit, sonar…" aria-label="Search calculators" />
          </label>
          <label>Domain
            <select [ngModel]="cat()" (ngModelChange)="cat.set($event)">
              <option *ngFor="let g of categories()" [value]="g">{{ g }}</option>
            </select>
          </label>
          <span class="count">{{ filtered().length }} of {{ all.length }}</span>
        </div>
        <div class="calc-grid">
          <a class="calc-card" *ngFor="let c of filtered()" [routerLink]="['/calculators', c.id]">
            <span class="cat">{{ c.category }}</span>
            <h4>{{ c.title }}</h4>
            <p>{{ blurb(c.id) }}</p>
          </a>
        </div>
        <p class="note" *ngIf="!filtered().length">No calculators match “{{ query() }}”.</p>
      </ng-container>

      <!-- selected calculator with side nav -->
      <div class="calc-layout" *ngIf="selected() as sel">
        <nav class="calc-nav">
          <a routerLink="/calculators">← all calculators</a>
          <ng-container *ngFor="let g of grouped()">
            <div class="grp">{{ g.cat }}</div>
            <a *ngFor="let c of g.items" [routerLink]="['/calculators', c.id]" [class.active]="c.id === sel.id">{{ c.title }}</a>
          </ng-container>
        </nav>
        <app-calculator [def]="sel"></app-calculator>
      </div>
    </div>
  `,
})
export class CalculatorsComponent {
  private route = inject(ActivatedRoute);
  all = CALCULATORS;
  query = signal('');
  cat = signal('all');
  private id = toSignal(this.route.paramMap.pipe(map((p) => p.get('id'))), { initialValue: null });
  selected = computed(() => { const i = this.id(); return i ? CALC_BY_ID[i] ?? null : null; });
  blurb(id: string) { return BLURBS[id] ?? ''; }

  categories = computed(() => ['all', ...Array.from(new Set(this.all.map((c) => c.category)))]);
  filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    const k = this.cat();
    return this.all.filter((c) => {
      if (k !== 'all' && c.category !== k) return false;
      if (!q) return true;
      return (c.title + ' ' + c.category + ' ' + (BLURBS[c.id] ?? '')).toLowerCase().includes(q);
    });
  });

  grouped() {
    const cats = Array.from(new Set(this.all.map((c) => c.category)));
    return cats.map((cat) => ({ cat, items: this.all.filter((c) => c.category === cat) }));
  }
}
