from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import sys
import os
import numpy as np
import traceback

# Add the parent directory to path so we can import the pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.quote_pipeline import QuotePipeline

app = FastAPI(
    title="QuoteIQ Insurance API",
    description="Multi-Agent Insurance Quote Analysis System",
    version="1.0"
)

# Function to convert numpy types to Python native types
def clean_numpy(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types."""
    if isinstance(obj, dict):
        return {key: clean_numpy(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_numpy(item) for item in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

# Initialize pipeline once at startup
pipeline = QuotePipeline()

class QuoteInput(BaseModel):
    quote_id: Optional[str] = "Q1001"
    HH_Vehicles: int
    HH_Drivers: int
    Driver_Age: int
    Driving_Exp: int
    Prev_Accidents: int
    Prev_Citations: int
    Annual_Miles_Mid: int
    Vehicle_Cost_Mid: int
    Salary_Mid: int
    Coverage: str
    Agent_Type: str
    Region: str
    Sal_Range: str
    Re_Quote: int
    Quoted_Premium: float
    Q_Valid_DT: int

@app.get("/")
def home():
    return {"message": "QuoteIQ API running"}

@app.post("/analyze")
def analyze_quote(quote: QuoteInput):
    try:
        quote_dict = quote.dict()
        print(f"Received quote: {quote_dict}")
        
        result = pipeline.run(quote_dict)
        print(f"Pipeline result: {result}")
        
        # Clean numpy values before returning
        cleaned_result = clean_numpy(result)
        return cleaned_result
    except Exception as e:
        print(f"Error in analyze_quote: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))