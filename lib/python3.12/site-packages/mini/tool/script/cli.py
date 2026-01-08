import click


@click.command()
@click.argument('pkg_name')
@click.argument('robot_id')
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.option('--debug', is_flag=False)
def cli_show_py_pkg(pkg_name: str, robot_id: str, type: str = "dedu", debug: bool = True):
    from mini import query_py_pkg
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    print(f'{query_py_pkg(pkg_name, robot_id)}')


@click.command()
@click.argument('robot_id')
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.option('--debug', is_flag=False)
def cli_list_py_pkg(robot_id: str, type: str = "dedu", debug: bool = True):
    from mini import list_py_pkg
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    print(f'{list_py_pkg(robot_id)}')


@click.command()
@click.argument('project_dir')
def cli_setup_py_pkg(project_dir: str):
    from mini import setup_py_pkg
    print(f'{setup_py_pkg(project_dir)}')


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.argument('pkg_path')
@click.argument('robot_id')
def cli_install_py_pkg(pkg_path: str, robot_id: str, type: str = "dedu", debug: bool = False):
    from mini import install_py_pkg
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    install_py_pkg(pkg_path, robot_id, debug)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.argument('pkg_name')
@click.argument('robot_id')
def cli_uninstall_py_pkg(pkg_name: str, robot_id: str, type: str = "dedu", debug: bool = False):
    from mini import uninstall_py_pkg
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    uninstall_py_pkg(pkg_name, robot_id, debug)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.argument('entry_point')
@click.argument('robot_id')
def cli_run_py_pkg(entry_point: str, robot_id: str, type: str = "dedu", debug: bool = False):
    from mini import run_py_pkg
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    run_py_pkg(entry_point, robot_id, debug)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.argument('cmd')
@click.argument('robot_id')
def cli_run_cmd(cmd: str, robot_id: str, type: str = "dedu", debug: bool = False):
    from mini import run_py_pkg
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    run_py_pkg(cmd, robot_id, debug)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.argument('cmd')
@click.argument('robot_id')
def cli_adb_enable(robot_id: str, type: str = "dedu", debug: bool = False):
    from mini import switch_adb
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    switch_adb(robot_id, True)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--type', type=click.Choice(['mini', 'dedu', 'edu', 'kor']))
@click.argument('cmd')
@click.argument('robot_id')
def cli_adb_disable(robot_id: str, type: str = "dedu", debug: bool = False):
    from mini import switch_adb
    from mini import mini_sdk as MiniSdk
    if type == 'mini':
        MiniSdk.set_robot_type(MiniSdk.RobotType.MINI)
    elif type == 'dedu':
        MiniSdk.set_robot_type(MiniSdk.RobotType.DEDU)
    elif type == "edu":
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    elif type == "kor":
        MiniSdk.set_robot_type(MiniSdk.RobotType.KOR)
    else:
        print(f'error robot_type:\'{type}\' param.')
        return
    if debug:
        import logging
        MiniSdk.set_log_level(logging.DEBUG)
    switch_adb(robot_id, False)
