from lnbits.db import Database


async def m001_proxyllm_init(db: Database):
    # Table for registered LLM agents
    await db.execute(
        f"""
        CREATE TABLE proxyllm.agents (
            id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            api_url TEXT NOT NULL,
            api_key TEXT,
            model_name TEXT NOT NULL,
            specialization TEXT,
            price_per_unit INTEGER NOT NULL,
            unit_type TEXT NOT NULL,
            available BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )

    # Table for prepaid access keys
    await db.execute(
        f"""
        CREATE TABLE proxyllm.access_keys (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            payment_hash TEXT NOT NULL,
            api_key TEXT NOT NULL,
            prepaid_units INTEGER NOT NULL,
            used_units INTEGER NOT NULL DEFAULT 0,
            active BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )

    # Table for usage logs
    await db.execute(
        f"""
        CREATE TABLE proxyllm.usage_logs (
            id TEXT PRIMARY KEY,
            access_key_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            units_used INTEGER NOT NULL,
            input_hash TEXT,
            request_snapshot TEXT,
            response_snapshot TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )
