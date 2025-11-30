from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as question_router

app = FastAPI(title="AI Assistant", description="AI Assistant Chatbot")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# middleware exception handlers
app.middleware("http")(catch_exception_middleware)

# routers

# route 1 - upload pdf documents 
app.include_router(upload_router)

# route 2 - asking query
app.include_router(question_router)
