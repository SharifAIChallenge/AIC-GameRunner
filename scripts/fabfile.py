import os.path
from time import sleep

from fabric.api import local, abort, run, env, put


def get_ip():
    return local('hostname -I | cut -d" " -f1', capture=True)


def install_docker():
    run("apt-get update")
    run("apt-get install apt-transport-https ca-certificates curl software-properties-common -y")
    run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")
    run("add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"")
    run("apt-get update")
    run("apt-get install docker-ce -y")


def swarm_join():
    token = local('docker swarm join-token manager -q', capture=True)
    ip = get_ip()
    run('docker swarm join --token {} {}:2377'.format(token, ip))


def mount_nfs():
    local("echo '/nfs {}(rw,sync,no_subtree_check,no_root_squash)' >> /etc/exports".format(env.host_string))
    local("systemctl restart nfs-kernel-server")
    ip = get_ip()
    run('apt-get install nfs-common -y')
    run('mkdir -p /nfs')
    sleep(3)
    run('mount {}:/nfs /nfs'.format(ip))
    run('echo "{}:/nfs /nsf nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0" >> /etc/fstab'.format(ip))


images = ["aic_py3_image", "kondor-manager", "aic_cpp_image", "aic_java_image",
          "aic_client_image", "aic_server_image"]


def push_images():
    ip = get_ip()
    for image in images:
        local("docker tag {} {}:5000/{}".format(image, ip, image))
        local("docker push {}:5000/{}".format(ip, image))


def pull_images():
    ip = get_ip()
    for image in images:
        run("docker pull {}:5000/{}".format(ip, image))
        run("docker tag {}:5000/{} {}".format(ip, image, image))


def docker_registry(certfile):
    if not os.path.isfile(certfile):
        abort("Aborting becuase certification file doesn't exists")

    ip = get_ip()
    run('mkdir -p "/etc/docker/certs.d/{}:5000"'.format(ip))
    put(certfile, "/etc/docker/certs.d/{}:5000/ca.crt".format(ip))

    username = "aichallenge"
    password = "aichallenge"
    run("docker login -u {} -p {} {}:5000".format(username, password, ip))
    pull_images()


def add_prune_crontab():
    run("echo */1 * * * * docker system prune --force > /var/spool/cron/crontabs/root")


def make_big(certfile=None):
    if certfile is None:
        print("Usage: fab -H hostnames,... make_big:<cert-file-location>")
        print("\n+ Swarm should be initialized.\n+ NFS directory should be exported.\n+ Docker images should be built.")
        print("+ Secure docker registry should be running\n+ Images should be pushed on the registry")
        return
    install_docker()
    sleep(60)
    swarm_join()
    mount_nfs()
    docker_registry(certfile)
    add_prune_crontab()


def docker_prune():
    local("docker system prune --force")
    run("docker system prune --force")
