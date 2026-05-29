import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../data.service';
import { FactChecks } from '../models';

@Component({
  selector: 'app-methodology',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="wrap">
      <section class="intro">
        <h2>Methodology &mdash; physics, scoring, code &amp; verification</h2>
        <p>Every number traces to a textbook relationship in the <code>osint_cad</code> Python package; the browser
          engine is parity-checked against it in CI. Full write-up in <code>METHODOLOGY.md</code>.</p>
      </section>

      <div class="cols">
        <section class="card">
          <h3>Physics-based analysis</h3>
          <ul class="m-list">
            <li><b>Detection range</b> &mdash; radar range equation, R &prop; &sigma;<sup>1/4</sup></li>
            <li><b>Propagation</b> &mdash; Friis + ITU-R P.676 gas absorption</li>
            <li><b>RCS</b> &mdash; empirical aspect models + Physical-Optics (&gamma;<sup>2</sup>)</li>
            <li><b>Geolocation</b> &mdash; TDOA/FDOA, GDOP, Cram&eacute;r-Rao bound</li>
            <li><b>Radar horizon</b> &mdash; 4/3-Earth, R &asymp; 4.12&middot;(&radic;h&#8341;+&radic;h&#8348;)</li>
            <li><b>Missile defense</b> &mdash; salvo 1&minus;(1&minus;Pk)<sup>n</sup>, cost-exchange</li>
          </ul>
          <p class="note">Three physics bugs were fixed and pinned by regression tests (&sigma;<sup>1/4</sup> seeker scaling, &gamma;<sup>2</sup> PO RCS, ITU-R P.676 absorption).</p>
        </section>
        <section class="card">
          <h3>Scoring &amp; rating</h3>
          <pre class="formula">lifecycle($B) = (R&amp;D + unit&times;qty + O&amp;M&times;qty&times;life)/1000
adj_benefit   = benefit &times; survivability / 100
value_index   = adj_benefit / lifecycle($B)   &larr; headline rating
uncertainty   = 1 &minus; confidence
value CI       = value_index &times; (1 &plusmn; uncertainty&middot;&radic;3)</pre>
          <p class="note"><b>value_index</b> = survivability-adjusted benefit per $B (higher = better). Punishes both
            high cost and low survivability &mdash; why the conceptual battleship ranks last. Benefit/survivability are
            coarse 0&ndash;100 analyst ratings, so each score carries a confidence interval. A value-for-money study aid,
            <b>not</b> a procurement or operational decision.</p>
        </section>
      </div>

      <section class="card" *ngIf="facts() as fc">
        <h3>Hard-fact corroboration (Tavily) &mdash; last run {{ fc.generated }}</h3>
        <table>
          <tr><th>fact</th><th>value used</th><th>status</th><th>news figure</th></tr>
          <tr *ngFor="let f of fc.facts">
            <td>{{ f.claim }}</td><td>{{ f.value_used }} {{ f.unit }}</td>
            <td><span class="fstatus" [attr.data-s]="f.status">{{ f.status }}</span></td>
            <td>{{ f.parsed_value !== undefined ? f.parsed_value : '—' }}</td>
          </tr>
        </table>
        <p class="note">Corroborated = comparable figure within &plusmn;25%. <i>possible_discrepancy</i> flagged for human
          review (values never auto-overwritten). The verifier never fabricates numbers.</p>
      </section>

      <section class="card">
        <h3>CI/CD &mdash; verified before posting</h3>
        <p>CI runs the full <code>pytest</code> suite on Python 3.10 &amp; 3.12, a TypeScript&harr;Python <b>engine
          parity</b> check, and a production Angular build &mdash; on every push. The site is redeployed only after green.</p>
        <pre class="formula">pip install -e ".[dev]" &amp;&amp; pytest
cd web &amp;&amp; npm ci &amp;&amp; node parity-check.mjs &amp;&amp; npx ng build</pre>
      </section>
    </div>
  `,
})
export class MethodologyComponent implements OnInit {
  private data = inject(DataService);
  facts = signal<FactChecks | null>(null);
  ngOnInit() { this.data.factChecks().subscribe((d) => this.facts.set(d)); }
}
