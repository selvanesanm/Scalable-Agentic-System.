knowledge_base = {
    "invoice": "To create an invoice, the customer and amount are required.",
    "payment": "Payment tools can be used to send and check payments.",
    "dispute": "Dispute tools can be used to check customer disputes."
}


def rag_tool(question):
    question = question.lower()

    for keyword, document in knowledge_base.items():
        if keyword in question:
            return "RAG answer: " + document

    return "RAG answer: No matching document was found."
