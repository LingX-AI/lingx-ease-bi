import asyncio
import base64

import paramiko


def json_list_to_ddl(json_datas) -> (list, str):
    database_ddl = []
    for json_data in json_datas:
        table_name = json_data["table"]
        table_comment = json_data["comment"]

        ddl = f"CREATE TABLE {table_name} (\n"
        for column in json_data["columns"]:
            name = column["name"]
            data_type = column["type"]
            default = column["default"]
            nullable = column["nullable"] == "YES"
            comment = column["comment"]

            ddl += f"  {name} {data_type}"
            if default is not None:
                ddl += f" DEFAULT {default}"
            if nullable:
                ddl += " NULL"
            else:
                ddl += " NOT NULL"
            ddl += f" COMMENT '{comment}',\n"

        ddl = ddl.rstrip(",\n") + "\n"
        ddl += f") COMMENT '{table_comment}';"
        database_ddl.append(ddl)

    database_ddl_str = "\n".join(database_ddl)

    return database_ddl, database_ddl_str


def execute_remote_command(
    host: str | None,
    username: str | None,
    password: str | None,
    command: str,
) -> int:
    if not all([host, username, password]):
        return 1
    client = paramiko.SSHClient()
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=22, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        return stdout.channel.recv_exit_status()

    except Exception as e:
        raise e
    finally:
        client.close()


def stream_execute_remote_command(
    host: str,
    username: str,
    password: str,
    command: str,
):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=22, username=username, password=password)

        transport = client.get_transport()
        channel = transport.open_session()
        channel.exec_command(command)
        return channel

    except Exception as e:
        raise e


async def stream_command_output(
    host: str,
    username: str,
    password: str,
    command: str,
):

    try:
        channel = execute_remote_command(host, username, password, command)
        while True:
            if channel.recv_ready():
                output = channel.recv(1024).decode("utf-8")
                encoded_output = base64.b64encode(output.encode("utf-8")).decode(
                    "utf-8"
                )
                print(encoded_output)
                yield f"data: {encoded_output}\n\n"
            elif channel.exit_status_ready():
                break
            else:
                await asyncio.sleep(0.1)
    except Exception as e:
        error_message = base64.b64encode(str(e).encode("utf-8")).decode("utf-8")
        yield f"data: Error: {error_message}\n\n"
