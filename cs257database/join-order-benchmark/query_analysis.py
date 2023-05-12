import sqlite3
import sqlparse
import numpy as np
from Ant_colony_algo_python import AntColonyOptimization
from Gentic_Algo_pyhton import GeneticAlgorithm
import matplotlib.pyplot as plt
from deap import base, creator, tools
from functools import partial
import sim


# part 1: read the query
raw_multi_join_query = ""
with open('2a.sql') as f:
    raw_multi_join_query = f.read()

connection = sqlite3.connect('test_database.db')
cursor = connection.cursor()

# read indices
indexDict = dict()

# TODO: retrieve indices info from sqlite3 generically instead of hardcoded
# items are formatted as column : number of keys
indexDict["movie_companies"] = {"company_id": 234988,
                                "company_type_id": 2, "movie_id": 1087231}
indexDict["movie_info_idx"] = {"info_type_id": 5, "movie_id": 459925}
indexDict["movie_info"] = {"info_type_id": 71, "movie_id": 2468580}
indexDict["person_info"] = {"info_type_id": 22, "person_id": 502889}
indexDict["movie_keyword"] = {"keyword_id": 134170, "movie_id": 476794}
indexDict["aka_title"] = {"kind_id": 6, "movie_id": 205583}
indexDict["title"] = {"kind_id": 6}
indexDict["movie_link"] = {"linked_movie_id": 16169,
                           "link_type_id": 16, "movie_id": 6411}
indexDict["cast_info"] = {"movie_id": 2331574, "person_id": 4051366,
                          "person_role_id": 3139935, "role_id": 11}
indexDict["complete_cast"] = {"movie_id": 93514}
indexDict["aka_name"] = {"person_id": 588211}


# TODO: count one time and save to local file for next run
def count_number_of_index_keys():
    for key, value in indexDict.items():
        for column_key in value.keys():
            sql_query = "SELECT COUNT( DISTINCT {}) from {}".format(column_key, key)
            print("Counting keys of ", column_key, "on", key, "...")
            cursor.execute(sql_query)
            row_count = cursor.fetchone()[0]
            value[column_key] = row_count


# TODO: save database last state to local file and reuse
# Please uncomment this line if the database was modified.
# count_number_of_index_keys()

# method to check if table has a given column as its index.
def isIndex(table, column):
    if table in indexDict:
        for key, value in indexDict[table].items():
            if key == column:
                return True
    return False


# Part 2: analyze SQL multi-join query
# method to get and analyze select tokens
def get_select_tokens(select):
    print(select.tokens)


# method to get a tuple of table name in short and full form.
def set_table_name(statement):
    table = statement.split()
    return table[2], table[0]


# method to get a dictionary which key : value are short form : full name of a tables
def get_from_tokens(from_clause):
    table_dict = dict()
    for token in from_clause.tokens:
        if isinstance(token, sqlparse.sql.Identifier):
            table_name = set_table_name(token.value)
            table_dict[table_name[0]] = table_name[1]
    return table_dict


# method to the where clause's terms
def get_where_tokens(where):
    where_terms = []
    for token in where.tokens:
        if isinstance(token, sqlparse.sql.Parenthesis) or isinstance(token, sqlparse.sql.Comparison) \
                or token.value == "AND" or token.value == "OR":
            where_terms.append(token)
    return where_terms


# method to check if a string is a comparison oper
def isComparisonOper(value):
    opers = ['=', 'IS', '>', '>=', '<', '<=', 'IN', 'IS NULL', 'LIKE', 'NOT LIKE', 'GLOB']
    if value in opers:
        return True
    return False


# method to remove spaces and parenthesis in a where clause term
def clean_up_term(term):
    removed_space_token = []
    if isinstance(term, sqlparse.sql.Comparison):
        for tok in term.tokens:
            if isinstance(tok, sqlparse.sql.Identifier) or isComparisonOper(tok.value):
                removed_space_token.append(tok)
        return removed_space_token
    if isinstance(term, sqlparse.sql.Parenthesis):
        for tok in term.tokens:
            if isinstance(tok, sqlparse.sql.Comparison):
                removed_space_token.append(clean_up_term(tok))
            elif tok.value == "OR":
                removed_space_token.append([tok])
    final_term = []
    if removed_space_token:
        for items in removed_space_token:
            for item in items:
                final_term.append(item)
    return final_term


def count_tables_row(tables):
    table_count = {}
    for key, value in tables.items():
        sql_query = "SELECT COUNT(*) from {}".format(value)
        cursor.execute(sql_query)
        row_count = cursor.fetchone()[0]
        table_count[value] = row_count

    return table_count


# method to compute cost of a term
def compute_reduction_factor(term):
    if len(term) == 2:
        # reduce number of rows for condition: column = value, column > value, etc
        table = tables[term[0].tokens[0].value]
        column = term[0].tokens[2].value
        oper = term[1].value
        if isIndex(table, column):
            # TODO: find a correct equation for case 'LIKE', 'NOT LIKE, 'IN', 'NOT IN', etc
            if oper == '=' or oper == 'IS' or oper == 'LIKE':
                table_count[table] = int(table_count[table] / indexDict[table][column])
            elif oper == '!=' or oper == 'NOT LIKE':
                table_count[table] = table_count[table] - int(table_count[table] / indexDict[table][column])
            elif oper in ['>', '>=', '<', '<=']:
                # TODO: get high key and low key and compute actual RF
                # will treat as no key for now
                table_count[table] = int(table_count[table] * 0.3)
            else:
                # TODO: find what is in else such as "IS NULL"
                table_count[table] = int(table_count[table] / 10)
        else:
            # TODO: find a correct equation for case 'LIKE', 'NOT LIKE, 'IN', 'NOT IN', etc
            if oper == '=' or oper == 'IS' or oper == 'LIKE':
                table_count[table] = int(table_count[table] / 10)
            elif oper == '!=' or oper == 'NOT LIKE':
                table_count[table] = table_count[table] - int(table_count[table] / 10)
            elif oper in ['>', '>=', '<', '<=']:
                table_count[table] = int(table_count[table] * 0.3)
            else:
                # TODO: find what is in else such as "IS NULL"
                table_count[table] = int(table_count[table] / 10)
    if len(term) == 3:
        # reduce number of rows for condition: column1 = column2, column1 > column2, etc
        lhs_table = tables[term[0].tokens[0].value]
        lhs_column = term[0].tokens[2].value
        oper = term[1].value
        rhs_table = tables[term[2].tokens[0].value]
        rhs_column = term[2].tokens[2].value
        rf = 0.0
        if isIndex(lhs_table, lhs_column) and isIndex(rhs_table, rhs_column):
            max_n_keys = 0
            if indexDict[lhs_table][lhs_column] > indexDict[rhs_table][rhs_column]:
                max_n_keys = indexDict[lhs_table][lhs_column]
            else:
                max_n_keys = indexDict[rhs_table][rhs_column]
            # TODO: find a correct equation for case 'LIKE', 'NOT LIKE, 'IN', 'NOT IN', etc
            if oper == '=' or oper == 'IS' or oper == 'LIKE':
                rf = 1 / max_n_keys
            elif oper == '!=' or oper == 'NOT LIKE':
                rf = 1 - 1 / max_n_keys
            elif oper in ['>', '>=', '<', '<=']:
                # TODO: get high key and low key and compute actual RF
                # will treat as no key for now
                rf = 0.3
            else:
                # TODO: find what is in else such as "IS NULL"
                rf = 0.1
        elif isIndex(lhs_table, lhs_column):
            max_n_keys = indexDict[lhs_table][lhs_column]
            # TODO: find a correct equation for case 'LIKE', 'NOT LIKE, 'IN', 'NOT IN', etc
            if oper == '=' or oper == 'IS' or oper == 'LIKE':
                rf = 1 / max_n_keys
            elif oper == '!=' or oper == 'NOT LIKE':
                rf = 1 - 1 / max_n_keys
            elif oper in ['>', '>=', '<', '<=']:
                # TODO: get high key and low key and compute actual RF
                # will treat as no key for now
                rf = 0.3
            else:
                # TODO: find what is in else such as "IS NULL"
                rf = 0.1
        elif isIndex(rhs_table, rhs_column):
            max_n_keys = indexDict[rhs_table][rhs_column]
            # TODO: find a correct equation for case 'LIKE', 'NOT LIKE, 'IN', 'NOT IN', etc
            if oper == '=' or oper == 'IS' or oper == 'LIKE':
                rf = 1 / max_n_keys
            elif oper == '!=' or oper == 'NOT LIKE':
                rf = 1 - 1 / max_n_keys
            elif oper in ['>', '>=', '<', '<=']:
                # TODO: get high key and low key and compute actual RF
                # will treat as no key for now
                rf = 0.3
            else:
                # TODO: find what is in else such as "IS NULL"
                rf = 0.1
        else:
            # TODO: find a correct equation for case 'LIKE', 'NOT LIKE, 'IN', 'NOT IN', etc
            if oper == '=' or oper == 'IS' or oper == 'LIKE':
                rf = 0.1
            elif oper == '!=' or oper == 'NOT LIKE':
                rf = 0.9
            elif oper in ['>', '>=', '<', '<=']:
                rf = 0.3
            else:
                # TODO: find what is in else such as "IS NULL"
                rf = 0.1
        if rf_tables[table_index[lhs_table]][table_index[rhs_table]] == 1:
            rf_tables[table_index[lhs_table]][table_index[rhs_table]] = rf
            rf_tables[table_index[rhs_table]][table_index[lhs_table]] = rf
        else:
            rf_tables[table_index[lhs_table]][table_index[rhs_table]] = rf *\
                                                                        rf_tables[table_index[lhs_table]][table_index[rhs_table]]
            rf_tables[table_index[rhs_table]][table_index[lhs_table]] = rf *\
                                                                        rf_tables[table_index[rhs_table]][table_index[lhs_table]]

    # TODO: cover more terms format like multiple expressions in one term.
    #  Current methods only cover single expression in a term like column = value or column1 = column2


raw_multi_join_query = sqlparse.format(raw_multi_join_query, reindent=True, keyword_case='upper')
print("Raw query:")
print(raw_multi_join_query)
parsed_query = sqlparse.parse(raw_multi_join_query)[0]
# parsed_query._pprint_tree()

select_clause = []
from_clause = []
where_clause = parsed_query[-1]

for i in range(0, len(parsed_query.tokens)):
    if parsed_query[i].value == "SELECT":
        select_clause = parsed_query[i + 2]
    elif parsed_query[i].value == "FROM":
        from_clause = parsed_query[i + 2]





# get_select_tokens(select_clause)
tables = get_from_tokens(from_clause)

table_count = count_tables_row(tables)
print("Before compute cost:", table_count)
where_terms = get_where_tokens(where_clause)

cleaned_where_terms = []
for term in where_terms:
    if term.value != "AND":
        cleaned_where_terms.append(clean_up_term(term))


n_tables = len(tables)
table_index = dict()
i = 0
for key, value in tables.items():
    table_index[value] = i
    i = i + 1
rf_tables = np.ones((n_tables, n_tables))


for term in cleaned_where_terms:
    compute_reduction_factor(term)

sim.compare_algorithms(table_count, rf_tables)
# Committing the changes
connection.commit()

# closing the database connection
connection.close()
