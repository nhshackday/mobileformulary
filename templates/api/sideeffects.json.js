{
    "apiVersion": "0.2",
    "swaggerVersion": "1.1",
    "basePath": "http://{{host}}/api/v2",
    "apis": [
        {
            "path": "/sideeffects",
            "description": "OpenBNF Side effects search",
            "operations": [
                {
                    "httpMethod": "GET",
                    "summary": "Search for drugs who might be relevant to {sideeffects}",
                    "responseClass": "string",
                    "nickname": "sideeffectsDrugs",
                    "parameters": [
                        {
                            "name": "sideeffects",
                            "description": "The side effects text you would like to search for",
                            "paramType": "query",
                            "required": true,
                            "allowMultiple": false,
                            "dataType": "string"
                        }
                    ],
                    "errorResponses": [
                        {
                            "code": 404,
                            "reason": "No matching drugs found"
                        }
                    ]
                }
            ]
        }
    ]
}