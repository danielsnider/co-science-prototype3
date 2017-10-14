# Install docker (Ubuntu 16.04)
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce

# ASSUMPTION NODE: You're current working director is the root folder of the co-science-prototype3 repository. 
# REASON: This is needed so that the docker build context has access to everything in the repository, otherwise docker build would only have access to the folders under the Dockerfile folder. More info: https://stackoverflow.com/questions/27068596/how-to-include-files-outside-of-dockers-build-context


# Build Docker image
docker build -f docker/Dockerfile.base -t cos-base .

# Test Docker image
docker run cos-base

# Snapshot Docker image
sudo docker commit 8ec3ea116cf03736e257004d0306bc2919e36b3c7e522034d8535b29c7340a63 danielsnider/cos-base:latest 

# Login to Dockerhub
sudo docker login

# Push to Dockerhub
sudo docker push danielsnider/cos-base

 