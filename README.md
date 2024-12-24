# Dockerize Deep learning model

The objectibe of this repository is to give overview of deplyoing a pretrained deep learning computer vison model by dockerizing it, which is based on kornia framework which matches the given two image.

[Kornia](https://kornia.readthedocs.io/en/latest/) is a computer vision framework built on top of pytorch

The pretrained model which has been used is [kornia implementation](https://kornia.readthedocs.io/en/latest/applications/image_matching.html) of LoFTR: Detector-Free Local Feature Matching with Transformers. LoFTR can extract high-quality semi-dense matches even in indistinctive regions with low-textures, motion blur, or repetitive patterns.

![image](./demo/images/output.jpg)

## To-Do

1. Install [Docker](https://docs.docker.com/engine/install/) as per your operating system. Ignore this part if you already have it.
2. Clone this repository by running `git clone https://github.com/Deshram/dockerize-image-matching-model`
3. Make a `models` folder and download weights from below links
4. Here I've used [outdoor](http://cmp.felk.cvut.cz/~mishkdmy/models/loftr_outdoor.ckpt) weights, but you can also try [indoor](http://cmp.felk.cvut.cz/~mishkdmy/models/loftr_indoor.ckpt) and [indoor new](http://cmp.felk.cvut.cz/~mishkdmy/models/loftr_indoor_ds_new.ckpt) weights which are trained on different dataset by downloading them in `models` folder
5. Build docker image by running `docker build -t IMAGE_NAME .` e.g. `docker build -t image_mathcing .`
6. Run docker container to deploy on host `docker run --gpus all -p HOST_PORT:CONTAINER_PORT IMAGE_NAME` e.g. `docker run --gpus all -p 5000:5000 image_matching`
   PS: Use `--gpus all` if host machine contains GPU

sudo docker run --gpus all -p 8000:8000 9ad952ab8ec9

https://github.com/Deshram/dockerize-image-matching-model/assets/43752639/42cd6637-4b6d-402d-b417-2d1a31e81879

----- My additional notes ---
{
"deploy:local": "ngrok http 8000",
"ssh:production": "ssh administrator@108.181.196.114",
"open:prod": "open http://108.181.196.11:8000/docs",
"kill": "kill $(lsof -t -i:8000)"
"cuda:version": "nvcc --version"
}

scp ./main.py administrator@108.181.196.114:jedrula
scp ./requirements.txt administrator@108.181.196.114:jedrula
scp -r ./models administrator@108.181.196.114:jedrula
scp -r ./images administrator@108.181.196.114:jedrula
scp -r ./ui administrator@108.181.196.114:jedrula

ssh:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt install -y python3.11 python3-pip libglib2.0-0 vim && sudo rm -rf /var/lib/apt/lists/\*
pip install uvicorn --break-system-packages
pip install -r requirements.txt --break-system-packages
pip install light-the-torch --break-system-packages
ltt install torch torchvision --break-system-packages
/home/administrator/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
open 8000 port using ufw, also REMEMBER to open 22 port at the same time "sudo ufw allow 8000/tcp and-allow-ssh
" (https://www.cyberciti.biz/faq/how-to-open-firewall-port-on-ubuntu-linux-12-04-14-04-lts/#:~:text=The%20service%20specific%20syntax%20is%20as%20follows%20to,sudo%20ufw%20allow%2080%2Ftcp%20sudo%20ufw%20allow%20443%2Ftcp)

https://github.com/garygrossgarten/github-action-scp

1. docker build -t image_mathcing .
2. go to docker desktop app and run container from image. Make sure to set 8000 in port mapping
3. go to localhost:8000/ui
4. choose image and take one from `test-user-images`. The region we compare against is hardcoded. Currently set to szczytna so you can pick szczytnik_gdzies2. It's a long wait, be patient.

i had issues with cuda, i then installed cuda with https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_local after watching: https://www.google.com/search?q=upgrade+cuda++ubuntu+&sca_esv=e7a2bf937769b224&rlz=1C5CHFA_enPL948PL949&sxsrf=ADLYWIIfYzLGhxI8KSZ7euR0VkZ25Zjx_Q%3A1724580715553&ei=awPLZqaxIeK8xc8PzqqZ-AI&ved=0ahUKEwjmkr_n84-IAxViXvEDHU5VBi8Q4dUDCA8&uact=5&oq=upgrade+cuda++ubuntu+&gs_lp=Egxnd3Mtd2l6LXNlcnAiFXVwZ3JhZGUgY3VkYSAgdWJ1bnR1IDIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIGEAAYFhgeSIkRUABYrQ9wAXgAkAEAmAF_oAGVCKoBAzAuObgBA8gBAPgBAZgCCqACtQjCAgQQIxgnwgILEAAYgAQYkQIYigXCAgoQABiABBhDGIoFwgIFEAAYgATCAgsQABiABBiGAxiKBcICBRAhGKABmAMAkgcDMS45oAfeOQ&sclient=gws-wiz-serp#fpstate=ive&vld=cid:1afad7c0,vid:8i3BiWa5AZ4,st:0
