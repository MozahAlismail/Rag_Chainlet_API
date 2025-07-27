from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.llms import HuggingFacePipeline

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from transformers import pipeline
import torch
import os

# Global variables to store initialized components
embedding_model = None
vectorstore = None
retriever = None
llm = None
rag_chain = None

def initialize_embeddings():
    """Initialize the embedding model"""
    global embedding_model
    print("🔄 Initializing embeddings...")
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    print("✅ Embeddings initialized successfully")
    return embedding_model

def initialize_vectorstore():
    """Initialize the vector database"""
    global vectorstore, retriever
    print("🔄 Loading ChromaDB...")
    
    if not os.path.exists("chroma_db"):
        raise FileNotFoundError("ChromaDB directory 'chroma_db' not found!")
    
    vectorstore = Chroma(
        persist_directory="chroma_db",  # path to your saved local DB
        embedding_function=embedding_model
    )
    
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    print("✅ ChromaDB loaded successfully")
    return vectorstore, retriever

def initialize_llm():
    """Initialize the Language Model"""
    global llm
    print("🔄 Loading Llama-2-7b model...")
    print("⚠️  This may take several minutes on first run...")
    
    model_name = "mistralai/Mistral-7B-Instruct-v0.1" # meta-llama/Llama-2-7b-chat-hf
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.3,
        )
        
        llm = HuggingFacePipeline(pipeline=pipe)
        print("✅ Llama-2-7b model loaded successfully")
        return llm
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise

def create_rag_chain():
    """Create the RAG chain"""
    global rag_chain
    print("🔄 Creating RAG chain...")
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an AI-powered policy assistant specialized in AI and Data Governance.
Your role is to support users by interpreting and explaining governance frameworks, ethical standards, compliance guidelines, and policy definitions.

Instructions:
1. Base your answer only on the provided context.
2. List the filenames of the documents you used (e.g., 'AI_Principles Document') under the "Sources" section.
3. If the context does not contain the answer, respond with exactly: "I don't know."
4. Do not make assumptions or add any information not explicitly stated in the context.

Question: {question}

Context: {context}

Answer:
"""
    )
    
    llm_chain = prompt | llm | StrOutputParser()
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | llm_chain
    )
    
    print("✅ RAG chain created successfully")
    return rag_chain

def initialize_rag_system():
    """Initialize the entire RAG system"""
    print("🚀 Initializing RAG System...")
    print("=" * 50)
    
    try:
        # Initialize components in order
        initialize_embeddings()
        initialize_vectorstore()
        initialize_llm()
        create_rag_chain()
        
        print("=" * 50)
        print("✅ RAG System initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        print("=" * 50)
        return False

def rag_chat(user_message: str) -> str:
    """
    Main function to handle RAG chat requests
    
    Args:
        user_message (str): The user's question
        
    Returns:
        str: The generated response
    """
    try:
        if rag_chain is None:
            return "❌ Error: RAG system not initialized. Please restart the server."
        
        print(f"🔍 Processing question: {user_message}")
        response = rag_chain.invoke(input=user_message)
        print(f"✅ Response generated successfully")
        
        return response
        
    except Exception as e:
        print(f"❌ Error in rag_chat: {e}")
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

def test_rag_system():
    """Test the RAG system with a sample question"""
    print("\n🧪 Testing RAG system...")
    test_question = "What is AI governance?"
    response = rag_chat(test_question)
    print(f"Test Question: {test_question}")
    print(f"Response: {response[:200]}...")
    return response

def main():
    """Main function to initialize and test the RAG system"""
    print("🎯 Starting RAG System Setup...")
    
    # Initialize the RAG system
    if initialize_rag_system():
        # Test the system
        test_rag_system()
        print("\n🎉 RAG system is ready for use!")
    else:
        print("\n💥 Failed to initialize RAG system!")
        return False
    
    return True

if __name__ == "__main__":
    main()