import sys
import os
import logging
import pprint
logging.basicConfig(level=logging.INFO)
import pymongo
import docker

class JobCreator():
    pass


if __name__ == "__main__":
    ip = 'localhost' #GETH CLIENT IP
    port = 10000 #GETH CLIENT PORT
    if len(sys.argv) > 1:
        prosumer_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        ip = sys.argv[2]
    if len(sys.argv) > 3:
        port = sys.argv[3]
    if len(sys.argv) > 4:
        providing = sys.argv[4]
    if len(sys.argv) > 5 :
        jobspath = sys.argv[5]

    # for (dirpath, dirnames, filenames) in os.walk(jobspath):
    #     if filenames :
    #         print(dirpath)
    #         print(filenames)

    jobpath = "/home/riaps/projects/transactive-blockchain/code/ResourcePlatform/jobs/job0"
    jobname = "eiselesr/job0"

    APIclient = docker.APIClient(base_url='unix://var/run/docker.sock')

    client = docker.from_env()
    client.login(username='eiselesr', password='eiselesr@docker')

    #build image
    image = client.images.build(path=jobpath, tag=jobname)[0]

    for line in client.images.push(jobname, stream=True):
        print (line)

#     dist_dict = APIclient.inspect_distribution(jobname)
#     pprint.pprint(dist_dict)
#     sha256 = dist_dict['Descriptor']['digest']
#     size = dist_dict['Descriptor']['size']
#     os = dist_dict['Platforms'][0]['os']
#     arch = dist_dict['Platforms'][0]['architecture']
# print(sha256, size, os, arch)

    image_dict = APIclient.inspect_image(jobname)
    pprint.pprint(image_dict)
    repoDigestSha = image_dict["RepoDigests"][0]
    IDsha = image_dict["Id"]
    size = image_dict["Size"]
    os = image_dict["Os"]
    arch = image_dict["Architecture"]
    print(repoDigestSha, IDsha, size, os, arch)


    #push image
    #get sha
