# Guidelines and Compliance conversational chatbot 

Welcome to the Legal Document Processing Project! This project leverages various technologies to ingest, process, and analyze legal and regulatory documents, including both PDFs and images. Below you'll find information about the project's tech stack, functionalities, and how to get started.

## Tech Stack ️

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python.
- **SQLite**: A lightweight, serverless, self-contained SQL database engine.
- **ChromaDB**: A database management system optimized for storing and querying embeddings and vectors.
- **LangChain**: A library for natural language processing and text analysis.
- **OpenAI**: Utilized for advanced AI capabilities, such as language modeling and text generation.
- **Brave API**: Provides access to various functionalities and data related to legal and regulatory matters.
- **Google Auth**: Used for authentication and authorization purposes.
- **Python**: The primary programming language used throughout the project.
- **Additional Libraries (For PDF Support)**: You might need additional libraries like PyPDF2 or Camelot for PDF processing and text extraction.

## Functionalities ⚙️

This project offers the following key functionalities:

1. **Document Ingestion**: Capable of ingesting legal and regulatory documents, including both PDFs and images.
2. **OCR and Image Recognition**: Utilizes neural network models to perform Optical Character Recognition (OCR) and image recognition on documents. (Applicable to images)
3. **PDF Text Extraction**: Extracts text content from uploaded PDFs using libraries like PyPDF2 or Camelot.
4. **Legal Document Labeling**: Employs Language Model (LLM) to label documents and convert unstructured data into semi-structured data.
5. **Database Integration**: Integrates with SQLite database to store processed data.
6. **Embedding Generation**: Converts semi-structured data into embeddings and stores them in ChromaDB.
7. **AI-Powered Chat Bot**: Exposes a websocket for interacting with an intelligent AI-powered chat bot specializing in legal and regulatory laws and policies.

## Getting Started 

To get started with the Legal Document Processing Project, follow these steps:

1. Clone the repository: `git clone https://github.com/JeevansSP/ondc-compliance-agent.git`
2. Install the required dependencies (including libraries for PDF support): `pip install -r requirements.txt` (Update requirements.txt to include PDF libraries)
3. Configure your environment variables for authentication (openai and brave api keys).
4. Run the FastAPI server: `uvicorn main:app --reload`

Once the server is up and running, you can start ingesting, processing, and analyzing legal and regulatory documents (PDFs and images) through the provided API endpoints.

## Contributing 

Contributions are welcome! If you'd like to contribute to this project, please fork the repository, make your changes, and submit a pull request. Be sure to follow the project's coding standards and guidelines.

## License 

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to reach out if you have any questions or need further assistance. Happy coding! 
