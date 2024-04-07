FROM python:3.10-slim

WORKDIR /proxy

RUN apt-get update && apt-get install gettext -y
RUN python -m pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./main.py ./main.py

CMD ["python", "main.py"]
