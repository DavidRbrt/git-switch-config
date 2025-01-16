# [Git switch config](.)

This allows to easily switch between git configurations (user, ssh key) by automatically update **~/.gitconfig** and **~/.ssh/config** files.

## Prerequisites

- Setup ssh keys in **~/.ssh** folder

- Create confs.yaml in this folder. Here is a template:

    ```yaml
    default:
        git_user_name: George Abitbol
        hostname: github.com
    specific:
        - name: perso
        git_user_email: george.abitbol@gmail.com
        ssh_key: id_perso
        - name: warner
        git_user_email: george.abitbol@warner-bros.com
        ssh_key: id_warner
        - name: canal
        hostname: gitlab.com
        git_user_email: george.abitbol@canal-plus.cam
        ssh_key: id_canal

    ```

    Note: Any argument in *specific* override *default* one.

## Use

```bash
$ git_switch_config.py ${confname}
```

- ex:

```bash
$ git_switch_config.py perso
```

You can eventually add lines like this into your .bashrc:

```bash
alias sgit_perso="${path_to_this}/git_switch_config.py perso"
```
