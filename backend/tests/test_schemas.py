from app.schemas.analysis import AnalysisResult, AnalysisRecord, AnalysisStatus

def test_analysis_result_schema():
    result = AnalysisResult(
        prediction="fake",
        confidence=0.9,
        model_name="test_model",
        model_version="1.0",
        evidence={"detail": "some detail"},
        processing_time_ms=100
    )
    assert result.prediction == "fake"
    assert result.confidence == 0.9

def test_analysis_record_schema():
    record = AnalysisRecord(
        id="123",
        filename="test.jpg",
        media_type="image"
    )
    assert record.status == AnalysisStatus.pending
    assert record.result is None
    
    # Test updating status
    record.status = AnalysisStatus.completed
    assert record.status == AnalysisStatus.completed
