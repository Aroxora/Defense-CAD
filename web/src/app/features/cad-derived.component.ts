import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../data.service';
import { CadDerived } from '../models';
import { ChartComponent, ChartPoint } from '../chart.component';

@Component({
  selector: 'app-cad-derived',
  standalone: true,
  imports: [CommonModule, FormsModule, ChartComponent],
  template: `
    <div class="wrap">
      <section class="intro">
        <h2>Derived from CAD geometry</h2>
        <p>
          These results are computed directly from the parametric CAD meshes using the Physical-Optics RCS calculator
          (<code>osint_cad/analysis/cad_derived.py</code>): the radar cross section over a full azimuth sweep, the resulting
          aspect-dependent detection-range envelope, and mesh geometric properties. PO RCS is valid for size ≫ wavelength;
          conceptual OSINT for study — <b>not operational guidance</b>.
        </p>
        <div class="filters" *ngIf="models().length">
          <label>Model
            <select [ngModel]="model()" (ngModelChange)="model.set($event)">
              <option *ngFor="let m of models()" [value]="m">{{ m }}</option>
            </select>
          </label>
        </div>
      </section>

      <div class="cols" *ngIf="current() as c">
        <section class="card">
          <h3>RCS vs azimuth — {{ c.rcs_profile.frequency_ghz }} GHz</h3>
          <app-chart [points]="rcsPoints()" xLabel="Azimuth (deg)" yLabel="RCS (dBsm)"></app-chart>
          <p class="note">min {{ c.rcs_profile.min_dbsm }} · mean {{ c.rcs_profile.mean_dbsm }} ·
            median {{ c.rcs_profile.median_dbsm }} · max {{ c.rcs_profile.max_dbsm }} dBsm
            (dynamic range {{ c.rcs_profile.dynamic_range_db }} dB over {{ c.rcs_profile.num_triangles }} facets).
            Low head-on, high on the beam — the shaping signature.</p>
        </section>

        <section class="card">
          <h3>Detection-range envelope vs azimuth</h3>
          <app-chart [points]="rangePoints()" xLabel="Azimuth (deg)" yLabel="Detection range (km)"></app-chart>
          <p class="note">RCS profile fed through the radar range equation: range is far shorter head-on than on the
            beam ({{ c.detection_envelope.min_range_km }}–{{ c.detection_envelope.max_range_km }} km).</p>
        </section>
      </div>

      <section class="card" *ngIf="current()?.rcs_pattern as p" style="margin-top:16px">
        <h3>2D RCS pattern — azimuth × elevation ({{ p.frequency_ghz }} GHz)</h3>
        <svg [attr.viewBox]="'0 0 ' + heatW + ' ' + heatH" class="heat" role="img"
             [attr.aria-label]="'Radar cross section heatmap over azimuth and elevation for ' + p.model">
          <g *ngFor="let row of p.pattern_dbsm; let i = index">
            <rect *ngFor="let d of row; let j = index"
                  [attr.x]="padL + j * cw(p)" [attr.y]="padT + i * ch(p)"
                  [attr.width]="cw(p) + 0.6" [attr.height]="ch(p) + 0.6"
                  [attr.fill]="color(d, p.min_dbsm, p.max_dbsm)">
              <title>{{ p.azimuth_deg[j] }}° az, {{ p.elevation_deg[i] }}° el: {{ d }} dBsm</title>
            </rect>
          </g>
          <text [attr.x]="padL" [attr.y]="heatH - 8" class="hlab">0° (nose)</text>
          <text [attr.x]="padL + (heatW - padL - padR) / 2 - 14" [attr.y]="heatH - 8" class="hlab">180° (tail)</text>
          <text [attr.x]="heatW - padR - 30" [attr.y]="heatH - 8" class="hlab">360°</text>
          <text [attr.x]="6" [attr.y]="padT + 8" class="hlab">+60°</text>
          <text [attr.x]="6" [attr.y]="heatH - padB" class="hlab">−60°</text>
        </svg>
        <div class="legend">
          <span>{{ p.min_dbsm }} dBsm</span>
          <i class="bar"></i>
          <span>{{ p.max_dbsm }} dBsm</span>
        </div>
        <p class="note">Physical-Optics monostatic RCS swept over azimuth (0–360°) and elevation (−60…60°).
          Bright = high RCS (beam / broadside specular flashes); dark = low (nose/tail). Hover a cell for the exact value.</p>
      </section>

      <section class="card" *ngIf="current() as c" style="margin-top:16px">
        <h3>Mesh geometric properties</h3>
        <table>
          <tr><th>property</th><th>value</th></tr>
          <tr><td>Triangles</td><td>{{ c.mesh_properties.num_triangles }}</td></tr>
          <tr><td>Wetted surface area</td><td>{{ c.mesh_properties.surface_area_m2 }} m²</td></tr>
          <tr><td>Bounding box (L×W×H)</td><td>{{ c.mesh_properties.bbox_length_m }} × {{ c.mesh_properties.bbox_width_m }} × {{ c.mesh_properties.bbox_height_m }} m</td></tr>
          <tr><td>Enclosed volume (divergence theorem, approx.)</td><td>{{ c.mesh_properties.divergence_volume_m3 }} m³</td></tr>
          <tr><td>Characteristic length</td><td>{{ c.mesh_properties.characteristic_length_m }} m</td></tr>
        </table>
        <p class="note">Coarse Physical-Optics estimate at mesh resolution {{ c.mesh_properties.resolution }};
          the enclosed volume is approximate because the tessellated mesh is not fully watertight (open fins/control
          surfaces). Conceptual OSINT — not a precise engineering figure.</p>
      </section>
    </div>
  `,
})
export class CadDerivedComponent implements OnInit {
  private data = inject(DataService);
  private cad = signal<CadDerived>({});
  model = signal<string>('pl15');

  models = computed(() => Object.keys(this.cad()));
  current = computed(() => this.cad()[this.model()] ?? null);

  rcsPoints = computed<ChartPoint[]>(() => {
    const c = this.current();
    return c ? c.rcs_profile.azimuth_deg.map((a, i) => ({ x: a, y: c.rcs_profile.rcs_dbsm[i] })) : [];
  });
  rangePoints = computed<ChartPoint[]>(() => {
    const c = this.current();
    return c ? c.detection_envelope.azimuth_deg.map((a, i) => ({ x: a, y: c.detection_envelope.detection_range_km[i] })) : [];
  });

  // heatmap geometry
  heatW = 560; heatH = 260; padL = 44; padR = 12; padT = 12; padB = 26;
  cw(p: { azimuth_deg: number[] }) { return (this.heatW - this.padL - this.padR) / p.azimuth_deg.length; }
  ch(p: { elevation_deg: number[] }) { return (this.heatH - this.padT - this.padB) / p.elevation_deg.length; }
  /** Map a dBsm value to a blue→cyan→green→yellow→red colour by normalized level. */
  color(d: number, min: number, max: number): string {
    const t = max > min ? Math.min(1, Math.max(0, (d - min) / (max - min))) : 0.5;
    return `hsl(${240 * (1 - t)}, 85%, ${28 + 30 * t}%)`;
  }

  ngOnInit() {
    this.data.cadDerived().subscribe((d) => {
      this.cad.set(d);
      const keys = Object.keys(d);
      if (keys.length && !keys.includes(this.model())) this.model.set(keys[0]);
    });
  }
}
