# DATABASE
DATABASE = '../project_database'

# COMMANDS
LIST_USERS = '/users'
LIST_USERS_METHOD = 'GET'

DISPLAY_USER = '/<uname>'
DISPLAY_USER_METHOD = 'GET'

ADD_USER = '/add/<uname>/<pay>'
ADD_USER_METHOD = 'GET'

RMV_USER = '/rmv/<uname>'
RMV_USER_METHOD = 'GET'

LIST_TRANSACTIONS = '/transactions'
LIST_TRANSACTIONS_METHOD = 'GET'

USER_TRANSACTIONS = '/<user>/transactions'
USER_TRANSACTIONS_METHOD = 'GET'

ADD_TRANSACTIONS = '/add/<source>/<recipient>/<amount>'
ADD_TRANSACTIONS_METHOD = 'GET'

CREATE_DATABASE = '/create_database'
CREATE_DATABASE_METHOD = 'GET'

HASH_CHECK = '/check_hash'
HASH_CHECK_METHOD = 'GET'
