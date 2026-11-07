# ADR 003: synthetic bank-side settlement sources

Accepted. Fixed RNG and source timestamps produce reproducible payment-to-payout-to-credit data.
No live Stripe or bank integration. Tradeoff: privacy, replay reliability and no external dependency
versus limited operational validity. Real merchant workflows, source timing, refund lifecycles and
policy variance require discovery. Cumulative payment refunds are modeled inline; separate refund
and fee-adjustment ledgers are deferred. One synthetic merchant workspace, no tenant claims.
