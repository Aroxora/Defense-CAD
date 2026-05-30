import { Component, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { AnalyticsService } from './analytics.service';
import { FaviconService } from './favicon.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <header class="topbar">
      <div class="brand">
        <span class="logo" aria-hidden="true">◆</span>
        <div>
          <h1>Defense OSINT <span class="byline">by TrenchWork.org</span></h1>
          <p>A TrenchWork.org Computer Network Defense initiative &mdash; physics-based OSINT
            defense-systems analysis: calculators · procurement · EW · doctrine</p>
        </div>
      </div>
      <span class="badge">UNCLASSIFIED // CONCEPTUAL // OSINT</span>
    </header>

    <nav class="tabs">
      <a routerLink="/portfolio" routerLinkActive="active">Procurement &amp; R&amp;D</a>
      <a routerLink="/calculators" routerLinkActive="active">Calculators</a>
      <a routerLink="/cad-derived" routerLinkActive="active">CAD-derived</a>
      <a routerLink="/ew" routerLinkActive="active">EW Strategy</a>
      <a routerLink="/doctrine" routerLinkActive="active">Doctrine (PLA / DoD)</a>
      <a routerLink="/reference" routerLinkActive="active">Reference</a>
      <a routerLink="/methodology" routerLinkActive="active">Methodology</a>
    </nav>

    <router-outlet></router-outlet>

    <footer>
      <b>Defense OSINT by TrenchWork.org</b> · Computer Network Defense.
      Conceptual, OSINT, public-release analysis for education/study &mdash; not operational guidance and not a targeting
      system. Source of truth: the <code>osint_cad</code> Python package; the browser engine is parity-checked against it.
      <br />
      Licensed under <b>GNU AGPL-3.0-only</b>. © 2026 <b>Bo Shang</b> &mdash;
      <a href="mailto:bo@trenchwork.org">bo&#64;trenchwork.org</a> · TrenchWork.org
    </footer>
  `,
})
export class AppComponent {
  private analytics = inject(AnalyticsService);
  private favicon = inject(FaviconService);

  constructor(router: Router) {
    // On each client-side route change: log a GA4 page_view and update the dynamic favicon
    // (GA4 only auto-logs the initial load).
    router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((e) => {
        this.analytics.pageView(e.urlAfterRedirects);
        this.favicon.updateForUrl(e.urlAfterRedirects);
      });
  }
}
