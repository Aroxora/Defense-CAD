import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

// Firebase + Analytics are initialized lazily by AnalyticsService (injected in AppComponent),
// which is guarded by analytics isSupported() for non-browser/unsupported environments.
bootstrapApplication(AppComponent, appConfig).catch((err) => console.error(err));
