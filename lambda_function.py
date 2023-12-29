# region Imports
import os
import json
import logging
import pinecone
from datetime import datetime
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
# endregion

# region Vars & Initialization
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

openai_api_key = os.environ.get('OPENAI_API_KEY')
embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pinecone_env_key = os.environ.get('PINECONE_ENV_KEY')
pinecone_index_name = os.environ.get('PINECONE_INDEX_NAME')
pinecone.init(api_key=pinecone_api_key, environment=pinecone_env_key)
index = pinecone.Index(pinecone_index_name)
# endregion

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

def query(text, filter_dict, top_k = 3, showLog = False):
    query_embedding = embeddings_model.embed_documents([text])[0]
    query_result = index.query(
        vector = query_embedding, 
        top_k = top_k, 
        include_metadata = True,
        filter = filter_dict
    )

    serializable_result = [{
        'id': match['id'],
        'score': match['score'],
        'metadata': {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in match.get('metadata', {}).items()
        }
    } for match in query_result['matches']]

    if showLog:
        print(f"Query Results: {query_result}\n")
        print(f"{'*'*50}\n")
    
    return serializable_result

def handler(event, context):
    try:
        logger.info(f'Started lambda_handler\n')

        logger.info(f'Event: {event}\n')
        
        # Check if the event body is a string and parse it if so, otherwise use it directly
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']

        query_text = body.get('query_text', 'Default input text if not provided')
        query_filter = body.get('query_filter', {})
        query_top_k = int(body.get('query_top_k', 3))
        show_log = str(body.get('show_log', False)).lower() == 'true'

        logger.info(f"Query Text: {query_text}\n")
        logger.info(f"Query Filter: {query_filter}\n")
        logger.info(f"Query Top K: {query_top_k}\n")
        logger.info(f"Show Log: {show_log}\n")

        query_result = query(
            text = query_text,
            filter_dict=query_filter,
            top_k = query_top_k,
            showLog = show_log
        )

        return {
            'statusCode': 200,
            'body': json.dumps(
                {
                    'message': 'Processing complete', 
                    'output': query_result
                }, 
                default=datetime_converter
            )
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
        'body': {
            'query_text': "ice cream",
            'query_filter': {
                "source": "recording"
            },
            'query_top_k': "3",
            'show_log': "True",
        }
    }

    # Call the lambda handler
    response = handler(test_event, test_context)
    print(response)