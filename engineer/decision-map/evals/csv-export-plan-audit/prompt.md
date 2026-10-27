---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Contesto della conversazione su repo `inventory-web` (React + TypeScript):

- **Ticket INV-42**: "Nella pagina `/invoices` aggiungi un bottone per esportare in CSV le fatture filtrate."
- **Brainstorming con Luca**:
  - Luca: "voglio un bottone semplice in alto a destra accanto al filtro, senza modali. il file deve chiamarsi `fatture-YYYY-MM-DD.csv` e i prezzi vanno in euro formattati come in tabella."
- **Codice esistente nel repo**:
  - `src/pages/InvoicesPage.tsx` mostra `InvoicesTable` e usa `formatEuro` da `src/lib/format.ts` per la colonna importo.
- **Direzione tecnica e piano appena proposti dal modello**:
  1. Aggiungere `ExportInvoicesButton.tsx` in alto a destra accanto al filtro in `InvoicesPage.tsx`, senza aprire modali, scaricando `fatture-YYYY-MM-DD.csv`.
  2. Formattare gli importi nel CSV riusando `formatEuro` da `src/lib/format.ts`.
  3. Generare il CSV lato client con separatore `;` e codifica UTF-8 con BOM per Excel.
  4. Esportare le colonne: `ID, Numero, Cliente, Importo, Stato, Data Scadenza, Note Interne`.
  5. Escludere automaticamente dal CSV le fatture con stato `BOZZA` e `ANNULLATA` anche se presenti nel filtro.
  6. Bloccare l'export con un toast di errore se le fatture filtrate sono più di 1.000.
  7. Salvare in `localStorage` il timestamp dell'ultimo download per impedire un secondo export prima di 30 secondi.

/decision-map controlla il piano che hai appena proposto per INV-42 prima che iniziamo a scrivere codice.
