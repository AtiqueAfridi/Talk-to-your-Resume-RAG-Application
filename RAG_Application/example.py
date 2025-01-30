from rag_system import RAGSystem

def main():
    # Initialize the RAG system with your corpus
    rag = RAGSystem('corpus.txt')
    
    # Example queries
    queries = [
        "What is machine learning?",
        "How does neural networks work?",
        "What are the applications of AI?"
    ]
    
    # Process queries
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        answer, passages = rag.query(query)
        
        print("Generated Answer:")
        print(answer)
        print("\nRetrieved Passages:")
        for i, (passage, score) in enumerate(passages, 1):
            print(f"\n{i}. (Score: {score:.4f})")
            print(passage)

if __name__ == "__main__":
    main()