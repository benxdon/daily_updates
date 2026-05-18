from mcp.server.fastmcp import FastMCP
import chromadb
from datetime import datetime, timedelta

mcp = FastMCP("email_search")

chroma_client = chromadb.PersistentClient(path="data/chroma")
collection = chroma_client.get_collection(name="emails")

@mcp.tool()
def search_emails(query:str, n_results:int=5) -> str:
    """
    find the related emails based on the query

    args: 
        query, the relation information to be found
        n_results, the number of emails being returned 
    output:
        the string of all the related emails
    """
    results = collection.query(
        query_texts = [query],
        n_results = n_results,
        include = ["documents", "metadatas", "distances"]
    )

    output = []

    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        from_address = meta["from"]
        to_address = meta["to"]
        content = [
            f"From: {from_address}\n",
            f"To: {to_address}\n",
            f"Body: {doc}"
        ]
        string = ''.join(content)
        output.append(string)

    return "\n".join(output) if output else "No matching found"

@mcp.tool()
def get_recent_emails(days:int = 1) -> str:
    """
    find all the emails within the last N days
    """
    cutoff = (datetime.now() - timedelta(days=days)).timestamp()
    results = collection.get(
        where={"date":{"$gte":cutoff}} # greater equal than cutoff
    )

    if not results["documents"]:
        return f"No emails were found in the last {days} days"


    output = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][i]
        from_address = meta["from"]
        to_address = meta["to"]
        content = [
            f"From: {from_address}\n",
            f"To: {to_address}\n",
            f"Body: {doc}"
        ]
        string = ''.join(content)
        output.append(string)

    return "\n".join(output)


if __name__ == "__main__":
    res1 = search_emails(query="hsbc")
    res2 = get_recent_emails(40)

    print(res1 + "\n" + res2)
