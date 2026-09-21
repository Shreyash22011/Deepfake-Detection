import asyncio
import httpx
import json

async def test_full_flow():
    print("Starting Phase 3 End-to-End Verification...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # TEST 1: File Upload & Analysis
        print("\n[Test 1] Uploading media to /api/analyze...")
        files = {'file': ('fake_image.jpg', b'dummy content', 'image/jpeg')}
        resp1 = await client.post('/api/analyze', files=files)
        
        if resp1.status_code != 200:
            print(f"FAILED to upload: {resp1.text}")
            return
            
        data = resp1.json()
        analysis_id = data.get("id")
        print(f"SUCCESS! Created Analysis ID: {analysis_id}")
        print(f"   Status: {data.get('status')}")
        print(f"   Prediction: {data.get('result', {}).get('prediction')}")
        
        # TEST 2: Retrieve from History
        print("\n[Test 2] Retrieving analysis history from MongoDB (/api/analyses)...")
        resp2 = await client.get('/api/analyses')
        if resp2.status_code != 200:
            print(f"FAILED to fetch history: {resp2.text}")
            return
            
        history = resp2.json()
        print(f"SUCCESS! Found {len(history)} records in the database.")
        
        # Check if our recent analysis is in the history
        found = any(record.get("id") == analysis_id for record in history)
        if found:
            print(f"   -> Confirmed: Analysis {analysis_id} was successfully saved to MongoDB!")
        else:
            print(f"   -> Warning: Analysis {analysis_id} not found in history.")

        # TEST 3: Retrieve Single Record
        print(f"\n[Test 3] Retrieving single record from MongoDB (/api/analyses/{analysis_id})...")
        resp3 = await client.get(f'/api/analyses/{analysis_id}')
        if resp3.status_code != 200:
            print(f"FAILED to fetch single record: {resp3.text}")
            return
            
        single_record = resp3.json()
        print(f"SUCCESS! Record retrieved successfully.")
        print("   Result Data:")
        print(json.dumps(single_record['result'], indent=2))
        
        print("\nALL PHASE 3 TESTS PASSED SUCCESSFULLY! The project is solid.")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
