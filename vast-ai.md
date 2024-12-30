ssh -i ~/.ssh/id_rsa -p 14768 root@ssh5.vast.ai -L 8080:localhost:8080

apt update && apt install -y python3.10 python3-pip libglib2.0-0 libgl1-mesa-glx vim && rm -rf /var/lib/apt/lists/\*

git clone https://github.com/jedrula/dockerize-image-matching-model.git

cd dockerize-image-matching-model/

pip install -r requirements.txt

installed ngrok with apt with https://download.ngrok.com/linux?tab=install <- used jupiter notebook for second terminal

    uvicorn main:app --host 0.0.0.0 --port 8000


    ####

    NGROK_AUTHTOKEN=xxx ngrok http 8000 <- run in jupiter notebook second terminal
