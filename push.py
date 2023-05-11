import os
import paramiko
import select


project_path = os.path.dirname(os.path.realpath(__file__))
username = os.environ.get("USERNAME", "admin")
password = os.environ.get("PASSWORD", "admin")
environment = os.environ.get("ENVIRONMENT", "test")

devices_dict = {"prod": {"prod00": "3.228.97.247",
                         "prod01": "34.192.157.124"},
                "test": {
                    "test00": "18.211.19.45",
                    "test01": "52.21.255.78"
                }}

name_translation = {"prod00": "test00",
                    "prod01": "test01"}


def prompt(chan, timeout=2):
    buff = ''
    while not buff.endswith('#'):
        ready, _, _ = select.select([chan], [], [], timeout)
        if not ready:
            output = chan.send("\n")
            break
        r = chan.recv(65535)
        r1 = str(r, 'utf-8')
        buff += r1
    return buff


def device_configure(configs, ip) -> str:
    """
    Creates SSH connection with device, sends commands, and collects results
    """
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, port=22, username=username, password=password, look_for_keys=False,
                  allow_agent=False)
        ssh = c.invoke_shell()
        prompt(ssh)
        ssh.send("config terminal\n")
        for c in configs:
            ssh.send(c)
            output = prompt(ssh)
            print(output)
        ssh.close()
        return output
    except Exception as e:
        print(f'Failed to connect to device {ip}. \nException {e}')
        return False


def main():
    devices = os.listdir(os.path.join(project_path, "devices"))
    for device in devices:
        device_config_filename = os.path.join(os.path.join(os.path.join(project_path, "devices"), device), "config")
        print(device_config_filename)
        with open(device_config_filename, "r") as f:
            config = f.readlines()
        print(config)
        if environment == "test":
            device = name_translation.get(device)
        device_configure(config, devices_dict[environment][device])


if __name__ == "__main__":
    main()
