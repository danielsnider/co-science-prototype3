# Install docker (Ubuntu 16.04)
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce

# ASSUMPTION NODE: You're current working director is the root folder of the co-science-prototype3 repository. 
# REASON: This is needed so that the docker build context has access to everything in the repository, otherwise docker build would only have access to the folders under the Dockerfile folder. More info: https://stackoverflow.com/questions/27068596/how-to-include-files-outside-of-dockers-build-context


# Build Docker image
sudo docker build -f docker/Dockerfile.base -t cos-base .

# Test Docker image
sudo docker run cos-base
sudo docker run --entrypoint "cos" cos-base launch # modify entry command
sudo docker run -it --entrypoint "/bin/bash" cos-base # interactive
sudo docker run -p 50052:50052 -p 50053:50053 --entrypoint "python" cos-app /cos_packages/filters/src/filter.py

# Stop Docker image
sudo docker stop `sudo docker ps -l -q`

# Snapshot Docker image
sudo docker ps -a # get container ID
sudo docker commit 6b41bf410fbf danielsnider/cos-base:latest

# Login to Dockerhub
sudo docker login

# Push to Dockerhub
sudo docker push danielsnider/cos-base

 