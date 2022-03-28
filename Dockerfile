FROM python:3.10

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

ENV TOKEN=$TOKEN
ENV PREFIX=$PREFIX

CMD ["python", "bot.py"]