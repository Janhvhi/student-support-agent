
from policy_search import search_policy

question = "What should I do if my fees are pending?"
result = search_policy(question)

print("Question:", question)
print("\nRetrieved policy sections:")

if "error" in result:
    print(result["error"])
elif result["results"]:
    for item in result["results"]:
        print("\nScore:", item["score"])
        print(item["text"])
else:
    print("No matching policy information found.")
