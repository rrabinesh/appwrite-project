import subprocess, sys
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import secrets
from starlette.responses import RedirectResponse
import uvicorn
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
 
# Initialize FastAPI app
app = FastAPI()
 
# Initialize Appwrite client
client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1") \
      .set_project('666acffd00052f2a4aea') \
      .set_key('d7de8799549d38448340077aff5b41c12e8d79baafc6e9a499703a4753f4211fd9d0e9f17cd5d0e209a511379afd785c575908e350299c017350fe943163186b086c75a5489ea0d2ba5b8062037407e619090bfa674ad51a0caaf734954d0d72f06cfbde6674f866e4478319f484eeee9525418d18cd9a72e7993bb80c455500')
databases = Databases(client)
 
# CORS Configuration
origins = [
      "*"
]
 
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 

class URLData(BaseModel):
    original_url: str
 
class URLResponse(BaseModel):
    original_url: str
    short_url: str

@app.get("/")
async def check():
    return {"message": "success"}
 
@app.post("/shorten", response_model=URLResponse)
async def shorten_url(url_data: URLData):
    try:
        # Generate short code
        short_code = secrets.token_urlsafe(6)
       
        # Construct the short URL
        base_url = "http://127.0.0.1:8000/"
        short_url = f"{base_url}{short_code}"
       
        data = {
            'original_url': str(url_data.original_url),
            'short_code': short_code
        }
        databases.create_document(
            '666ad60e0034e443ce80',  # Replace with your database ID
            'TinyUrl',   # Replace with your collection ID
            document_id='unique()',
            data=data
        )
       
        # Return the response with original_url and short_url
        return URLResponse(original_url=str(url_data.original_url), short_url=short_url)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
 
@app.get("/{short_code}")
async def get_original_url(short_code: str):
    try:
        # Query Appwrite database for the document with given short_code
        response = databases.list_documents('666ad60e0034e443ce80', 'TinyUrl', [
            Query.equal('short_code', short_code)
        ])
 
        if response['documents']:
            document = response['documents'][0]
            original_url = document['original_url']
            return RedirectResponse(url=original_url)
        else:
            raise HTTPException(status_code=404, detail="Short code not found")
 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
 
