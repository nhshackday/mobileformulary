{
    "apiVersion": "0.2",
    "swaggerVersion": "1.1",
    "basePath": "http://{{host}}/api/v2",
    "apis": [
        {
            "path": "/indication",
            "description": "OpenBNF Indication search",
            "operations": [
                {
                    "httpMethod": "GET",
                    "summary": "Search for drugs who might be relevant to {indication}",
                    "responseClass": "string",
                    "nickname": "indicationDrugs",
                    "parameters": [
                        {
                            "name": "indication",
                            "description": "The indication text you would like to search for",
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