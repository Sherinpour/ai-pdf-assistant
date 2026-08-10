export interface ApiErrorDetail {
  detail?: string | Array<{ msg?: string; loc?: unknown[] }>
}
