# In this demo the registry is a plain Python list, which is enough to
# show how search/routing behaves once there are a few dozen tools
# instead of just four. At real scale (hundreds or thousands of tools,
# e.g. a full PayPal API collection plus other services) this would
# move to a database or a dedicated tool catalog service, and
# tool_search.py would query it with embeddings instead of keywords
# (see DESIGN.md section 13).

tools = [
    # --- invoicing ---
    {
        "name": "create_invoice",
        "description": "Create an invoice for a customer",
        "category": "invoice",
        "parameters": ["customer", "amount"]
    },
    {
        "name": "send_invoice",
        "description": "Send an invoice to a customer",
        "category": "invoice",
        "parameters": ["customer", "amount"]
    },
    {
        "name": "void_invoice",
        "description": "Cancel an invoice that has not been paid yet",
        "category": "invoice",
        "parameters": ["invoice_id"]
    },
    {
        "name": "get_invoice_status",
        "description": "Check whether an invoice has been paid",
        "category": "invoice",
        "parameters": ["invoice_id"]
    },

    # --- payments ---
    {
        "name": "create_payment",
        "description": "Charge a customer for a one-off payment",
        "category": "payment",
        "parameters": ["customer", "amount"]
    },
    {
        "name": "capture_payment",
        "description": "Capture a previously authorized payment",
        "category": "payment",
        "parameters": ["payment_id"]
    },
    {
        "name": "refund_payment",
        "description": "Refund a payment fully or partially",
        "category": "payment",
        "parameters": ["payment_id", "amount"]
    },
    {
        "name": "get_payment_status",
        "description": "Check the status of a payment",
        "category": "payment",
        "parameters": ["payment_id"]
    },

    # --- disputes ---
    {
        "name": "get_dispute",
        "description": "Check whether a customer has an open dispute",
        "category": "dispute",
        "parameters": ["user_id"]
    },
    {
        "name": "list_disputes",
        "description": "List all open disputes for the account",
        "category": "dispute",
        "parameters": []
    },
    {
        "name": "respond_to_dispute",
        "description": "Submit evidence or a response for an open dispute",
        "category": "dispute",
        "parameters": ["dispute_id", "message"]
    },
    {
        "name": "escalate_dispute",
        "description": "Escalate a dispute to claim status",
        "category": "dispute",
        "parameters": ["dispute_id"]
    },

    # --- reporting ---
    {
        "name": "get_sales_report",
        "description": "Get total sales volume and sales report",
        "category": "report",
        "parameters": []
    },
    {
        "name": "get_transaction_report",
        "description": "Get a detailed list of transactions for a date range",
        "category": "report",
        "parameters": ["start_date", "end_date"]
    },
    {
        "name": "get_payout_report",
        "description": "Get a summary of payouts for a date range",
        "category": "report",
        "parameters": ["start_date", "end_date"]
    },

    # --- payouts ---
    {
        "name": "create_payout",
        "description": "Send a payout to a seller or vendor",
        "category": "payout",
        "parameters": ["recipient", "amount"]
    },
    {
        "name": "get_payout_status",
        "description": "Check whether a payout has completed",
        "category": "payout",
        "parameters": ["payout_id"]
    },

    # --- subscriptions ---
    {
        "name": "create_subscription",
        "description": "Set up a recurring subscription for a customer",
        "category": "subscription",
        "parameters": ["customer", "plan"]
    },
    {
        "name": "cancel_subscription",
        "description": "Cancel a customer's active subscription",
        "category": "subscription",
        "parameters": ["subscription_id"]
    },
    {
        "name": "get_subscription_status",
        "description": "Check whether a subscription is active",
        "category": "subscription",
        "parameters": ["subscription_id"]
    },

    # --- account ---
    {
        "name": "get_account_balance",
        "description": "Check the current available account balance",
        "category": "account",
        "parameters": []
    },
    {
        "name": "update_account_details",
        "description": "Update account contact or business details",
        "category": "account",
        "parameters": ["field", "value"]
    },
    {
        "name": "get_account_limits",
        "description": "Check current sending and receiving limits",
        "category": "account",
        "parameters": []
    },
]
