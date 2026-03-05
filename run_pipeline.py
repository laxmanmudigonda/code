from pipeline.quote_pipeline import QuotePipeline

pipeline = QuotePipeline()

sample_quote = {
    "quote_id": "Q001",
    "Risk_Tier": 1,
    "Re_Quote": 0,
    "Q_Valid_DT": 5,
    "HH_Drivers": 2,
    "Coverage": "Comprehensive",
    "Agent_Type": "EA",
    "Region": "West",
    "Sal_Range": "80-120k",
    "Quoted_Premium": 700
}

result = pipeline.process_quote(sample_quote)

print("\nFINAL PIPELINE RESULT")
print(result)