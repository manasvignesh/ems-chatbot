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
    assert res1.classification == "CLEARLY_OUT_OF_SCOPE"

    res2 = await classifier.classify("Write a python script to parse CSV files")
    assert res2.classification == "CLEARLY_OUT_OF_SCOPE"

    res3 = await classifier.classify("What is the stock price of Apple?")
    assert res3.classification == "CLEARLY_OUT_OF_SCOPE"


@pytest.mark.asyncio
async def test_classifier_ipl_disambiguation():
    classifier = ScopeClassifier()
    # Equinox sub-event queries
    res_in1 = await classifier.classify("How does IPL Auction work in Equinox?")
    assert res_in1.classification == "IN_SCOPE"

    res_in2 = await classifier.classify("In IPL Auction what do we do?")
    assert res_in2.classification == "IN_SCOPE"

    res_in3 = await classifier.classify("IPL auction")
    assert res_in3.classification == "IN_SCOPE"

    # Ambiguous cricket query
    res_amb = await classifier.classify("cricket")
    assert res_amb.classification == "AMBIGUOUS"
    assert "IPL Auction" in res_amb.clarification_prompt

    # Real cricket queries -> CLEARLY_OUT_OF_SCOPE
    res_out1 = await classifier.classify("What is today's cricket match score?")
    assert res_out1.classification == "CLEARLY_OUT_OF_SCOPE"

    res_out2 = await classifier.classify("who won IPL yesterday?")
    assert res_out2.classification == "CLEARLY_OUT_OF_SCOPE"

    res_out3 = await classifier.classify("IPL score")
    assert res_out3.classification == "CLEARLY_OUT_OF_SCOPE"

    res_out4 = await classifier.classify("current India vs Australia score")
    assert res_out4.classification == "CLEARLY_OUT_OF_SCOPE"
