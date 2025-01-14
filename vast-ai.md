ssh -i ~/.ssh/id_rsa -p 14768 root@ssh5.vast.ai -L 8080:localhost:8080

apt update && apt install -y python3.10 python3-pip libglib2.0-0 libgl1-mesa-glx vim && rm -rf /var/lib/apt/lists/\*

git clone https://github.com/jedrula/dockerize-image-matching-model.git

cd dockerize-image-matching-model/

pip install -r requirements.txt

curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
 | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
 && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
 | sudo tee /etc/apt/sources.list.d/ngrok.list \
 && sudo apt update \
 && sudo apt install ngrok

uvicorn main:app --host 0.0.0.0 --port 8000

    ####

    NGROK_AUTHTOKEN=xxx ngrok http 8000 <- run in jupiter notebook second terminal
