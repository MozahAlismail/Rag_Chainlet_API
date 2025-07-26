import os
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import HuggingFaceEndpoint
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Initialize embeddings (lightweight model)
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

# Load local Chroma DB
vectorstore = Chroma(
    persist_directory="chroma_db",  # path to your saved local DB
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Use Hugging Face Inference API instead of loading model locally
# This significantly reduces memory usage and deployment size
huggingface_api_token = os.getenv("HUGGINGFACE_API_TOKEN")

if huggingface_api_token:
    # Use Hugging Face Inference API (much smaller footprint)
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-2-7b-chat-hf",
        huggingfacehub_api_token=huggingface_api_token,
        model_kwargs={
            "temperature": 0.3,
            "max_new_tokens": 512,
            "do_sample": True,
        }
    )
else:
    # Load Llama-2-7b locally if no API token is provided
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    from langchain.llms import HuggingFacePipeline
    import torch
    
    print("HUGGINGFACE_API_TOKEN not found. Loading Llama-2-7b locally...")
    
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
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
        pad_token_id=tokenizer.eos_token_id
    )
    
    llm = HuggingFacePipeline(pipeline=pipe)

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

def rag_chat(user_message: str) -> str:
    try:
        response = rag_chain.invoke(input=user_message)
        return response
    except Exception as e:
        print(f"Error in RAG processing: {e}")
        return "Sorry, I encountered an error while processing your request. Please try again."
