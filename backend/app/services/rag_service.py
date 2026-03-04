from ..services.rag_store import retrieve_context

def rag_validate(discrepancy, faiss_index, docs):
    query = f"""
    Is this discrepancy allowed?
    Item: {discrepancy['item']}
    Type: {discrepancy['type']}
    """

    context = retrieve_context(query, faiss_index, docs)

    return context
