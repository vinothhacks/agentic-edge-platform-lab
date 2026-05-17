# ADR-0004 · In-memory queue first

## Status
Accepted

## Context

Provisioning is asynchronous — the broker must return `202 Accepted` immediately and let a worker do the work. The textbook choice is Redis + Celery / RQ.

But for a single-host teaching lab, "spin up Redis just to demo a job queue" buries the lesson. The thing readers need to internalise is: *the broker writes a row in `PENDING`, a worker picks it up, the state machine advances*. That works with any queue.

## Decision

Start with an **in-memory queue** + a polling worker. The worker scans `provisioning_operations` for `PENDING` rows every second. The DB *is* the queue. Production swap is one file: `apps/worker/queue.py` from in-memory to Redis-backed.

## Consequences

**Good**
- One fewer container in the demo.
- The state machine logic is identical to what you'd write for Redis.
- Easier to debug — `sqlite3 aepl.db` and you can see every job's state.

**Bad**
- Single-worker only. Multiple workers would race for the same `PENDING` rows without row-locking.
- Polling has a 1-second floor on latency. Production should switch to Redis pub/sub or PostgreSQL `LISTEN/NOTIFY`.
- The DB-as-queue pattern doesn't scale beyond a few hundred ops/sec.

We accept all three trade-offs because **none of them get in the way of learning the state machine**, which is the actual lesson.
