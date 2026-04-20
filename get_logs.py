import boto3
import json

logs = boto3.client('logs', region_name='ap-northeast-1')
try:
    response = logs.describe_log_streams(
        logGroupName='/aws/lambda/handson-llmops-handson-llmops-v10-CrewFunction',
        orderBy='LastEventTime',
        descending=True
    )
    
    if response.get('logStreams'):
        latest_stream = response['logStreams'][0]['logStreamName']
        print(f"Latest stream: {latest_stream}")
        
        # Get log events
        events = logs.get_log_events(
            logGroupName='/aws/lambda/handson-llmops-handson-llmops-v10-CrewFunction',
            logStreamName=latest_stream,
            limit=50,
            startFromHead=False
        )
        
        for event in events.get('events', []):
            print(event.get('message', ''))
    else:
        print("No log streams found")
except Exception as e:
    print(f"Error: {e}")
