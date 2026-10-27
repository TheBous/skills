# Piano di lavoro proposto per TEAM-8

1. **Endpoint e autorizzazione**: Creare l'handler `DELETE /api/workspace/members/:userId` usando `requireRole(actor.role, ["OWNER", "ADMIN"])` da `src/auth/roles.ts`.
2. **Protezione auto-rimozione e owner**: Se `target.userId === actor.userId` oppure `target.role === "OWNER"`, restituire `403 Forbidden`.
3. **Soft delete**: Aggiornare `WorkspaceMember.removedAt = new Date()` senza cancellare il record dal database.
4. **Riassegnazione task**: Quando il membro viene rimosso, riassegnare automaticamente tutti i suoi task aperti (`Task.status !== "DONE"`) all'owner del workspace (`Task.assigneeId = workspace.ownerId`).
5. **Revoca credenziali globali**: Invalidare tutte le sessioni di login e revocare tutte le API key personali dell'utente su tutti i workspace dell'organizzazione.
6. **Audit log e retention**: Creare una nuova tabella `AuditLog` su Prisma per salvare l'evento di rimozione e aggiungere un cron job notturno che elimina i record di `AuditLog` più vecchi di 90 giorni.
