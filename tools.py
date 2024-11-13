tools = [
    {
        "type": "function",
        "function": {
            "name": "query_similar_texts",
            "description": "Query similar texts from the vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "The query to search for similar texts in vector database."
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "The number of similar texts to return."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rewrite_question",
            "description": "Rewrite the question to improve its clarity and suitability for web search or retrieval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to rewrite."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grade_document",
            "description": "Grade the document based on the question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document": {
                        "type": "string",
                        "description": "The document to grade."
                    },
                    "question": {
                        "type": "string",
                        "description": "The question to grade the document."
                    }
                }
            }
        }
    }
]