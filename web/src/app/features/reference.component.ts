import { Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CALCULATORS } from '../calc-defs';
import { GLOSSARY } from '../glossary';

/** Auto-generated reference: every calculator's equation, parameters and units (pulled from
 *  calc-defs, the source of truth — no hand-copied numbers), plus a curated glossary. */
@Component({
  selector: 'app-reference',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="wrap">
      <section class="intro">
        <h2>Reference &mdash; equations, parameters &amp; glossary</h2>
        <p>
          A single index of every calculator: its formula, inputs and outputs with units, generated directly from the
          models so it can never drift. {{ all.length }} calculators across {{ domains().length }} domains. Conceptual
          OSINT for education/study &mdash; <b>not operational guidance</b>.
        </p>
        <div class="filters">
          <label>Search
            <input type="text" [ngModel]="q()" (ngModelChange)="q.set($event)"
                   placeholder="symbol, term, equation…" aria-label="Search reference" />
          </label>
          <span class="count">{{ filtered().length }} of {{ all.length }}</span>
        </div>
      </section>

      <section class="card" *ngFor="let c of filtered()">
        <div class="chead">
          <h3><a [routerLink]="['/calculators', c.id]">{{ c.title }}</a></h3>
          <span class="cat">{{ c.category }}</span>
        </div>
        <pre class="formula">{{ c.equation }}</pre>
        <div class="reftab">
          <div>
            <h4>Inputs</h4>
            <ul>
              <li *ngFor="let i of c.inputs"><b>{{ i.label }}</b> <em>[{{ i.unit }}]</em></li>
            </ul>
          </div>
          <div>
            <h4>Outputs</h4>
            <ul>
              <li *ngFor="let o of c.compute(defaults(c))"><b>{{ o.label }}</b> <em>[{{ o.unit || '—' }}]</em></li>
            </ul>
          </div>
        </div>
        <p class="src">Source: <code>{{ c.source }}</code></p>
      </section>

      <section class="intro" style="margin-top: 28px">
        <h2>Glossary</h2>
      </section>
      <div class="cols">
        <section class="card" *ngFor="let g of glossary()">
          <div class="chead"><h3>{{ g.term }}</h3><span class="cat">{{ g.unit }}</span></div>
          <p>{{ g.def }}</p>
        </section>
      </div>
    </div>
  `,
})
export class ReferenceComponent {
  all = CALCULATORS;
  q = signal('');
  domains = computed(() => Array.from(new Set(this.all.map((c) => c.category))));

  defaults(c: (typeof CALCULATORS)[number]): Record<string, number> {
    const v: Record<string, number> = {};
    for (const i of c.inputs) v[i.key] = i.default;
    return v;
  }

  filtered = computed(() => {
    const s = this.q().trim().toLowerCase();
    if (!s) return this.all;
    return this.all.filter((c) =>
      (c.title + ' ' + c.category + ' ' + c.equation + ' ' +
        c.inputs.map((i) => i.label + ' ' + i.unit).join(' ')).toLowerCase().includes(s));
  });

  glossary = computed(() => {
    const s = this.q().trim().toLowerCase();
    if (!s) return GLOSSARY;
    return GLOSSARY.filter((g) => (g.term + ' ' + g.def + ' ' + g.unit).toLowerCase().includes(s));
  });
}
