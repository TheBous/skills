---
type: llm
focus: trace
weight: 1
---

The model-assumed list includes the unrequested code decisions: the Prisma migration adding failedAttempts and nextRetryAt, mutating Customer.isSuspended, and wrapping sendTransactionalEmail in a BullMQ/Redis queue.
