# Datazoic Assignment - Design Explanation

## 1. Problem

The problem is tool overload.

With only a few tools, an LLM can normally select the required tool. With hundreds or thousands of tools, the number of choices becomes large and the model can select the wrong tool or create incorrect parameters.

The solution is to put a tool search layer before the agent.

Instead of:

1000 tools -> LLM

I use:

1000 tools -> Tool Search -> top relevant tools -> LLM

This keeps the LLM focused.

---

## 2. Architecture

User
 |
 v
Router
 |
 +--------------------+----------------------+
 |                    |                      |
 v                    v                      v
RAG Tool        System Search Tool       Tool Search
                                          |
                                          v
                                  Relevant Tools
                                          |
                                          v
                                       Agent
                                          |
                                          v
                                  Validate Parameters
                                          |
                                          v
                                    Tool Executor
                                          |
                                          v
                                  PayPal / Other APIs
                                          |
                                          v
                                      State Store
                                          |
                                          v
                                       User

---

## 3. Tool Registry

All available tools are stored in one registry.

Each tool has:

- name
- description
- category
- required parameters

Example:

create_invoice
send_invoice
get_sales_report
get_dispute

The registry currently has 23 tools across 7 categories (invoice,
payment, dispute, report, payout, subscription, account) instead of
just the 4 used in the assignment's example scenarios. The extra
tools are there so that tool search and the top-K cutoff
(`MAX_TOOLS_FOR_AGENT`) are actually being exercised, not just
described. Most of them are mocked with a generic simulated response
in `tools.py` rather than custom logic, since the point at this stage
is to show the routing holds up, not to hand-write 20+ fake API
integrations.

In a small demo the registry is a Python list.

In a large system it can be stored in a database or a service.

---

## 4. Tool Selection and Routing

The first step is routing.

Example:

"Send an invoice for $50"

The router identifies this as an action request.

The tool search looks for invoice-related tools.

Only a few relevant tools are passed to the agent.

This is important because the LLM should not receive all 500 or 1000 tools.

For this fresher implementation, tool search uses simple keyword/category matching.

For production, I would use embeddings and vector search because it works better when the user's wording is different from the tool description.

Example:

User: "I need to bill a customer"

The search should still find:

create_invoice
send_invoice

I also added a small stopword list (words like "the", "a", "is") to the
keyword matcher. Without it, common words in the request start matching
almost every tool description once the registry grows past a handful of
tools, and the top-K list stops being useful. This is a cheap fix for a
keyword-based search. It does not remove the need for embeddings once
the registry is large (see section 13), it just keeps the demo honest
at the size it is currently at (23 tools, several services).

---

## 5. Agent

The agent receives:

- user request
- relevant tools (the narrowed list from tool search, not the full registry)
- current state

It decides which tool should be used.

For example:

User:
"Is there a dispute open from user_123?"

Agent:
get_dispute

Parameters:
user_id = user_123

### How tool selection actually happens

`agent.py` first tries to call the model (see `llm_client.py`). The
narrowed tool list from tool search is turned into Claude tool
definitions, and the model is forced to pick one (`tool_choice: "any"`)
and fill in its parameters. This is the real version of the decision
described above, and it is what makes the tool-search step worthwhile:
the model only ever sees the 5 tools that search_tools() returned, not
the whole registry, so raising the registry from 4 tools to 500 does
not change how much the model has to read per request.

If `ANTHROPIC_API_KEY` is not set, or the `anthropic` package is not
installed, `agent.py` falls back to a small set of keyword rules
(`choose_tool_fallback` / `build_parameters_fallback`). This is the
same idea as the very first version of this file, kept intentionally
so the project can be run, read and tested with no external
credentials. In a real deployment this fallback would not exist; it is
here for the assignment reviewer's convenience.

Either path ends up at the same place: a `tool_name` and a
`parameters` dict, which then go through parameter validation before
anything is executed.

---

## 6. Parameter Validation

I do not directly execute an LLM-generated tool call.

The parameters are checked first.

For example, get_dispute requires user_id.

create_invoice requires:

- customer
- amount

If required information is missing, the system should not make the API call.

In a real system, JSON schema validation would be used.

---

## 7. Tool Execution

The executor is separate from the agent.

The agent decides WHAT to call.

The executor decides HOW to call it.

This separation makes the system easier to maintain.

For the assignment, the PayPal API calls are mocked.

In production they would be replaced with actual HTTP/API clients.

---

## 8. Multi-Step Tasks

Some user requests need more than one API.

Example:

"Create an invoice and send it."

Flow:

create_invoice
     |
     v
invoice_id
     |
     v
send_invoice
     |
     v
success

The result from the first call becomes input to the next call.

This is one reason state is important.

### How this is actually implemented

`agent.py` has a small `CHAIN_RULES` table that maps a tool to a
possible next tool, along with the trigger words that mean the user
wants that next step too (e.g. `create_invoice` -> `send_invoice`,
triggered by the word "send"). After a tool runs successfully,
`maybe_chain()` checks this table. If it applies, the result of the
first call is inspected for fields the next call needs (here,
`invoice_id`), those are merged into the next call's parameters, and
the next tool runs the same way the first one did: validate, execute,
update state.

This loop is capped by `MAX_CHAIN_STEPS` in `config.py` so a bad rule
can't chain forever. It is deliberately a lookup table rather than
letting the model decide an open-ended sequence of tool calls by
itself. A lookup table is predictable and easy to unit test
(`tests/test_chain.py`), and it is enough for the two- or three-step
flows this system needs. If the number of realistic multi-step flows
grew a lot, I would move this into the LLM call itself (an agent loop
where the model sees the result of each tool call and decides whether
to call another one), which is closer to how LangGraph represents
this kind of flow as an explicit graph with conditional edges.

---

## 9. State Management

The system stores simple state:

- last request
- last selected tool
- last result

Example:

state = {
    "last_request": "...",
    "last_tool": "get_dispute",
    "last_result": "No open dispute"
}

For a real application, I would use Redis or a database so state is available across requests and multiple servers.

---

## 10. RAG Tool

RAG is kept separate from API actions.

The RAG tool is useful for questions about documentation.

Example:

"How do I create an invoice?"

The RAG tool searches the knowledge base and returns relevant documentation.

Production flow:

Question
 -> Embedding
 -> Vector database
 -> Relevant documents
 -> LLM
 -> Answer

The demo uses a small local knowledge base so it is easy to run.

---

## 11. System Search Tool

System Search is different from RAG.

RAG searches business/product documentation.

System Search searches the agent system itself.

Examples:

"What tools are available for managing invoices?"

"What is the status of my last request?"

It can search tool metadata, request history and system logs.

---

## 12. Error Handling

Possible failures:

1. Tool not found
2. Missing parameter
3. Invalid parameter
4. API failure
5. Temporary network problem

The system handles these before returning a response.

For temporary failures, a small retry count can be used.

I would not retry forever.

One more case worth naming: the LLM call itself can fail or time out
(rate limit, network issue, malformed tool call). `llm_client.py`
already treats "no usable tool call came back" as a signal to fall
back to the keyword rules rather than crashing the request. In
production I would separate those two cases more explicitly (a
genuine API error should probably retry or alert, not silently fall
back), but for this assignment keeping one fallback path was simpler
and still demonstrates the idea: the agent should degrade gracefully
rather than leave the user with no answer.

---

## 13. Scalability

The most important scalability decision is tool retrieval.

For 50 tools:

simple search is enough for a demo.

For 500+ tools:

tool metadata can be indexed.

For thousands of tools:

Use:

tool descriptions
 -> embeddings
 -> vector database
 -> top K search
 -> agent

The LLM still receives only a small set of relevant tools.

This reduces prompt size and tool-selection confusion.

---

## 14. Framework Choice

For the workflow, I would choose LangGraph.

Why?

- It is suitable for multi-step agent workflows.
- State can be represented clearly.
- Conditional routing is easy to understand.
- Tool execution and retries can be represented as workflow steps.

I would not combine many frameworks unnecessarily.

A simple production stack could be:

LangGraph
+ Python
+ Vector database
+ Redis/database
+ LangSmith

---

## 15. Why not use every framework?

### LangChain

Good for LLM and tool integrations.

Trade-off:
It can become abstract when the workflow becomes large.

### LangGraph

Good for explicit agent workflows and state.

Trade-off:
There is a little more setup than a simple single-agent program.

### LlamaIndex

Good for RAG and document retrieval.

Trade-off:
The main problem in this assignment is tool routing, not only document retrieval.

### CrewAI

Good for multiple specialized agents.

Trade-off:
This assignment does not require many independent agents, so it can add unnecessary complexity.

### DSPy

Good for systematic prompt/program optimization.

Trade-off:
It is not necessary for the basic routing architecture.

For this task, I would keep the core workflow simple and use LangGraph when moving the prototype to production.

---

## 16. Observability

I would use LangSmith or a similar tracing system in production.

Useful information to record:

- user request
- selected tools
- parameters
- tool execution time
- success/failure
- retry count
- final response

This helps find why the agent selected the wrong tool.

---

## 17. Security

API credentials should not be placed inside prompts or source code.

They should be stored in environment variables or a secrets manager.

The system should also:

- validate inputs
- limit tool permissions
- log important actions
- prevent unauthorized tools from being called

---

## 18. Final Flow

User
 |
 v
Router
 |
 +--> RAG Tool
 |
 +--> System Search
 |
 +--> Tool Search
          |
          v
     Top relevant tools
          |
          v
        Agent
          |
          v
   Parameter validation
          |
          v
    Tool execution
          |
          v
       State
          |
          v
       Response

The key idea is simple:

DO NOT SEND ALL TOOLS TO THE LLM.

FIRST FIND THE RELEVANT TOOLS.

THEN LET THE AGENT CHOOSE FROM THE SMALL SET.

This allows the same architecture to grow from 50 tools to hundreds or thousands of tools.
