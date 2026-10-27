# Note brainstorming con Luca (TEAM-8)

**Luca**: "ok ma un admin non deve poter rimuovere se stesso e nemmeno l'owner del workspace. se prova a farlo torna 403. non cancellare la riga dal db, usa il campo `removedAt` che c'è già su `WorkspaceMember`."
