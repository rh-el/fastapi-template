curl -i https://fastapi-template-lake.vercel.app/ \
  -H "Origin: https://statics.dmcdn.net"

curl -i https://fastapi-template-lake.vercel.app/ \
  -H "Origin: https://evil.example"

curl -i -X GET https://fastapi-template-lake.vercel.app/api/v1/user \
  -H "Origin: https://statics.dmcdn.net" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -H 'accept: application/json'

curl -i -X OPTIONS https://fastapi-template-lake.vercel.app/api/v1/user \
  -H "Origin: https://evil.example" \
  -H "Access-Control-Request-Method: POST"