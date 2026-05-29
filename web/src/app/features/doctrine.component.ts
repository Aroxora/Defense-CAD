import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../data.service';
import { DoctrineData, DoctrineSide } from '../models';

@Component({
  selector: 'app-doctrine',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="wrap">
      <section class="intro">
        <h2>Strategy &amp; doctrine &mdash; OSINT reference</h2>
        <p>Symmetric, descriptive open-source characterizations of published PLA and U.S. DoD concepts,
          cross-referenced to the modeled systems. <b>Not operational guidance.</b></p>
      </section>
      <div *ngFor="let side of sides()">
        <h2 class="side-h">{{ side.side }}</h2>
        <div class="concept" *ngFor="let c of side.concepts">
          <div class="chead">
            <h3>{{ c.name_en }}</h3>
            <span class="native">{{ c.name_native }}</span>
            <span class="conf">conf {{ c.confidence | percent }}</span>
          </div>
          <p>{{ c.summary }}</p>
          <p class="notes"><b>Study with:</b> {{ c.analytical_notes }}</p>
          <div class="tags"><span class="tag" *ngFor="let s of c.related_systems">{{ s }}</span></div>
        </div>
      </div>
    </div>
  `,
})
export class DoctrineComponent implements OnInit {
  private data = inject(DataService);
  private d = signal<DoctrineData | null>(null);
  sides = () => { const x = this.d(); return x ? ([x.pla, x.dod].filter(Boolean) as DoctrineSide[]) : []; };
  ngOnInit() { this.data.doctrine().subscribe((x) => this.d.set(x)); }
}
