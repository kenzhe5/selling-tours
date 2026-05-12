import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found-page',
  imports: [RouterLink],
  template: `
    <section class="container-page py-24 text-center">
      <div class="rounded-[2rem] border border-border bg-paper p-10">
        <p class="text-sm font-black uppercase tracking-[0.22em] text-accent">404</p>
        <h1 class="section-title mt-3">This route wandered off.</h1>
        <p class="mx-auto mt-5 max-w-xl text-xl leading-8 text-muted">
          Return to the catalog and keep the booking demo on the happy path.
        </p>
        <a class="btn-primary mt-8" routerLink="/">Back to tours</a>
      </div>
    </section>
  `,
})
export class NotFoundPageComponent {}
