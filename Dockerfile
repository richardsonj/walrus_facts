FROM python:3.7.2-slim
WORKDIR /walrus_facts
COPY . /walrus_fats
RUN pip install --trusted-host pypi.python.org -r requirements.txt
ENV NAME World
CMD ["python", "walrus_facts.py"]