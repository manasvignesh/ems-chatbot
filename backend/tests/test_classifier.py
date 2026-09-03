import pytest
from app.ai.classifier import ScopeClassifier
from app.models.chat import PageContext


@pytest.mark.asyncio
async def test_classifier_in_scope():
    classifier = ScopeClassifier()
    res1 = await classifier.classify("What events are happening at Equinox 2.0?")
    assert res1.classification == "IN_SCOPE"

    res2 = await classifier.classify("When does Crossroads start?")
    assert res2.classification == "IN_SCOPE"

    res3 = await classifier.classify("Tell me about Startup Poly")
    assert res3.classification == "IN_SCOPE"


@pytest.mark.asyncio
async def test_classifier_out_of_scope():
    classifier = ScopeClassifier()
    res1 = await classifier.classify("Who won yesterday's IPL match?")
    assert res1.classification == "OUT_OF_SCOPE"

    res2 = await classifier.classify("Write a python script to parse CSV files")
    assert res2.classification == "OUT_OF_SCOPE"

    res3 = await classifier.classify("What is the stock price of Apple?")
    assert res3.classification == "OUT_OF_SCOPE"


@pytest.mark.asyncio
async def test_classifier_ipl_disambiguation():
    classifier = ScopeClassifier()
    # Equinox sub-event query
    res_in = await classifier.classify("How does IPL Auction work in Equinox?")
    assert res_in.classification == "IN_SCOPE"

    # Real cricket query
    res_out = await classifier.classify("What is today's cricket match score?")
    assert res_out.classification == "OUT_OF_SCOPE"
