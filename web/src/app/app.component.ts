import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <header class="topbar">
      <div class="brand">
        <span class="logo" aria-hidden="true">◆</span>
        <div>
          <h1>OSINT Defense-CAD</h1>
          <p>Physics-based, interactive analysis &mdash; calculators · procurement · EW · doctrine</p>
        </div>
      </div>
      <span class="badge">UNCLASSIFIED // CONCEPTUAL // OSINT</span>
    </header>

    <nav class="tabs">
      <a routerLink="/portfolio" routerLinkActive="active">Procurement &amp; R&amp;D</a>
      <a routerLink="/calculators" routerLinkActive="active">Calculators</a>
      <a routerLink="/ew" routerLinkActive="active">EW Strategy</a>
      <a routerLink="/doctrine" routerLinkActive="active">Doctrine (PLA / DoD)</a>
      <a routerLink="/methodology" routerLinkActive="active">Methodology</a>
    </nav>

    <router-outlet></router-outlet>

    <footer>
      Conceptual, OSINT, public-release analysis for education/study &mdash; not operational guidance and not a targeting
      system. Source of truth: the <code>osint_cad</code> Python package; the browser engine is parity-checked against it.
      MIT licensed.
    </footer>
  `,
})
export class AppComponent {}
