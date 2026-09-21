import asyncio
from app.schemas.analysis import AnalysisRecord, AnalysisStatus
from app.core.database import connect_to_mongo, close_mongo_connection, get_db

async def test():
    await connect_to_mongo()
    db = get_db()
    record = AnalysisRecord(
        id="test-id",
        filename="test.mp4",
        media_type="video",
        status=AnalysisStatus.processing
    )
    try:
        await db.analyses.insert_one(record.model_dump())
        print("Insert successful!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test())
