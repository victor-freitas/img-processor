FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update &&\
	apt install curl -y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - &&\
	curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list &&\
	apt install apt-transport-https -y &&\
	apt update &&\
	ACCEPT_EULA=Y apt-get install msodbcsql17 unixodbc-dev mssql-tools -y

COPY . .

CMD ["python", "worker.py"]
