FROM python:3.8
WORKDIR /api
COPY requirements.txt /api/requirements.txt
RUN pip3 install — no-cache-dir -r /api/requirements.txt
COPY . /api/
CMD [“uvicorn”, main:app”, “ — host=0.0.0.0”, “ — reload”]