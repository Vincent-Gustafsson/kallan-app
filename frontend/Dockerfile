FROM node:20-alpine

WORKDIR /app

# Install deps first (cached)
COPY package*.json ./
RUN npm ci

# Copy source (for image completeness; bind mount will override in dev)
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173", "--strictPort"]
