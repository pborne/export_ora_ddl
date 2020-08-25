import cx_Oracle
import os

# Where do we want to save the files?
path_to_save = "/tmp/ora_export"

# Insert the path to the Oracle instance client
cx_Oracle.init_oracle_client(lib_dir='<path_to_oracle_instant_client>',
                             config_dir=None, error_url=None, driver_name=None)

# Define all the schemas you want to fetch from a given database
# Field 1: Oracle user name
# Field 2: Oracle Password
# Field 3: Oracle Server
# Field 4: Port number
# Field 5: Oracle Service name

schemas = [['user1', 'password', '192.168.0.199', 1521, 'SID'],
           ['user2', 'password', '192.168.0.199', 1521, 'SID'],
           ['user3', 'password', '192.168.0.199', 1521, 'SID'],
           ]

# Field 1: Oracle Object type
# Field 2: File extension to use when saving in a text file
# Field 3: Oracle query to use

ora_queries = [['tables', 'tab',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'TABLE' \
                   and object_name not like 'BIN$%' \
                   and   owner = """],
               ['indices', 'idx',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'INDEX' \
                   and   owner = """],
               ['views', 'view',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'VIEW' \
                   and   owner = """],
               ['mat_views', 'matview',
                """select owner, object_name, dbms_metadata.GET_DDL('MATERIALIZED_VIEW', object_name, owner) \
                   from dba_objects \
                   where object_type = 'MATERIALIZED VIEW' \
                   and   owner = """],
               ['sequences', 'seq',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'SEQUENCE' \
                   and   owner = """],
               ['packages', 'pkg',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'PACKAGE' \
                   and   owner = """],
               ['procedures', 'prc',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'PROCEDURE' \
                   and   owner = """],
               ['functions', 'fnc',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'FUNCTION' \
                   and   owner = """],
               ['synonyms', 'syn',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'SYNONYM' \
                   and   owner = """],
               ['triggers', 'trg',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'TRIGGER' \
                   and   owner = """],
               ['types', 'typ',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'TYPE' \
                   and   owner = """],
               ['type_bodies', 'typbdy',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) \
                   from dba_objects \
                   where object_type = 'TYPE BODY' \
                   and   owner = """]
               ]

grant_queries = [['grants', 'sql',
                  """select username, 'system', dbms_metadata.get_granted_ddl( 'SYSTEM_GRANT', username ) \
                     from all_users \
                     where username = """],
                 ['grants', 'sql',
                  """select username, 'object', dbms_metadata.get_granted_ddl( 'OBJECT_GRANT', username ) \
                     from all_users \
                     where username = """],
                 ['grants', 'sql',
                  """select username, 'role', dbms_metadata.get_granted_ddl( 'ROLE_GRANT', username ) \
                     from all_users \
                     where username = """]
                 ]

for schema in schemas:
    user = schema[0]
    pwd = schema[1]
    server = schema[2]
    port = schema[3]
    db = schema[4]
    dsn = cx_Oracle.makedsn(server, port, db)

    connection = cx_Oracle.connect(user, pwd, dsn)
    print("Connected to: ", dsn)
    cursor = connection.cursor()

    # Grants
    for ora_query in grant_queries:
        object_type = ora_query[0]
        file_extension = ora_query[1]
        sql_query = ora_query[2] + "'" + str.upper(user) + "'"
        print(sql_query)

        for result in cursor.execute(sql_query):
            file_path = path_to_save + "/" + db + "/schema=" + user + "/" + object_type + "/" + result[1] \
                        + "." + file_extension
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_handle = open(file_path, "w+")
            retrieved_ddl = result[2].read().rstrip()  # Result back from O.

            new_ddl = retrieved_ddl.replace("\n \n", ";\n")  # Insert missing ';'
            file_handle.write(new_ddl)  # Save it

            if not new_ddl.endswith(";"):  # Do we need a final ';'?
                file_handle.write(";\n")

            file_handle.close()

    # Tables, Views, PL/SQL...
    for ora_query in ora_queries:
        object_type = ora_query[0]
        file_extension = ora_query[1]
        sql_query = ora_query[2] + "'" + str.upper(user) + "'"
        print(sql_query)

        for result in cursor.execute(sql_query):
            file_path = path_to_save + "/" + db + "/schema=" + user + "/" + object_type + "/" + result[1] \
                        + "." + file_extension
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_handle = open(file_path, "w+")
            retrieved_ddl = result[2].read().rstrip()
            file_handle.write(retrieved_ddl)
            if not retrieved_ddl.endswith(";"):
                file_handle.write(";")
            file_handle.close()

    print()
    connection.close()
