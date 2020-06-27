FROM node:lts-stretch-slim
WORKDIR /usr/src/bot
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8080
CMD ["npm", "run", "start"]