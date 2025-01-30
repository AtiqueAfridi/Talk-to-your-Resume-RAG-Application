import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import textwrap
from typing import List, Tuple

class RAGSystem:
    def __init__(self, corpus_path: str):
        """
        Initialize the RAG system with a corpus file path.
        
        Args:
            corpus_path (str): Path to the text corpus file
        """
        # Load models
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.generator = AutoModelForCausalLM.from_pretrained('distilgpt2')
        self.tokenizer = AutoTokenizer.from_pretrained('distilgpt2')
        
        # Load and process corpus
        self.passages = self._load_corpus(corpus_path)
        self.passage_embeddings = None
        self.index = None
        self._build_index()

    def _load_corpus(self, corpus_path: str) -> List[str]:
        """
        Load and preprocess the text corpus.
        
        Args:
            corpus_path (str): Path to the corpus file
            
        Returns:
            List[str]: List of text passages
        """
        with open(corpus_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Split into passages (here using paragraphs)
        passages = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Clean and preprocess passages
        passages = [' '.join(p.split()) for p in passages]
        return passages

    def _build_index(self):
        """Build FAISS index for the corpus passages."""
        # Generate embeddings for all passages
        self.passage_embeddings = self.encoder.encode(self.passages)
        
        # Initialize FAISS index
        dimension = self.passage_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to index
        self.index.add(np.array(self.passage_embeddings).astype('float32'))

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Retrieve the k most relevant passages for a query.
        
        Args:
            query (str): The query text
            k (int): Number of passages to retrieve
            
        Returns:
            List[Tuple[str, float]]: List of (passage, score) tuples
        """
        # Encode query
        query_embedding = self.encoder.encode([query])
        
        # Search in FAISS index
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        # Return passages and their distances
        results = [(self.passages[idx], dist) for idx, dist in zip(indices[0], distances[0])]
        return results

    def generate_answer(self, query: str, retrieved_passages: List[Tuple[str, float]]) -> str:
        """
        Generate an answer based on retrieved passages.

        Args:
            query (str): The original query
            retrieved_passages (List[Tuple[str, float]]): List of (passage, score) tuples

        Returns:
            str: Generated answer
        """
        # Limit context length dynamically (prevent token overflow)
        context = " ".join([p[0] for p in retrieved_passages])[:1000]  # Approx. 1000 chars
        
        # Construct prompt
        prompt = (
            f"Given the following resume data, answer the question concisely.\n\n"
            f"Resume Data:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Provide a well-structured answer:"
        )


        # Tokenize with truncation
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)

        # Generate response
        with torch.no_grad():
            outputs = self.generator.generate(
                inputs.input_ids,
                max_new_tokens=150,  # Generate up to 150 tokens without truncating input
                num_return_sequences=1,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode output
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove prompt from response (avoid duplicate text)
        answer = answer.replace(prompt, "").strip()

        return answer


    def query(self, query: str, k: int = 3) -> Tuple[str, List[Tuple[str, float]]]:
        """
        Process a query through the full RAG pipeline.
        
        Args:
            query (str): The query text
            k (int): Number of passages to retrieve
            
        Returns:
            Tuple[str, List[Tuple[str, float]]]: Generated answer and retrieved passages
        """
        retrieved_passages = self.retrieve(query, k)
        answer = self.generate_answer(query, retrieved_passages)
        return answer, retrieved_passages