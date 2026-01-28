#!/bin/bash
set -e

echo "🚀 Starting Deployment Process..."

# 1. Backend Deployment
echo "📦 Deploying Backend (Cloud Functions)..."
# In a real pipeline, we'd lint and test first
# pushd backend && pytest && popd
firebase deploy --only functions

# 2. Frontend Build & Deploy
echo "🏗️ Building Student Portal..."
cd frontend
npm install
npm run build
cd ..

echo "📤 Deploying Student Portal..."
firebase deploy --only hosting

# 3. Admin Portal Build & Deploy (Skipped for single site config)
# echo "🏗️ Building Admin Portal..."
# cd admin_portal
# npm install
# npm run build
# cd ..
# 
# echo "📤 Deploying Admin Portal..."
# # firebase deploy --only hosting:admin-portal

echo "✅ Deployment Complete!"
