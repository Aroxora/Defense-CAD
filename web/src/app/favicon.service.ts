import { Injectable } from '@angular/core';
import { CALC_BY_ID } from './calc-defs';

/**
 * Dynamic favicon that reflects the section / calculator the user is viewing. Renders a
 * crisp SVG (emoji glyph on the dark theme square with an accent ring) as a data-URI and
 * swaps the document icon on each route change. Pure DOM; no dependencies.
 */
@Injectable({ providedIn: 'root' })
export class FaviconService {
  private readonly ACCENT = '#46e0c0';
  private readonly BG = '#0a0e14';

  // First URL segment -> glyph
  private readonly sectionGlyph: Record<string, string> = {
    portfolio: '💰', calculators: '🧮', 'cad-derived': '📐', ew: '📡',
    doctrine: '📜', reference: '📖', methodology: '🔬',
  };

  // Calculator category -> glyph (for /calculators/:id)
  private readonly categoryGlyph: Record<string, string> = {
    Radar: '📡', EW: '⚡', Detection: '🎯', RCS: '✈️', 'Missile defense': '🛡️',
    Procurement: '💰', 'CAD-derived': '📐', Comms: '🛰️', PNT: '🧭', 'IR / EO': '🌡️',
    Undersea: '🌊', Space: '🛰️', Kinematics: '📈', 'Directed Energy': '🔦',
    Guidance: '🎯', 'ISR / SAR': '🛰️', Propagation: '🌧️', 'Pulse-Doppler': '📶',
  };

  /** Update the favicon to match the current router URL. */
  updateForUrl(url: string): void {
    this.setGlyph(this.glyphForUrl(url));
  }

  private glyphForUrl(url: string): string {
    const parts = url.split('?')[0].split('/').filter(Boolean);
    if (parts[0] === 'calculators' && parts[1]) {
      const cat = CALC_BY_ID[parts[1]]?.category;
      if (cat && this.categoryGlyph[cat]) return this.categoryGlyph[cat];
    }
    return (parts[0] && this.sectionGlyph[parts[0]]) || '◆';
  }

  private setGlyph(glyph: string): void {
    if (typeof document === 'undefined') return;
    const svg =
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">` +
      `<rect width="64" height="64" rx="14" fill="${this.BG}" stroke="${this.ACCENT}" stroke-width="4"/>` +
      `<text x="32" y="36" font-size="34" text-anchor="middle" dominant-baseline="central"` +
      ` font-family="Apple Color Emoji,Segoe UI Emoji,Noto Color Emoji,sans-serif">${glyph}</text></svg>`;
    const href = 'data:image/svg+xml,' + encodeURIComponent(svg);
    let link = document.querySelector<HTMLLinkElement>('link[rel~="icon"]');
    if (!link) {
      link = document.createElement('link');
      link.rel = 'icon';
      document.head.appendChild(link);
    }
    link.type = 'image/svg+xml';
    link.href = href;
  }
}
