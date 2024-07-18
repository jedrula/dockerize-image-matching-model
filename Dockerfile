FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
RUN apt update && apt install -y python3.10 python3-pip libglib2.0-0 libgl1-mesa-glx vim && rm -rf /var/lib/apt/lists/*
WORKDIR /app
EXPOSE 8000
COPY ./models /app/models
COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
# RUN pip3 install torch==1.13.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
# this works but is not recommened apparetnly, maybe the below works without complaints but is untested: CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload <
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]