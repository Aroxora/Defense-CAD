import { Component, Input, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ChartPoint { x: number; y: number; }

/** Dependency-free responsive SVG line chart with an optional highlighted marker. */
@Component({
  selector: 'app-chart',
  standalone: true,
  imports: [CommonModule],
  template: `
    <svg [attr.viewBox]="'0 0 ' + W + ' ' + H" preserveAspectRatio="xMidYMid meet" class="chart"
         role="img" [attr.aria-label]="yLabel + ' versus ' + xLabel">
      <title>{{ yLabel }} versus {{ xLabel }}</title>
      <!-- axes -->
      <line [attr.x1]="padL" [attr.y1]="padT" [attr.x2]="padL" [attr.y2]="H - padB" class="axis" aria-hidden="true" />
      <line [attr.x1]="padL" [attr.y1]="H - padB" [attr.x2]="W - padR" [attr.y2]="H - padB" class="axis" aria-hidden="true" />
      <!-- gridlines + y labels -->
      <g *ngFor="let t of yTicks()" aria-hidden="true">
        <line [attr.x1]="padL" [attr.y1]="t.py" [attr.x2]="W - padR" [attr.y2]="t.py" class="grid" />
        <text [attr.x]="padL - 6" [attr.y]="t.py + 3" class="tick" text-anchor="end">{{ t.label }}</text>
      </g>
      <g *ngFor="let t of xTicks()">
        <text [attr.x]="t.px" [attr.y]="H - padB + 16" class="tick" text-anchor="middle">{{ t.label }}</text>
      </g>
      <!-- curve -->
      <polyline [attr.points]="polyline()" class="curve" />
      <!-- current marker -->
      <circle *ngIf="marker() as m" [attr.cx]="m.px" [attr.cy]="m.py" r="4" class="marker" />
      <line *ngIf="marker() as m" [attr.x1]="m.px" [attr.y1]="padT" [attr.x2]="m.px" [attr.y2]="H - padB" class="markerline" />
      <!-- axis labels -->
      <text [attr.x]="(padL + W - padR) / 2" [attr.y]="H - 4" class="axlabel" text-anchor="middle">{{ xLabel }}</text>
      <text [attr.x]="12" [attr.y]="(padT + H - padB) / 2" class="axlabel"
            [attr.transform]="'rotate(-90 12 ' + (padT + H - padB) / 2 + ')'" text-anchor="middle">{{ yLabel }}</text>
    </svg>
  `,
  styles: [`
    .chart { width: 100%; height: auto; display: block; }
    .axis { stroke: #2b3a52; stroke-width: 1; }
    .grid { stroke: #18222f; stroke-width: 1; }
    .curve { fill: none; stroke: #46e0c0; stroke-width: 2; }
    .marker { fill: #4aa3ff; }
    .markerline { stroke: #4aa3ff; stroke-width: 1; stroke-dasharray: 3 3; opacity: .5; }
    .tick { fill: #7e8ca3; font-size: 10px; }
    .axlabel { fill: #9fb0c8; font-size: 11px; }
  `],
})
export class ChartComponent {
  W = 560; H = 300; padL = 56; padR = 16; padT = 14; padB = 34;

  private _points = signal<ChartPoint[]>([]);
  private _cur = signal<ChartPoint | null>(null);
  @Input() xLabel = '';
  @Input() yLabel = '';
  @Input() logX = false;
  @Input() set points(p: ChartPoint[]) { this._points.set(p ?? []); }
  @Input() set current(c: ChartPoint | null) { this._cur.set(c); }

  private xs = computed(() => this._points().map((p) => (this.logX ? Math.log10(Math.max(p.x, 1e-9)) : p.x)));
  private ys = computed(() => this._points().map((p) => p.y));
  private xMin = computed(() => { const a = this.xs(); return a.length ? Math.min(...a) : 0; });
  private xMax = computed(() => { const a = this.xs(); return a.length ? Math.max(...a) : 1; });
  // Fit the y-domain to the real data extent with ~6% headroom (do NOT clamp to 0,
  // which squished all-negative curves like aspect-RCS in dBsm).
  private yMin = computed(() => {
    const a = this.ys(); if (!a.length) return 0;
    const lo = Math.min(...a), hi = Math.max(...a), pad = (hi - lo) * 0.06 || Math.abs(lo) * 0.06 || 1;
    return lo - pad;
  });
  private yMax = computed(() => {
    const a = this.ys(); if (!a.length) return 1;
    const lo = Math.min(...a), hi = Math.max(...a), pad = (hi - lo) * 0.06 || Math.abs(hi) * 0.06 || 1;
    return hi + pad;
  });

  private sx(xv: number): number {
    const lo = this.xMin(), hi = this.xMax();
    const t = hi > lo ? (xv - lo) / (hi - lo) : 0.5;
    return this.padL + t * (this.W - this.padL - this.padR);
  }
  private sy(yv: number): number {
    const lo = this.yMin(), hi = this.yMax();
    const t = hi > lo ? (yv - lo) / (hi - lo) : 0;
    return this.H - this.padB - t * (this.H - this.padT - this.padB);
  }

  polyline = computed(() =>
    this._points().map((p) => `${this.sx(this.logX ? Math.log10(Math.max(p.x, 1e-9)) : p.x)},${this.sy(p.y)}`).join(' '));

  marker = computed(() => {
    const c = this._cur();
    if (!c) return null;
    return { px: this.sx(this.logX ? Math.log10(Math.max(c.x, 1e-9)) : c.x), py: this.sy(c.y) };
  });

  yTicks = computed(() => {
    const lo = this.yMin(), hi = this.yMax();
    return [0, 0.25, 0.5, 0.75, 1].map((f) => {
      const v = lo + f * (hi - lo);
      return { py: this.sy(v), label: fmt(v) };
    });
  });

  xTicks = computed(() => {
    const lo = this.xMin(), hi = this.xMax();
    return [0, 0.5, 1].map((f) => {
      const xv = lo + f * (hi - lo);
      return { px: this.sx(xv), label: fmt(this.logX ? 10 ** xv : xv) };
    });
  });
}

function fmt(v: number): string {
  const a = Math.abs(v);
  if (a !== 0 && (a < 0.01 || a >= 100000)) return v.toExponential(1);
  if (a >= 100) return v.toFixed(0);
  if (a >= 1) return v.toFixed(1);
  return v.toFixed(3);
}
