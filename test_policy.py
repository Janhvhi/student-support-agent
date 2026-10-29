
from policy_search import search_policy


def main():
    question = "What should I do if my fees are pending?"

    print(f"Question: {question}")
    results = search_policy(question)

    print("\nRetrieved policy sections:")

    if not results:
        print("No relevant policy sections found.")
        return

    for index, result in enumerate(results, start=1):
        if isinstance(result, dict):
            text = result.get("text", "")
            chunk_id = result.get("chunk_id", index)
        else:
            text = str(result)
            chunk_id = index

        print(f"\nSection {chunk_id}:")
        print(text)

    print("\nPolicy retrieval check completed.")


if __name__ == "__main__":
    main()
