{
    "apiVersion": "0.2",
    "swaggerVersion": "1.1",
    "basePath": "http://{{host}}/api/v2",
    "apis": [
        {
            "path": "/drug",
            "description": "OpenBNF Drug entries",
            "operations": [
                {
                    "httpMethod": "GET",
                    "summary": "Search for drugs by name",
                    "responseClass": "string",
                    "nickname": "drugName",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "The name of the drug",
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