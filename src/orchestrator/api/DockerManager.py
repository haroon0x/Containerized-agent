import docker
import os

#configs
IMAGE = os.getenv("AGENT_IMAGE", "containerized-agent:latest")

class DockerManager():
    def __init__(self): # connect to the docker deamon
        self.client = docker.from_env()
        pass
    
    def run_container(self , prompt :str ):

        container = self.client.containers.run(
            IMAGE,
            detach=True,
            auto_remove=True,
            entrypoint="/entrypoint.sh",
            environment= {"PROMPT": prompt},
            volumes={"bind":"/home/task","mode":"rw"},
            network_mode="bridge",                        
            )
        return container

    def list_containers(self):
        return self.client.containers.list(all=True)
        
    def get_container(self,id:str):
        return self.client.containers.get(id)
    
    def get_container_id(self,container):
        return container.id 
    
    
    def stop_container(self, id :str):
        self.get_container(id).stop()

    