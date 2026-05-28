# Prompt de la sesión programada (8 am)

Pega este texto como prompt de la sesión programada de Claude Code en la web.

---

Ejecuta el skill `supabase-health` para el proyecto **BD Domus**
(`ifqwrtheakkvgezewxqx`). Sigue su proceso de principio a fin:

1. Corre `scripts/fetch_metrics.sh` para las métricas de infra (CPU, disk IO/burst
   balance, disco, RAM, egress, conexiones). Si falta `SUPABASE_SERVICE_ROLE_KEY`,
   sigue con la introspección y anótalo.
2. Ejecuta las consultas de `references/queries.md` con `execute_sql`.
3. Corre `get_advisors(performance)` y `get_logs(postgres)` + `get_logs(api)`.
4. Evalúa contra `references/thresholds.md` y arma el `status` global + hallazgos
   accionables (máx 5).
5. Manda el payload JSON a `https://vicente-domus.app.n8n.cloud/webhook/supabase-health`
   para que llegue por WhatsApp.

Deja el análisis completo en el chat. No hagas cambios en la BD ni en el repo: esto
es solo lectura + notificación.

---

## Setup único (una sola vez antes de agendar)

1. **Variable de entorno** del entorno cloud: `SUPABASE_SERVICE_ROLE_KEY`
   (service_role secret de Supabase → Project Settings → API keys). **No** commitear.
2. **Workflow n8n** `DomusBot - Alerta Salud Supabase` (ya creado, id `Z7ftgjmBjQ7bPMTV`,
   webhook `/webhook/supabase-health`). Manda el resumen como **texto libre** vía el
   sub-workflow `DomusBot - Enviar con Guard CSW` (respeta la ventana CSW; no requiere
   plantilla ni credencial propia). Destinatario por defecto: Vicente
   (`whatsapp:+529991569426`), sobreescribible con el campo `to` del payload.
   - Solo falta **activarlo** (toggle Active en n8n) para que el webhook quede en
     producción. Ya fue probado end-to-end con una ejecución manual.

## Cómo agendarlo (UI de Claude Code web)

- **Repo:** `vicentedomus/domus-hub`
- **Branch:** `main` (o el que prefieras tener vivo)
- **Cron:** `0 8 * * *`  ·  **Timezone:** `America/Mexico_City`
- Docs: https://code.claude.com/docs/en/claude-code-on-the-web
