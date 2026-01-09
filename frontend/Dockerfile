FROM node:18-alpine

WORKDIR /app

COPY package.json .
# We are only copying package.json for now to allow `npm install` to work in the container 
# even if the user hasn't run it locally. 
# Ideally, we would also copy package-lock.json if it existed.
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
