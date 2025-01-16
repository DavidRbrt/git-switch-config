#!/usr/bin/env python3

import argparse
from pathlib import Path
import yaml
import subprocess
from _io import TextIOWrapper


GIT_CONFIG_FILE_PATH = Path.home() / ".gitconfig"
SSH_CONFIG_FILE_PATH = Path.home() / ".ssh/config"


def git_switch_config(conf_requested: str):
    script_folder = Path(__file__).parents[0]
    confs_file_path = script_folder / "confs.yaml"

    hostname: str = None
    git_user_name: str = None
    git_user_email: str = None
    ssh_key: str = None

    with open(confs_file_path, 'r') as confs_file:
        confs = yaml.safe_load(confs_file)

        # parse default
        default_conf = confs.get("default", None)
        if default_conf is not None:
            hostname = default_conf.get("hostname", hostname)
            git_user_name = default_conf.get("git_user_name", git_user_name)
            git_user_email = default_conf.get("git_user_email", git_user_email)
            ssh_key = default_conf.get("ssh_key", ssh_key)

        # parse specific
        specific_confs = confs.get("specific", None)
        if specific_confs is not None:
            for specific_conf in specific_confs:
                if specific_conf.get("name", None) == conf_requested:
                    hostname = specific_conf.get("hostname", hostname)
                    git_user_name = specific_conf.get("git_user_name", git_user_name)
                    git_user_email = specific_conf.get("git_user_email", git_user_email)
                    ssh_key = specific_conf.get("ssh_key", ssh_key)

        # setup git config global
        if git_user_name is not None:
            cmd = subprocess.run(["git", "config", "--global", "user.name", git_user_name])
        else:
            print("WARNING: no user_name configuration")
            cmd = subprocess.run(["git", "config", "--global", "--unset", "user.name"])

        if git_user_email is not None:
            cmd = subprocess.run(["git", "config", "--global", "user.email", git_user_email])
        else:
            print("WARNING: no user_email configuration")
            cmd = subprocess.run(["git", "config", "--global", "--unset", "user.email"])

        # setup ssh key
        if ssh_key is not None:
            ssh_key_path = Path(f"~/.ssh/{Path(ssh_key).name}")
            ssh_config = None
            if SSH_CONFIG_FILE_PATH.exists():
                with open(SSH_CONFIG_FILE_PATH, "r") as ssh_config_file:
                    ssh_config = _ssh_config_file_to_dict(ssh_config_file)
            ssh_config_found = False
            if ssh_config is not None:
                for host in ssh_config:
                    if host.get("HostName", None) == hostname:
                        ssh_config_found = True
                        host["IdentityFile"] = str(ssh_key_path)
            if ssh_config is None or not ssh_config_found:
                if ssh_config is None:
                    ssh_config = []
                ssh_config.append({
                    "name": hostname,
                    "HostName": hostname,
                    "IdentityFile": str(ssh_key_path)
                })
            with open(SSH_CONFIG_FILE_PATH, "w+") as ssh_config_file:
                _ssh_config_dict_to_file(ssh_config, ssh_config_file)
        else:
            print("WARNING: no ssh_key configuration")

        _print_conf()

    return 0


def _ssh_config_file_to_dict(ssh_config_file: TextIOWrapper):
    ssh_config = []
    current_host = {}
    for line in ssh_config_file.readlines():
        line = line.strip()
        if line == "":
            continue
        elif line.startswith("Host "):
            if current_host.get("name", None) is not None:
                ssh_config.append(current_host)
                current_host = {}
            current_host["name"] = line.replace("Host ", "").strip()
        else:
            elements = line.split(" ")
            current_host[elements[0]] = elements[1]

    if current_host.get("name", None) is not None:
        ssh_config.append(current_host)

    return ssh_config


def _ssh_config_dict_to_file(ssh_config: dict, ssh_config_file: TextIOWrapper):
    for host in ssh_config:
        ssh_config_file.write(f"Host {host['name']}\n")
        for param in host:
            if param != "name":
                ssh_config_file.write(f"    {param} {host[param]}\n")


def _command_line_parser():
    parser = argparse.ArgumentParser(description='Git switch configuration tool')

    parser.add_argument('conf', type=str, help='conf name')

    args, _ = parser.parse_known_args()

    return args


def _print_conf():
    print(f"* GIT configuration (${GIT_CONFIG_FILE_PATH})\n******************************************************")
    subprocess.run(["cat", GIT_CONFIG_FILE_PATH])
    print("")

    print(f"* SSH configuration (${SSH_CONFIG_FILE_PATH})\n******************************************************")
    subprocess.run(["cat", SSH_CONFIG_FILE_PATH])
    print("")


if __name__ == '__main__':
    args = _command_line_parser()
    ret = git_switch_config(conf_requested=args.conf)
    exit(ret)
