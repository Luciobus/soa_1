To start docker use `docker-compose up --build`

To get result for specific format use
`echo -n '{"type": "get_result", "format" : $FORMAT_TYPE}' | nc -u -w1 0.0.0.0 2000`

Available formats:
NATIVE
JSON
XML
GOOGLE_BUFFER
APACHE
YAML
MESSAGEPACK

To get all result use
`echo -n '{"type": "get_result_all"}' | nc -u -w1 0.0.0.0 2000`
