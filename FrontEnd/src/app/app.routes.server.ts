import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: 'registrar_encomienda',
    renderMode: RenderMode.Client,
  },
  {
    path: 'panel-control',
    renderMode: RenderMode.Client,
  },
  {
    path: 'gestor-usuarios',
    renderMode: RenderMode.Client,
  },
  {
    path: '**',
    renderMode: RenderMode.Prerender,
  },
];
