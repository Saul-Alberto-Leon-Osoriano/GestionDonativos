/**
 * Descarga un archivo de texto en el navegador. En SSR no hace nada.
 */
export function descargarArchivo(
  nombre: string,
  contenido: string,
  tipo = 'text/csv;charset=utf-8;',
): void {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return;
  }

  const blob = new Blob([`\uFEFF${contenido}`], { type: tipo });
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombre;
  enlace.rel = 'noopener';
  enlace.click();
  URL.revokeObjectURL(url);
}
