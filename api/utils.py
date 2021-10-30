import docker
import pathlib
import shutil
from fastapi import UploadFile

from schemas import Configuration, Container

DOCKER_CLIENT = docker.from_env()


def create_containter(filename: str):
    used_ports = set()
    for container in DOCKER_CLIENT.containers.list():
        used_port = container.ports.get('1080/tcp')[0].get('HostPort')
        used_ports.add(used_port)

    port = 1080
    while str(port) in used_ports:
        port += 1

    container = DOCKER_CLIENT.containers.run(
        'saronqw/openvpn-socks5',
        cap_add='NET_ADMIN',
        devices=['/dev/net/tun'],
        dns=['8.8.4.4'],
        ports={
            1080: port
        },
        tty=True,
        volumes={
            pathlib.Path(
                str(pathlib.Path.cwd().joinpath('configs').joinpath(filename))
            ): {
                'bind': '/vpn/' + filename,
                'mode': 'rw'
            }
        },
        detach=True
    )

    return get_info_container(container)


def get_info_container(container: Container):
    state = container.attrs.get('State')

    ovpn_file = None
    for mount in container.attrs.get('Mounts'):
        if mount.get('Type') == 'bind':
            ovpn_file = mount.get('Destination').split('/')[-1]

    return Container(
        id=container.attrs.get('Id'),
        ports=container.attrs.get('HostConfig').get('PortBindings'),
        status=state.get('Status'),
        started_at=state.get('StartedAt'),
        finished_at=state.get('FinishedAt'),
        ovpn_file=ovpn_file
    )


def get_info_container_by_id(container_id: str):
    try:
        container = DOCKER_CLIENT.containers.get(container_id)
    except docker.errors.NotFound:
        return False

    return get_info_container(container)


def get_info_containers():
    container_list = DOCKER_CLIENT.containers.list()
    container_list_objects = []
    for container in container_list:
        container_list_objects.append(get_info_container(container))

    return container_list_objects


def delete_container_by_id(container_id: str):
    container = DOCKER_CLIENT.containers.get(container_id)
    container.stop()
    container.remove()


def create_config_file(file: UploadFile):
    filename = file.filename
    with pathlib.Path('configs/', filename).open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def delete_config_file(config: Configuration):
    pathlib.Path.unlink(
        pathlib.Path.cwd().joinpath('configs').joinpath(config.filename)
    )
