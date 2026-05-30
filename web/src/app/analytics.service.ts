import { Injectable } from '@angular/core';
import { getApps, initializeApp } from 'firebase/app';
import { Analytics, getAnalytics, isSupported, logEvent } from 'firebase/analytics';
import { environment } from '../environments/environment';

/**
 * Firebase Analytics (GA4) wrapper. Initializes lazily and only where supported (real
 * browser); all calls are no-ops otherwise. Provides SPA route page-view tracking plus
 * simple custom events. No PII is sent — only route paths and titles.
 */
@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private analytics: Analytics | null = null;
  private ready: Promise<void>;

  constructor() {
    this.ready = isSupported()
      .then((ok) => {
        if (!ok) return;
        const app = getApps().length ? getApps()[0] : initializeApp(environment.firebase);
        this.analytics = getAnalytics(app);
      })
      .catch(() => undefined);
  }

  /** Log a custom GA4 event once analytics is ready (no-op if unsupported). */
  log(event: string, params?: Record<string, unknown>): void {
    this.ready.then(() => {
      if (this.analytics) logEvent(this.analytics, event as never, params as never);
    });
  }

  /** Log a virtual page view for an Angular client-side route change. */
  pageView(path: string, title?: string): void {
    this.log('page_view', {
      page_path: path,
      page_title: title ?? (typeof document !== 'undefined' ? document.title : path),
      page_location: typeof location !== 'undefined' ? location.href : path,
    });
  }
}
