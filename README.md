# Model
A vErY nIcE rAG aRcHiTeCtUrE mOdEl

## Setup

First, you must install some packages.

```bash
pip install -r requirements.txt
```

## Running the API

Once you have the project set up, you can start the FastAPI server by running the following command:

```bash
uvicorn chatbot_api:app --reload
```

This will start the server and the API will be available at `http://127.0.0.1:8000`.

### API Endpoints

- **POST /query**: This endpoint accepts a user query and returns a response from the chatbot.

    **Request:**
    - `POST http://127.0.0.1:8000/query`
    - Body (JSON):
    
    ```json
    {
      "query": "What is the capital of Vietnam?"
    }
    ```

    **Response:**
    
    ```json
    {
      "response": "The capital of Vietnam is Hanoi."
    }
    ```

    **Parameters:**
    - `query`: The user's query as a string.

## Stopping the Server

To stop the server, press `Ctrl+C` in the terminal.

## Troubleshooting

- **Missing Environment Variables**: Make sure that the `.env` file exists and contains all the required environment variables.
- **Port Conflicts**: If port `8000` is already in use, you can change the port by running the command with the `--port` option:
  
  ```bash
  uvicorn chatbot_api:app --reload --port 8080
  ```
