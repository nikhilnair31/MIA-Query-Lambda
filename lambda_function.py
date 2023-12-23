# region Imports
import os
import json
import logging
import pinecone
from openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
# endregion

# region Vars & Initialization
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)
embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pinecone_env_key = os.environ.get('PINECONE_ENV_KEY')
pinecone_index_name = os.environ.get('PINECONE_INDEX_NAME')
pinecone.init(api_key=pinecone_api_key, environment=pinecone_env_key)
index = pinecone.Index(pinecone_index_name)
# endregion

def query(text, showLog = False):
    top_k = 3
    query_embedding = embeddings_model.embed_documents([text])[0]
    query_result = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    if showLog:
        print(f"Query Results: {query_result}\n")
        print(f"{'*'*50}\n")

        print(f"Query Results\n")
        for match in query_result['matches']:
            print(f"ID: {match['id']}\nScore: {match['score']}\nMetadata: {match.get('metadata', {})}\n")
        print(f"{'*'*50}\n")
    
    return query_result

def gpt(query_text, query_result, modelName = "gpt-4-1106-preview", seed = 48, length = 1024, temp = 0.0):
    system_prompt = f"""
        You are the user's companion. Help them using the context provided from metadata text. 
        Do not make up any information, admit if you don't know something. 
        Context:
    """
    response = openai_client.chat.completions.create(
        model=modelName,
        seed=seed,
        max_tokens=length,
        temperature=temp,
        messages=[
            {"role": "system", "content": f'{system_prompt} {query_result}'},
            {"role": "user", "content": query_text},
        ],
    )
    res = response.choices[0].message.content
    
    print(f"\n{'*'*50}")
    print(f"Response\n{res}")
    print(f"{'*'*50}\n")

    return res

def handler(event, context):
    try:
        logger.info(f'Started lambda_handler\n')

        logger.info(f'Event: {event}\n')
        if 'body' in event:
            body = json.loads(event['body'])
            input_text = body.get('input_text', 'Default input text if not provided')
            show_log = str(body.get('show_log', False)).lower() == 'true'
        else:
            input_text = 'Default input text if not provided'
            show_log = False
        logger.info(f"Input Text: {input_text}\n")

        query_result = query(text=input_text, showLog = show_log)
        gpt_output = gpt(
            query_text=input_text, 
            query_result=query_result, 
            modelName="gpt-4-1106-preview", 
            seed=48, 
            length=1024, 
            temp=0.0
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing complete', 'gpt_output': gpt_output})
        }

    except Exception as e:
        logger.error(f'Error: \n{e}\n\n')
        logger.error("Stack Trace:", exc_info=True)

        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

if __name__ == '__main__':
    # Dummy context
    test_context = None
    # Dummy event with input text
    test_event = {
        'show_log': "True",
        'input_text': "I remember hearing something about a forklift."
    }

    # Call the lambda handler
    response = handler(test_event, test_context)
    print(response)