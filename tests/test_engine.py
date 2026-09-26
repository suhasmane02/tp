from app.analytics.engine import classify
def test_classification_is_conservative():
 assert classify(100,'none','#Shorts day')[0]=='short'
 assert classify(100,'none','vertical vlog')[0]=='unknown'
 assert classify(181,'none','vlog')[0]=='long_form'
 assert classify(100,'live','#Shorts')[0]=='live'
