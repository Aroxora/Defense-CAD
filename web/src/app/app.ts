import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { initializeApp, FirebaseApp } from 'firebase/app';
import { getAnalytics, logEvent, Analytics } from 'firebase/analytics';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `<router-outlet></router-outlet>`,
  styles: [`
    :host {
      display: block;
      min-height: 100vh;
    }
  `]
})
export class App implements OnInit {
  private firebaseApp!: FirebaseApp;
  private analytics!: Analytics;

  ngOnInit(): void {
    this.firebaseApp = initializeApp(environment.firebase);
    if (environment.production) {
      this.analytics = getAnalytics(this.firebaseApp);
      logEvent(this.analytics, 'page_view', {
        page_title: 'Golden Fleet Program',
        page_location: window.location.href
      });
    }
  }
}
