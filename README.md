# Scalable-Agentic-System.
Python-based scalable AI agent system with tool search, parameter validation, retries, state management, RAG, and multi-step tool execution.



# Datazoic Scalable Agentic System

A simple Python-based agent system that selects the relevant tools before sending them to the AI agent.

The main idea is to avoid sending all available tools to the LLM. The system first searches for the relevant tools, then the agent chooses the required tool and executes it.

## Main Features

* Tool registry
* Tool search
* AI agent tool selection
* Parameter validation
* Tool execution
* Retry handling
* Multi-step tool execution
* Simple state management
* RAG support
* System search
* Fallback when the LLM is not available

## How It Works

The basic flow is:

```text
User Request
     ↓
Router
     ↓
Tool Search
     ↓
Relevant Tools
     ↓
AI Agent
     ↓
Parameter Validation
     ↓
Tool Executor
     ↓
Result
```

For example, if the user asks for a sales report, the system searches the available tools and finds the relevant sales report tool instead of sending every tool to the agent.

## Project Structure

```text
Datazoic-Scalable-Agentic-System/
│
├── main.py
├── agent.py
├── router.py
├── tool_registry.py
├── tool_search.py
├── tools.py
├── llm_client.py
├── error_handler.py
├── state.py
├── rag_tool.py
├── system_search.py
├── config.py
├── requirements.txt
│
├── ARCHITECTURE.txt
└── DESIGN.md
```

## Tools

The project currently contains 23 tools in different categories.

### Invoice

* create_invoice
* send_invoice
* void_invoice
* get_invoice_status

### Payment

* create_payment
* capture_payment
* refund_payment
* get_payment_status

### Dispute

* get_dispute
* list_disputes
* respond_to_dispute
* escalate_dispute

### Reports

* get_sales_report
* get_transaction_report
* get_payout_report

### Payout

* create_payout
* get_payout_status

### Subscription

* create_subscription
* cancel_subscription
* get_subscription_status

### Account

* get_account_balance
* update_account_details
* get_account_limits

## Tool Search

The system does not send all tools to the AI agent.

Instead, the user request is searched against the tool registry. The most relevant tools are selected and only those tools are given to the agent.

The current system limits the number of tools sent to the agent.

```python
MAX_TOOLS_FOR_AGENT = 5
```

This makes the tool selection process smaller and easier to manage.

## Agent

After the relevant tools are found, the agent selects the tool that matches the user's request.

For example:

```text
User: Show me the sales report

        ↓

Tool Search

        ↓

get_sales_report

        ↓

Agent selects the tool

        ↓

Tool executes

        ↓

Sales report returned
```

If the LLM is available, the system uses it for tool selection.

If the LLM is not available, the project has a simple fallback method using keywords.

## Parameter Validation

Before executing a tool, the required parameters are checked.

For example, creating an invoice requires:

```text
customer
amount
```

The system checks these values before executing the tool.

This helps prevent invalid tool calls.

## Multi-Step Requests

The system also supports simple multi-step operations.

Example:

```text
Create an invoice and send it
```

The flow is:

```text
Create Invoice
      ↓
Get invoice_id
      ↓
Send Invoice
```

The invoice ID from the first operation is passed to the next operation.

## Retry Handling

If a tool fails, the system can retry the operation.

The retry count is configured in `config.py`.

```python
MAX_RETRIES = 2
```

If the tool still fails after the retries, an error message is returned.

## State Management

The project keeps a small amount of state information:

```text
last_request
last_tool
last_result
```

This can be used to understand the previous operation performed by the agent.

## RAG

A simple local RAG component is included in the project.

It contains basic information related to:

* Invoice
* Payment
* Dispute

Documentation-related questions can be routed to the RAG component instead of the tool agent.

## System Search

The system also supports simple system-related queries.

For example, a user can ask about available invoice tools or the previous request and result.

## LLM Support

The project can use Anthropic Claude for tool selection.

The API key is read from an environment variable.

```text
ANTHROPIC_API_KEY
```

If the API key or Anthropic package is not available, the project uses the built-in fallback logic.

## Configuration

The main configuration values are stored in `config.py`.

```python
MAX_TOOLS_FOR_AGENT = 5
MAX_RETRIES = 2
MAX_CHAIN_STEPS = 3
```

## Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
```

Go to the project folder:

```bash
cd Datazoic-Scalable-Agentic-System
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Project

Run:

```bash
python main.py
```

The application starts with:

```text
Datazoic Scalable Agentic System
```

Enter a request and the agent will process it.

To stop the application:

```text
exit
```

## Example

```text
User: Create an invoice

Agent: Invoice created successfully. Invoice ID: INV1001
```

Another example:

```text
User: Create an invoice and send it

Agent:
Invoice created successfully.
Invoice sent successfully.
```

## Current Implementation

This project is designed as a simple working demonstration.

The payment and other external API operations are mocked for the assignment. The main focus is the agent workflow, tool search, tool selection, validation, execution, and multi-step handling.

## Future Improvements

Some possible improvements for a production system are:

* Use embeddings for better tool search
* Use a vector database for a large number of tools
* Add authentication and permissions
* Connect real payment APIs
* Add better logging
* Add more test cases
* Add monitoring for agent execution

## Key Idea

The main idea of this project is:

```text
DO NOT SEND ALL TOOLS TO THE LLM.

FIRST FIND THE RELEVANT TOOLS.

THEN LET THE AGENT CHOOSE.
```

This approach helps keep the agent focused on the tools that are actually related to the user's request.
