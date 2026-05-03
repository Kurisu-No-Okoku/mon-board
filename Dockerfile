FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

# Copie tout le contenu du dossier (y compris index.html) dans le container
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
