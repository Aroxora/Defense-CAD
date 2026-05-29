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

  ngOnInit() {
    this.data.cadDerived().subscribe((d) => {
      this.cad.set(d);
      const keys = Object.keys(d);
      if (keys.length && !keys.includes(this.model())) this.model.set(keys[0]);
    });
  }
}
