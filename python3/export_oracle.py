import cx_Oracle
import os

# Where do we want to save the files?
path_to_save = "/tmp/ora_export"

# Insert the path to the Oracle instant client
cx_Oracle.init_oracle_client(lib_dir='/Users/pborne/lib/instantclient_18_1',
                             config_dir=None, error_url=None, driver_name=None)

oracle_sys_password = 'XXXXXXXXXXX'

# Define all the schemas you want to fetch from a given database
# Field 1: Oracle username
# Field 2: Oracle Server (FQN or IP)
# Field 3: Oracle Port number
# Field 4: Oracle Service name

schemas = [['user1', 'x.y.z.t', 1521, 'PDB1'],
           ['user2', 'x.y.z.t', 1521, 'PDB1']
           ]

# Field 1: Oracle Object type
# Field 2: File extension to use when saving in a text file
# Field 3: Oracle query to use

ora_queries = [['tables', 'tab',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects
                   where object_type = 'TABLE'
                   and object_name not like 'BIN$%'
                   and   owner = """],
               ['indices', 'idx',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects
                   where object_type = 'INDEX'
                   and   owner = """],
               ['views', 'view',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects
                   where object_type = 'VIEW'
                   and   owner = """],
               ['mat_views', 'matview',
                """select owner, object_name, dbms_metadata.GET_DDL('MATERIALIZED_VIEW', object_name, owner)
                   from dba_objects 
                   where object_type = 'MATERIALIZED VIEW'
                   and   owner = """],
               ['sequences', 'seq',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects
                   where object_type = 'SEQUENCE'
                   and   owner = """],
               ['packages', 'pkg',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects
                   where object_type = 'PACKAGE' 
                   and   owner = """],
               ['procedures', 'prc',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects 
                   where object_type = 'PROCEDURE' 
                   and   owner = """],
               ['functions', 'fnc',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects 
                   where object_type = 'FUNCTION' 
                   and   owner = """],
               ['synonyms', 'syn',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner)
                   from dba_objects 
                   where object_type = 'SYNONYM' 
                   and   owner = """],
               ['triggers', 'trg',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) 
                   from dba_objects 
                   where object_type = 'TRIGGER' 
                   and   owner = """],
               ['types', 'typ',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) 
                   from dba_objects 
                   where object_type = 'TYPE' 
                   and   owner = """],
               ['type_bodies', 'typbdy',
                """select owner, object_name, dbms_metadata.GET_DDL(object_type, object_name, owner) 
                   from dba_objects 
                   where object_type = 'TYPE BODY' 
                   and   owner = """]
               ]

grants = [['grants', 'grant',
           """select {username}, 'system', dbms_metadata.get_granted_ddl( 'SYSTEM_GRANT', {username} ) from dual """],
          ['grants', 'grant',
           """select {username}, 'object', dbms_metadata.get_granted_ddl( 'OBJECT_GRANT', {username} ) from dual """],
          ['grants', 'grant',
           """select {username}, 'role', dbms_metadata.get_granted_ddl( 'ROLE_GRANT', {username} ) from dual """]
          ]

for schema in schemas:
    user = schema[0]
    server = schema[1]
    port = schema[2]
    service = schema[3]
    dsn = cx_Oracle.makedsn(server, port, service_name=service)
    connection = cx_Oracle.connect('sys', oracle_sys_password, dsn, cx_Oracle.SYSDBA)

    print("Connected to:", dsn)
    cursor = connection.cursor()

    # Grants
    counter = 0
    for ora_query in grants:
        object_type = ora_query[0]
        file_extension = ora_query[1]
        sql_query = ora_query[2].format(username="'" + str.upper(user) + "'")
        # print(sql_query)

        for result in cursor.execute(sql_query):
            file_path = path_to_save + "/" + service + "/schema=" + user + "/" + object_type + "/" + result[1] \
                        + "." + file_extension
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                print("Saving to ", directory)
                os.makedirs(directory)

            file_handle = open(file_path, "w+")
            retrieved_ddl = result[2].read().strip()  # Result back from Oracle

            splits = retrieved_ddl.split('\n')
            for split in splits:
                file_handle.write(split.strip() + ';\n')
            counter += 1
            file_handle.close()

    print("Retrieved %d grants for schema %s" % (counter, user))

    # Tables, Views, PL/SQL...
    for ora_query in ora_queries:
        object_type = ora_query[0]
        file_extension = ora_query[1]
        sql_query = ora_query[2] + "'" + str.upper(user) + "'"
        # print(sql_query)

        counter = 0
        for result in cursor.execute(sql_query):
            file_path = path_to_save + "/" + service + "/schema=" + user + "/" + object_type + "/" + result[1] \
                        + "." + file_extension
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                print("Saving to ", directory)
                os.makedirs(directory)

            file_handle = open(file_path, "w+")
            retrieved_ddl = result[2].read().rstrip()
            file_handle.write(retrieved_ddl)
            if not retrieved_ddl.endswith(";"):
                file_handle.write("\n;")
            counter += 1
            file_handle.close()

        print("Retrieved %d %s for schema %s" % (counter, object_type, user))

    print()
    connection.close()
