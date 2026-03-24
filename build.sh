#!/bin/bash
# Generates google-ads.yaml from environment variables at Railway startup.
# This avoids committing credentials to git.

cat > google-ads.yaml <<EOF
developer_token: ${GOOGLE_ADS_DEVELOPER_TOKEN}
client_id: ${GOOGLE_CLIENT_ID}
client_secret: ${GOOGLE_CLIENT_SECRET}
refresh_token: ${GOOGLE_ADS_REFRESH_TOKEN}
use_proto_plus: True
EOF

echo "google-ads.yaml generated"
