import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DataService } from '../data.service';
import { EwStrategy } from '../models';

@Component({
  selector: 'app-ew',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="wrap" *ngIf="ew() as e">
      <section class="intro">
        <h2>EW strategy &mdash; defensive/analytical study</h2>
        <p class="premise">{{ e.premise }}</p>
        <p class="note"><b>Defensive, analytical OSINT example for study.</b> Parameters are illustrative with wide
          uncertainty; this is <b>not operational guidance and not a targeting system</b>.</p>
        <p class="note">Explore the underlying physics interactively in the
          <a routerLink="/calculators/esm-intercept">ESM intercept</a>,
          <a routerLink="/calculators/jammer-to-signal">J/S</a>, and
          <a routerLink="/calculators/tdoa-geolocation">geolocation</a> calculators.</p>
      </section>

      <div class="loe-grid">
        <div class="loe" *ngFor="let l of e.lines_of_effort">
          <div class="loe-id">{{ l.id }}</div>
          <h3>{{ l.title }}</h3>
          <p class="sub">{{ l.subtitle }}</p>
          <p>{{ l.detail }}</p>
        </div>
      </div>

      <div class="cols">
        <section class="card">
          <h3>Passive intercept range vs dwell</h3>
          <table>
            <tr><th>dwell (µs)</th><th>proc gain (dB)</th><th>range (km)</th></tr>
            <tr *ngFor="let r of e.intercept_vs_dwell"><td>{{ r.dwell_us }}</td><td>{{ r.proc_gain_db }}</td><td>{{ r.intercept_range_km }}</td></tr>
          </table>
          <p class="note">Best case &mdash; presumes the observer is in a sidelobe during a burst.</p>
        </section>
        <section class="card">
          <h3>Geolocation sizing (TDOA CRLB, 10 ns sync)</h3>
          <table>
            <tr><th>N</th><th>baseline km</th><th>GDOP</th><th>ops CEP (m)</th></tr>
            <tr *ngFor="let r of e.geolocation_sizing">
              <td>{{ r.platforms }}</td><td>{{ r.baseline_km }}</td><td>{{ r.gdop ?? '—' }}</td>
              <td>{{ r.ill_conditioned ? 'ill-cond' : r.ops_cep_m }}</td>
            </tr>
          </table>
          <p class="note">CRLB floor &times;5 for hopping/multipath. ≥4 platforms required.</p>
        </section>
      </div>

      <div class="cols">
        <section class="card">
          <h3>Own-datalink hardening</h3>
          <table>
            <tr><th>sidelobe (dB)</th><th>EIRP (dBm)</th><th>adversary intercept (km)</th></tr>
            <tr *ngFor="let r of e.hardening_sweep"><td>{{ r.sidelobe_db }}</td><td>{{ r.sidelobe_eirp_dbm }}</td><td>{{ r.adversary_intercept_km }}</td></tr>
          </table>
        </section>
        <section class="card">
          <h3>EW reallocation ({{ e.reallocation.jam_power_kw }} kW &#64; {{ e.reallocation.range_km }} km)</h3>
          <div class="js">
            <div [class.good]="e.reallocation.radar_effective">
              <span>{{ e.reallocation.js_radar_db }} dB</span>
              <label>J/S vs APG-81 radar &mdash; {{ e.reallocation.radar_effective ? 'EFFECTIVE' : 'marginal' }}</label>
            </div>
            <div [class.bad]="!e.reallocation.madl_effective">
              <span>{{ e.reallocation.js_madl_db }} dB</span>
              <label>J/S vs MADL (standoff LPI) &mdash; {{ e.reallocation.madl_effective ? 'opportunistic' : 'INEFFECTIVE' }}</label>
            </div>
          </div>
          <p class="note">After a {{ e.reallocation.madl_isolation_db }} dB spatial-isolation + processing-gain penalty.</p>
        </section>
      </div>
    </div>
  `,
})
export class EwComponent implements OnInit {
  private data = inject(DataService);
  ew = signal<EwStrategy | null>(null);
  ngOnInit() { this.data.ewStrategy().subscribe((d) => this.ew.set(d)); }
}
