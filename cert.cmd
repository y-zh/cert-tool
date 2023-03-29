# curl -X POST http://localhost:5000/cert -H "Content-Type: application/json" --insecure -d @data.json -o cert.zip

curl -X POST https://cert.earth.xpaas.lenovo.com/cert -H "Content-Type: application/json" -d @data.json -o cert.zip