import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { CALCULATORS, CALC_BY_ID, BLURBS } from '../calc-defs';
import { CalculatorComponent } from '../calculator.component';

@Component({
  selector: 'app-calculators',
  standalone: true,
  imports: [CommonModule, RouterLink, CalculatorComponent],
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

      <!-- hub grid -->
      <div class="calc-grid" *ngIf="!selected()">
        <a class="calc-card" *ngFor="let c of all" [routerLink]="['/calculators', c.id]">
          <span class="cat">{{ c.category }}</span>
          <h4>{{ c.title }}</h4>
          <p>{{ blurb(c.id) }}</p>
        </a>
      </div>

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
  private id = toSignal(this.route.paramMap.pipe(map((p) => p.get('id'))), { initialValue: null });
  selected = computed(() => { const i = this.id(); return i ? CALC_BY_ID[i] ?? null : null; });
  blurb(id: string) { return BLURBS[id] ?? ''; }

  grouped() {
    const cats = Array.from(new Set(this.all.map((c) => c.category)));
    return cats.map((cat) => ({ cat, items: this.all.filter((c) => c.category === cat) }));
  }
}
