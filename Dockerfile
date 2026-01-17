FROM node:18-alpine as frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
RUN npm run build

FROM opengauss/opengauss-server:latest

ENV GS_PASSWORD='Gauss@123'

ENV GS_DB='music_db'

WORKDIR /app

RUN yum install -y python3 python3-pip nc && \
    pip3 install --upgrade pip

COPY --from=frontend-builder /frontend/dist dist

COPY backend/ .

RUN pip3 install -r requirements.txt

RUN cat > /start.sh <<'EOF'
#!/bin/bash

/entrypoint.sh gaussdb &

while ! python3 -c "import psycopg2; from config import Config; psycopg2.connect(host=Config.DB_HOST, port=Config.DB_PORT, database='postgres', user=Config.DB_USER, password=Config.DB_PASSWORD).close(); print('数据库连接成功!')" 2>/dev/null; do
    sleep 10
done

python3 init_db.py && python3 app.py && python -m http.server 8000 --directory dist

EOF

RUN chmod +x /start.sh

ENTRYPOINT [ "/start.sh" ]

EXPOSE 5000

