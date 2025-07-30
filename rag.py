from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.llms import HuggingFacePipeline

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from transformers import pipeline
import torch
import os
from together import Together

# Set your Hugging Face token directly here (REPLACE WITH YOUR ACTUAL TOKEN)
from huggingface_hub import login
os.environ["HUGGINGFACE_API_TOKEN"] = "Token_Here"
login(token=os.environ["HUGGINGFACE_API_TOKEN"])
# os.environ["TOGETHER_API_KEY"] = "Token_Here"

# Global variables to store initialized components
embedding_model = None
vectorstore = None
retriever = None
llm = None
rag_chain = None
chat_history = []

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

'''def initialize_llm():
    """Initialize the Language Model"""
    global llm
    print("🔄 Loading language model...")
    print("⚠️  This may take several minutes on first run...")
    
    # Use TinyLlama for faster testing, can be changed to Llama-2-7b later
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Alternative: "meta-llama/Llama-2-7b-chat-hf"
    print(f"📦 Using model: {model_name}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,  # Increased for more creative responses
            repetition_penalty=1.1,  # Reduce repetition
            pad_token_id=tokenizer.eos_token_id
        )
        
        llm = HuggingFacePipeline(pipeline=pipe)
        print(f"✅ Language model loaded successfully")
        return llm
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        raise'''
        
def initialize_llm():
        """Initialize the Together AI hosted LLaMA 3.3 70B model"""
        global llm
        print("🔄 Loading Together AI model (via API)...")
        print("⚠️  Requires internet access and a Together API key.")

        try:
            # Set your Together API key
            TOGETHER_API_KEY = "Token_Here"
            client = Together(api_key=TOGETHER_API_KEY)

            # Model name hosted on Together
            model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
            print(f"📦 Using Together AI model: {model_name}")

            # Define and assign the LLM function globally
            def _llm(messages):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=512,
                    top_p=0.9
                )
                return response.choices[0].message.content.strip()
            '''def _llm(prompt, system_message="You are a helpful assistant."):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=512,
                    top_p=0.9
                )
                return response.choices[0].message.content.strip()'''

            # Set the global llm to the defined function
            llm = _llm
            globals()["llm"] = llm

        except Exception as e:
            print(f"❌ Error initializing Together AI model: {e}")
            print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
            raise

def create_rag_chain():
    """Create the RAG chain"""
    global rag_chain, prompt
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
    
    def build_messages(context, question):
        return [
            {"role": "system", "content": """You are an AI-powered policy assistant specialized in AI and Data Governance.
Your role is to support users by interpreting and explaining governance frameworks, ethical standards, compliance guidelines, and policy definitions.

Instructions:
1. Base your answer only on the provided context.
2. List the filenames of the documents you used (e.g., 'AI_Principles Document') under the "Sources" section.
3. If the context does not contain the answer, respond with exactly: "I don't know."
4. Do not make assumptions or add any information not explicitly stated in the context.

Question: {question}

Context: {context}

Answer:"""},
            *chat_history,  # ← this will hold prior conversation turns
            {"role": "user", "content": f"{question}\n\nContext:\n{context}"}
        ]

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | RunnableLambda(lambda inputs: llm(build_messages(inputs["context"], inputs["question"])))
        | StrOutputParser()
    ) 
    
    
    #llm_chain = prompt | llm | StrOutputParser()
    '''llm_chain = (
    prompt
    | RunnableLambda(lambda prompt_str: llm(prompt_str))
    | StrOutputParser()
    )'''
    '''# history = {"question": , history: }
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | RunnableLambda(lambda inputs: llm(
            prompt.format(context=inputs["context"], question=inputs["question"])
        ))
        | StrOutputParser()
    )'''
    
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
        print(f"📊 RAG chain initialized: {rag_chain is not None}")
        print(f"📊 Retriever initialized: {retriever is not None}")
        print(f"📊 LLM initialized: {llm is not None}")
        
        # Invoke the RAG chain
        print("🔄 Invoking RAG chain...")
        response = rag_chain.invoke(input=user_message)
        
        print(f"✅ Response generated successfully")
        print(f"📏 Response length: {len(response) if response else 0} characters")
        print(f"🔍 Response preview: {response[:100] if response else 'None'}...")
        
        if not response or response.strip() == "":
            return "I apologize, but I couldn't generate a response to your question. Please try rephrasing your question or try again."
        
        return response
        
    except Exception as e:
        print(f"❌ Error in rag_chat: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        print(f"📊 Stack trace: {str(e)}")
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