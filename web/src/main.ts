import { bootstrapApplication } from '@angular/platform-browser';
import { initializeApp } from 'firebase/app';
import { getAnalytics, isSupported } from 'firebase/analytics';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { environment } from './environments/environment';

// Initialize Firebase (analytics is best-effort; guarded for unsupported environments).
try {
  const app = initializeApp(environment.firebase);
  isSupported()
    .then((ok) => {
      if (ok) {
        getAnalytics(app);
      }
    })
    .catch(() => void 0);
} catch (e) {
  console.warn('Firebase init skipped:', e);
}

bootstrapApplication(AppComponent, appConfig).catch((err) => console.error(err));
