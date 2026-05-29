import { Component, Input, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CalcDef, CalcInput } from './calc-defs';
import { ChartComponent, ChartPoint } from './chart.component';

@Component({
  selector: 'app-calculator',
  standalone: true,
  imports: [CommonModule, FormsModule, ChartComponent],
  templateUrl: './calculator.component.html',
  styleUrl: './calculator.component.scss',
})
export class CalculatorComponent {
  private _def = signal<CalcDef | null>(null);
  values = signal<Record<string, number>>({});

  @Input() set def(d: CalcDef) {
    this._def.set(d);
    const v: Record<string, number> = {};
    for (const inp of d.inputs) v[inp.key] = inp.default;
    this.values.set(v);
  }
  get def() { return this._def()!; }

  outputs = computed(() => {
    const d = this._def();
    return d ? d.compute(this.values()) : [];
  });

  chartPoints = computed<ChartPoint[]>(() => {
    const d = this._def();
    if (!d) return [];
    const inp = d.inputs.find((i) => i.key === d.chart.xKey);
    if (!inp) return [];
    const v = this.values();
    const N = 64;
    const pts: ChartPoint[] = [];
    for (let i = 0; i <= N; i++) {
      const t = i / N;
      const x = inp.log
        ? 10 ** (Math.log10(inp.min) + t * (Math.log10(inp.max) - Math.log10(inp.min)))
        : inp.min + t * (inp.max - inp.min);
      const y = d.chart.y(x, v);
      if (Number.isFinite(y)) pts.push({ x, y });
    }
    return pts;
  });

  current = computed<ChartPoint | null>(() => {
    const d = this._def();
    if (!d) return null;
    const x = this.values()[d.chart.xKey];
    const y = d.chart.y(x, this.values());
    return Number.isFinite(y) ? { x, y } : null;
  });

  chartLogX = computed(() => {
    const d = this._def();
    const inp = d?.inputs.find((i) => i.key === d.chart.xKey);
    return !!inp?.log;
  });

  xAxisLabel = computed(() => {
    const d = this._def();
    const inp = d?.inputs.find((i) => i.key === d.chart.xKey);
    return inp ? `${inp.label}${inp.unit && inp.unit !== '-' ? ' (' + inp.unit + ')' : ''}` : '';
  });

  setVal(key: string, value: number) {
    this.values.set({ ...this.values(), [key]: +value });
  }

  fmtVal(inp: CalcInput, v: number): string {
    if (inp.log || Math.abs(v) < 0.01) return v < 1 ? v.toPrecision(2) : v.toFixed(2);
    return v >= 100 ? v.toFixed(0) : v.toFixed(2);
  }

  fmtOut(o: { value: number | null; fmt?: string }): string {
    if (o.value === null || !Number.isFinite(o.value)) return '—';
    const v = o.value;
    if (o.fmt === 'pct') return (v * 100).toFixed(1) + '%';
    const a = Math.abs(v);
    if (a !== 0 && (a < 0.01 || a >= 100000)) return v.toExponential(2);
    if (a >= 100) return v.toFixed(0);
    if (a >= 1) return v.toFixed(2);
    return v.toFixed(3);
  }
}
