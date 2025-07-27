#!/usr/bin/env python3
"""
Standalone RAG System Tester
Run this to test if the RAG system works independently of the API
"""

import sys
import os

def test_rag_standalone():
    """Test the RAG system standalone"""
    print("🧪 Testing RAG System Standalone")
    print("=" * 50)
    
    try:
        # Import and test the RAG system
        print("📦 Importing RAG module...")
        from rag import rag_chat, initialize_rag_system
        
        print("🚀 Initializing RAG system...")
        if initialize_rag_system():
            print("✅ RAG system initialized successfully!")
            
            # Test with a sample question
            test_question = "What is AI governance?"
            print(f"\n🔍 Testing with question: '{test_question}'")
            
            response = rag_chat(test_question)
            
            print(f"\n📝 Response:")
            print("-" * 30)
            print(response)
            print("-" * 30)
            
            print("\n✅ RAG system test completed successfully!")
            return True
        else:
            print("❌ Failed to initialize RAG system")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'torch',
        'transformers',
        'langchain',
        'chromadb',
        'sentence_transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True

def check_chroma_db():
    """Check if ChromaDB exists"""
    print("\n🔍 Checking ChromaDB...")
    
    if os.path.exists("chroma_db"):
        print("✅ ChromaDB directory found")
        
        # Check for some expected files
        db_files = os.listdir("chroma_db")
        if db_files:
            print(f"✅ ChromaDB contains {len(db_files)} files/directories")
            return True
        else:
            print("⚠️  ChromaDB directory is empty")
            return False
    else:
        print("❌ ChromaDB directory not found!")
        print("Please make sure 'chroma_db' directory exists in the current directory")
        return False

def main():
    """Main function"""
    print("🎯 RAG System Standalone Test")
    print("=" * 50)
    
    # Check environment
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Run checks
    if not check_dependencies():
        return False
    
    if not check_chroma_db():
        return False
    
    # Test RAG system
    return test_rag_standalone()

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 All tests passed! RAG system is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Please check the errors above.")
        sys.exit(1)
