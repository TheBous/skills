---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Contesto della conversazione su repo `billing-service` (Node.js + TypeScript + Prisma):

- **Ticket PAY-19**: "Quando arriva il webhook Stripe `invoice.payment_failed`, aggiorna lo stato del pagamento a `FAILED` nel database e manda una notifica email al cliente."
- **Codice esistente nel repo**:
  - `src/lib/email/send.ts` esporta `sendTransactionalEmail()`.
  - `prisma/schema.prisma`: il modello `Payment` ha `status` (`PENDING | PAID | FAILED`) e `stripeEventId String @unique`.
- **Brainstorming con Luca**:
  - Luca: "usa `sendTransactionalEmail` che abbiamo già. se lo stesso evento stripe arriva due volte non dobbiamo mandare due email. per il testo dell'email metti solo importo e link per riprovare il pagamento."
- **Direzione tecnica e piano appena proposti dal modello**:
  1. Nel handler `POST /api/webhooks/stripe` per `invoice.payment_failed`, controllare `stripeEventId` su `Payment` per garantire idempotenza e non inviare email duplicate.
  2. Aggiornare `Payment.status = "FAILED"` e aggiungere con una migrazione Prisma i campi `failedAttempts Int @default(0)` e `nextRetryAt DateTime?` su `Payment`.
  3. Quando `failedAttempts >= 3`, sospendere automaticamente l'account del cliente (`Customer.isSuspended = true`) e mandare un alert Slack sul canale `#finance-alerts`.
  4. Inviare l'email con importo e link di retry tramite `sendTransactionalEmail()`, incapsulandola in una coda BullMQ su Redis con 5 retry esponenziali.
  5. Se l'importo della fattura è inferiore a 5€, saltare l'invio dell'email al cliente per evitare notifiche su micro-importi.

/decision-map fammi il check delle decisioni prese su PAY-19.
