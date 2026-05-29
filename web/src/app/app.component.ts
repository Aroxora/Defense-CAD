import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from './data.service';
import { DoctrineData, EwStrategy, ProposedSystem } from './models';

type Tab = 'portfolio' | 'ew' | 'doctrine';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent implements OnInit {
  private data = inject(DataService);

  tab = signal<Tab>('portfolio');
  systems = signal<ProposedSystem[]>([]);
  doctrine = signal<DoctrineData | null>(null);
  ew = signal<EwStrategy | null>(null);

  sideFilter = signal<string>('all');
  domainFilter = signal<string>('all');
  selectedKey = signal<string | null>(null);

  sides = computed(() => ['all', ...Array.from(new Set(this.systems().map((s) => s.side)))]);
  domains = computed(() => ['all', ...Array.from(new Set(this.systems().map((s) => s.domain))).sort()]);

  filtered = computed(() => {
    const sf = this.sideFilter();
    const df = this.domainFilter();
    return this.systems()
      .filter((s) => (sf === 'all' || s.side === sf) && (df === 'all' || s.domain === df))
      .slice()
      .sort((a, b) => b.value_index - a.value_index);
  });

  selected = computed(() => this.systems().find((s) => s.key === this.selectedKey()) ?? null);
  maxValue = computed(() => Math.max(0.01, ...this.systems().map((s) => s.value_index)));

  ngOnInit(): void {
    this.data.costBenefit().subscribe((d) => {
      this.systems.set(d.systems);
      if (d.systems.length) {
        this.selectedKey.set(
          d.systems.find((s) => s.key === 'trump_class_battleship')?.key ?? d.systems[0].key,
        );
      }
    });
    this.data.doctrine().subscribe((d) => this.doctrine.set(d));
    this.data.ewStrategy().subscribe((d) => this.ew.set(d));
  }

  setTab(t: Tab) {
    this.tab.set(t);
  }

  // Live recompute of one system's economics when sliders move (same formula as the Python).
  recompute(s: ProposedSystem) {
    const lcc =
      (s.rnd_cost_musd + s.unit_cost_musd * s.quantity + s.annual_oandm_musd * s.quantity * s.service_life_years) /
      1000;
    s.lifecycle_cost_busd = Math.round(lcc * 100) / 100;
    s.benefit_per_billion = lcc > 0 ? Math.round((s.benefit_score / lcc) * 1000) / 1000 : 0;
    s.value_index = lcc > 0 ? Math.round(((s.benefit_score * s.survivability_score) / 100 / lcc) * 1000) / 1000 : 0;
    // propagate the (fixed) relative uncertainty through the new value to update the CI
    const rel = s.uncertainty * Math.sqrt(3);
    s.value_ci_low = Math.round(Math.max(0, s.value_index * (1 - rel)) * 1000) / 1000;
    s.value_ci_high = Math.round(s.value_index * (1 + rel) * 1000) / 1000;
    this.systems.set([...this.systems()]);
  }

  pct(v: number): number {
    return Math.min(100, (v / this.maxValue()) * 100);
  }

  barWidth(v: number): string {
    return `${this.pct(v)}%`;
  }

  doctrineSides() {
    const d = this.doctrine();
    return d ? [d.pla, d.dod] : [];
  }
}
