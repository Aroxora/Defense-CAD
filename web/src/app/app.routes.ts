import { Routes } from '@angular/router';
import { GoldenFleetComponent } from './components/golden-fleet/golden-fleet.component';
import { SidelobeDetectionComponent } from './components/sidelobe-detection/sidelobe-detection.component';
import { AsbmKillChainComponent } from './components/asbm-kill-chain/asbm-kill-chain.component';
import { DiseaseCureComponent } from './components/disease-cure/disease-cure.component';

export const routes: Routes = [
  { path: '', component: DiseaseCureComponent },
  { path: 'golden-fleet', component: GoldenFleetComponent },
  { path: 'sidelobe-detection', component: SidelobeDetectionComponent },
  { path: 'asbm-kill-chain', component: AsbmKillChainComponent },
  { path: 'disease-cure', component: DiseaseCureComponent },
  { path: '**', redirectTo: '' }
];
