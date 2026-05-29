import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../data.service';
import { ProposedSystem } from '../models';

@Component({
  selector: 'app-portfolio',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './portfolio.component.html',
})
export class PortfolioComponent implements OnInit {
  private data = inject(DataService);
  systems = signal<ProposedSystem[]>([]);
  sideFilter = signal('all');
  domainFilter = signal('all');
  selectedKey = signal<string | null>(null);

  sides = computed(() => ['all', ...Array.from(new Set(this.systems().map((s) => s.side)))]);
  domains = computed(() => ['all', ...Array.from(new Set(this.systems().map((s) => s.domain))).sort()]);
  filtered = computed(() => {
    const sf = this.sideFilter(), df = this.domainFilter();
    return this.systems().filter((s) => (sf === 'all' || s.side === sf) && (df === 'all' || s.domain === df))
      .slice().sort((a, b) => b.value_index - a.value_index);
  });
  selected = computed(() => this.systems().find((s) => s.key === this.selectedKey()) ?? null);
  maxValue = computed(() => Math.max(0.01, ...this.systems().map((s) => s.value_index)));

  ngOnInit() {
    this.data.costBenefit().subscribe((d) => {
      this.systems.set(d.systems);
      if (d.systems.length) this.selectedKey.set(d.systems.find((s) => s.key === 'trump_class_battleship')?.key ?? d.systems[0].key);
    });
  }

  setField(s: ProposedSystem, key: keyof ProposedSystem, value: unknown) {
    (s as unknown as Record<string, number>)[key as string] = Number(value); // coerce to number
    this.recompute(s);
  }

  recompute(s: ProposedSystem) {
    const lcc = (s.rnd_cost_musd + s.unit_cost_musd * s.quantity + s.annual_oandm_musd * s.quantity * s.service_life_years) / 1000;
    s.lifecycle_cost_busd = Math.round(lcc * 100) / 100;
    s.value_index = lcc > 0 ? Math.round(((s.benefit_score * s.survivability_score) / 100 / lcc) * 1000) / 1000 : 0;
    const rel = s.uncertainty * Math.sqrt(3);
    s.value_ci_low = Math.round(Math.max(0, s.value_index * (1 - rel)) * 1000) / 1000;
    s.value_ci_high = Math.round(s.value_index * (1 + rel) * 1000) / 1000;
    this.systems.set([...this.systems()]);
  }
  pct(v: number) { return Math.min(100, (v / this.maxValue()) * 100); }
  barWidth(v: number) { return `${this.pct(v)}%`; }
}
