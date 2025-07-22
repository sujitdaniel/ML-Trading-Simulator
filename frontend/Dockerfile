FROM node:20-alpine

WORKDIR /app

# Copy package files from the build context (which is the frontend folder)
COPY package*.json ./

# Install all dependencies
RUN npm install

# Copy the rest of the source code from the build context
COPY . .

CMD ["npm", "run", "dev"]