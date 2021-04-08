from handler import handle

#Example test event
event = {
    "Records": [
        {
            "s3": {
                "bucket": {
                "name": "team3testbucket"
            },
        "object": {
        "key": "chesterfield_09-03-2021_22-37-00.csv"
        }
    }
    }
    ]
}

handle(event, {})